package service

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/ifan0927/stds-backend/internal/apperr"
	claimsauth "github.com/ifan0927/stds-backend/internal/auth"
	"github.com/ifan0927/stds-backend/internal/config"
	"golang.org/x/crypto/bcrypt"
)

func TestAuthService_Login(t *testing.T) {
	t.Parallel()

	now := time.Date(2026, 3, 21, 12, 0, 0, 0, time.UTC)
	passwordHash := mustHashPassword(t, "secret123")

	tests := []struct {
		name           string
		repo           *authRepositoryStub
		input          LoginInput
		expectedCode   string
		expectedStatus int
		assertResult   func(t *testing.T, result LoginResult)
	}{
		{
			name: "success",
			repo: &authRepositoryStub{
				findByUsernameFunc: func(ctx context.Context, username string) (AuthUser, error) {
					return AuthUser{
						UserID:       42,
						Username:     "alice",
						Name:         "Alice",
						Email:        "alice@example.com",
						Role:         "admin",
						IsEnabled:    true,
						PasswordHash: passwordHash,
					}, nil
				},
				updateLastLoginAtFunc: func(ctx context.Context, userID int64, at time.Time) error {
					if userID != 42 {
						t.Fatalf("UpdateLastLoginAt() userID = %d, want 42", userID)
					}
					if !at.Equal(now) {
						t.Fatalf("UpdateLastLoginAt() at = %v, want %v", at, now)
					}
					return nil
				},
			},
			input: LoginInput{
				Username: "alice",
				Password: "secret123",
			},
			assertResult: func(t *testing.T, result LoginResult) {
				t.Helper()
				if result.User.Username != "alice" {
					t.Fatalf("result.User.Username = %q, want %q", result.User.Username, "alice")
				}
				if !result.ExpiresAt.Equal(now.Add(18 * time.Hour)) {
					t.Fatalf("result.ExpiresAt = %v, want %v", result.ExpiresAt, now.Add(18*time.Hour))
				}

				parser := jwt.NewParser(jwt.WithTimeFunc(func() time.Time { return now }))
				parsed, err := parser.ParseWithClaims(result.AccessToken, &claimsauth.Claims{}, func(token *jwt.Token) (interface{},
					error) {
					return []byte("jwt-secret"), nil
				})
				if err != nil {
					t.Fatalf("ParseWithClaims() error = %v", err)
				}
				if !parsed.Valid {
					t.Fatal("parsed token is invalid")
				}

				claims, ok := parsed.Claims.(*claimsauth.Claims)
				if !ok {
					t.Fatalf("claims type = %T, want *auth.Claims", parsed.Claims)
				}
				if claims.UserID != 42 {
					t.Fatalf("claims.UserID = %d, want 42", claims.UserID)
				}
				if claims.Username != "alice" {
					t.Fatalf("claims.Username = %q, want %q", claims.Username, "alice")
				}
				if claims.Role != "admin" {
					t.Fatalf("claims.Role = %q, want %q", claims.Role, "admin")
				}
				if claims.Subject != "42" {
					t.Fatalf("claims.Subject = %q, want %q", claims.Subject, "42")
				}
				if claims.IssuedAt == nil || !claims.IssuedAt.Time.Equal(now) {
					t.Fatalf("claims.IssuedAt = %v, want %v", claims.IssuedAt, now)
				}
				if claims.ExpiresAt == nil || !claims.ExpiresAt.Time.Equal(now.Add(18*time.Hour)) {
					t.Fatalf("claims.ExpiresAt = %v, want %v", claims.ExpiresAt, now.Add(18*time.Hour))
				}
			},
		},
		{
			name: "username not found returns invalid credentials",
			repo: &authRepositoryStub{
				findByUsernameFunc: func(ctx context.Context, username string) (AuthUser, error) {
					return AuthUser{}, ErrNotFound
				},
			},
			input: LoginInput{
				Username: "missing",
				Password: "secret123",
			},
			expectedCode:   apperr.CodeInvalidCredentials,
			expectedStatus: 401,
		},
		{
			name: "disabled user returns invalid credentials",
			repo: &authRepositoryStub{
				findByUsernameFunc: func(ctx context.Context, username string) (AuthUser, error) {
					return AuthUser{
						UserID:       42,
						Username:     "alice",
						IsEnabled:    false,
						PasswordHash: passwordHash,
					}, nil
				},
			},
			input: LoginInput{
				Username: "alice",
				Password: "secret123",
			},
			expectedCode:   apperr.CodeInvalidCredentials,
			expectedStatus: 401,
		},
		{
			name: "wrong password returns invalid credentials",
			repo: &authRepositoryStub{
				findByUsernameFunc: func(ctx context.Context, username string) (AuthUser, error) {
					return AuthUser{
						UserID:       42,
						Username:     "alice",
						IsEnabled:    true,
						PasswordHash: passwordHash,
					}, nil
				},
			},
			input: LoginInput{
				Username: "alice",
				Password: "bad-password",
			},
			expectedCode:   apperr.CodeInvalidCredentials,
			expectedStatus: 401,
		},
	}

	for _, tt := range tests {
		tt := tt
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			cfg := config.Config{
				JWTAccessTokenTTL: 18 * time.Hour,
			}
			svc := NewAuthService(tt.repo, JWTIssuer{Secret: []byte("jwt-secret")}, func() time.Time { return now }, cfg)
			result, err := svc.Login(context.Background(), tt.input)

			if tt.assertResult != nil {
				if err != nil {
					t.Fatalf("Login() error = %v", err)
				}
				tt.assertResult(t, result)
				return
			}

			var appErr apperr.AppError
			if !errors.As(err, &appErr) {
				t.Fatalf("Login() error = %v, want apperr.AppError", err)
			}
			if appErr.Code != tt.expectedCode {
				t.Fatalf("appErr.Code = %q, want %q", appErr.Code, tt.expectedCode)
			}
			if appErr.HTTPStatus != tt.expectedStatus {
				t.Fatalf("appErr.HTTPStatus = %d, want %d", appErr.HTTPStatus, tt.expectedStatus)
			}
		})
	}
}

func TestAuthService_ChangeMyPassword(t *testing.T) {
	t.Parallel()

	currentHash := mustHashPassword(t, "old-password")

	tests := []struct {
		name           string
		repo           *authRepositoryStub
		input          ChangeMyPasswordInput
		expectedCode   string
		expectedStatus int
		assertNoError  bool
	}{
		{
			name: "success",
			repo: &authRepositoryStub{
				getPasswordHashByUserIDFunc: func(ctx context.Context, userID int64) (string, error) {
					if userID != 7 {
						t.Fatalf("PasswordHashByUserID() userID = %d, want 7", userID)
					}
					return currentHash, nil
				},
				updatePasswordHashFunc: func(ctx context.Context, userID int64, passwordHash string) error {
					if userID != 7 {
						t.Fatalf("UpdatePasswordHash() userID = %d, want 7", userID)
					}
					if passwordHash == currentHash {
						t.Fatal("UpdatePasswordHash() received unchanged hash")
					}
					return bcrypt.CompareHashAndPassword([]byte(passwordHash), []byte("new-secret"))
				},
			},
			input: ChangeMyPasswordInput{
				UserID:          7,
				CurrentPassword: "old-password",
				NewPassword:     "new-secret",
			},
			assertNoError: true,
		},
		{
			name: "validation error when current password missing",
			repo: &authRepositoryStub{},
			input: ChangeMyPasswordInput{
				UserID:          7,
				CurrentPassword: "",
				NewPassword:     "new-secret",
			},
			expectedCode:   apperr.CodeValidationError,
			expectedStatus: 400,
		},
		{
			name: "validation error when new password too short",
			repo: &authRepositoryStub{},
			input: ChangeMyPasswordInput{
				UserID:          7,
				CurrentPassword: "old-password",
				NewPassword:     "123",
			},
			expectedCode:   apperr.CodeValidationError,
			expectedStatus: 400,
		},
		{
			name: "current password incorrect returns conflict",
			repo: &authRepositoryStub{
				getPasswordHashByUserIDFunc: func(ctx context.Context, userID int64) (string, error) {
					return currentHash, nil
				},
			},
			input: ChangeMyPasswordInput{
				UserID:          7,
				CurrentPassword: "wrong-password",
				NewPassword:     "new-secret",
			},
			expectedCode:   apperr.CodeCurrentPasswordIncorrect,
			expectedStatus: 409,
		},
	}

	for _, tt := range tests {
		tt := tt
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			cfg := config.Config{
				JWTAccessTokenTTL: 18 * time.Hour,
			}
			svc := NewAuthService(tt.repo, JWTIssuer{Secret: []byte("jwt-secret")}, time.Now, cfg)
			err := svc.ChangeMyPassword(context.Background(), tt.input)

			if tt.assertNoError {
				if err != nil {
					t.Fatalf("ChangeMyPassword() error = %v", err)
				}
				return
			}

			var appErr apperr.AppError
			if !errors.As(err, &appErr) {
				t.Fatalf("ChangeMyPassword() error = %v, want apperr.AppError", err)
			}
			if appErr.Code != tt.expectedCode {
				t.Fatalf("appErr.Code = %q, want %q", appErr.Code, tt.expectedCode)
			}
			if appErr.HTTPStatus != tt.expectedStatus {
				t.Fatalf("appErr.HTTPStatus = %d, want %d", appErr.HTTPStatus, tt.expectedStatus)
			}
		})
	}
}

type authRepositoryStub struct {
	findByUsernameFunc          func(ctx context.Context, username string) (AuthUser, error)
	updateLastLoginAtFunc       func(ctx context.Context, userID int64, at time.Time) error
	getPasswordHashByUserIDFunc func(ctx context.Context, userID int64) (string, error)
	updatePasswordHashFunc      func(ctx context.Context, userID int64, passwordHash string) error
}

func (s *authRepositoryStub) FindByUsername(ctx context.Context, username string) (AuthUser, error) {
	if s.findByUsernameFunc == nil {
		return AuthUser{}, errors.New("unexpected FindByUsername call")
	}
	return s.findByUsernameFunc(ctx, username)
}

func (s *authRepositoryStub) UpdateLastLoginAt(ctx context.Context, userID int64, at time.Time) error {
	if s.updateLastLoginAtFunc == nil {
		return nil
	}
	return s.updateLastLoginAtFunc(ctx, userID, at)
}

func (s *authRepositoryStub) PasswordHashByUserID(ctx context.Context, userID int64) (string, error) {
	if s.getPasswordHashByUserIDFunc == nil {
		return "", errors.New("unexpected PasswordHashByUserID call")
	}
	return s.getPasswordHashByUserIDFunc(ctx, userID)
}

func (s *authRepositoryStub) UpdatePasswordHash(ctx context.Context, userID int64, passwordHash string, at time.Time) error {
	if s.updatePasswordHashFunc == nil {
		return errors.New("unexpected UpdatePasswordHash call")
	}
	return s.updatePasswordHashFunc(ctx, userID, passwordHash)
}

func mustHashPassword(t *testing.T, password string) string {
	t.Helper()

	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		t.Fatalf("GenerateFromPassword() error = %v", err)
	}
	return string(hash)
}
