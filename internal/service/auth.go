package service

import (
	"context"
	"errors"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/ifan0927/stds-backend/internal/apperr"
	"github.com/ifan0927/stds-backend/internal/auth"
	"github.com/ifan0927/stds-backend/internal/config"
	"golang.org/x/crypto/bcrypt"
)

const (
	// minPasswordLength is the minimum accepted length for a new password.
	minPasswordLength = 6
)

var (
	// ErrNotFound marks repository lookups that did not match any row.
	ErrNotFound = errors.New("not found")
)

// AuthRepository defines the persistence methods required by the auth service.
type AuthRepository interface {
	FindByUsername(ctx context.Context, username string) (AuthUser, error)
	UpdateLastLoginAt(ctx context.Context, userID int64, at time.Time) error
	PasswordHashByUserID(ctx context.Context, userID int64) (string, error)
	UpdatePasswordHash(ctx context.Context, userID int64, passwordHash string, at time.Time) error
}

// TokenIssuer signs JWTs for successful login responses.
type TokenIssuer interface {
	IssueToken(claims auth.Claims) (string, error)
}

// AuthService orchestrates auth-related business rules.
type AuthService interface {
	Login(ctx context.Context, input LoginInput) (LoginResult, error)
	Logout(ctx context.Context, input LogoutInput) error
	ChangeMyPassword(ctx context.Context, input ChangeMyPasswordInput) error
}

// AuthUser contains the auth-facing user fields loaded from storage.
type AuthUser struct {
	UserID       int64
	Username     string
	Name         string
	Email        string
	Role         string
	IsEnabled    bool
	PasswordHash string
	Bio          *string
	Occupation   *string
	CreatedAt    time.Time
	LastLoginAt  *time.Time
}

// LoginInput contains the credentials submitted by the caller.
type LoginInput struct {
	Username string
	Password string
}

// LoginResult contains the token and user data returned after login.
type LoginResult struct {
	AccessToken string
	ExpiresAt   time.Time
	User        AuthUser
}

// LogoutInput is kept for symmetry with other auth operations.
type LogoutInput struct{}

// ChangeMyPasswordInput contains the password rotation request for the current user.
type ChangeMyPasswordInput struct {
	UserID          int64
	CurrentPassword string
	NewPassword     string
}

type authService struct {
	repo   AuthRepository
	issuer TokenIssuer
	now    func() time.Time
	cfg    config.Config
}

// JWTIssuer signs auth claims using HS256.
type JWTIssuer struct {
	Secret []byte
}

// IssueToken signs a JWT access token from auth claims.
func (i JWTIssuer) IssueToken(claims auth.Claims) (string, error) {
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(i.Secret)
}

// NewAuthService creates an auth service with concrete dependencies.
func NewAuthService(repo AuthRepository, issuer TokenIssuer, now func() time.Time, cfg config.Config) AuthService {
	if now == nil {
		now = time.Now
	}
	return &authService{
		repo:   repo,
		issuer: issuer,
		now:    now,
		cfg:    cfg,
	}
}

// Login verifies credentials, issues a JWT, and updates lastLoginAt on a best-effort basis.
func (s *authService) Login(ctx context.Context, input LoginInput) (LoginResult, error) {
	user, err := s.repo.FindByUsername(ctx, input.Username)
	if err != nil {
		if errors.Is(err, ErrNotFound) {
			return LoginResult{}, invalidCredentialsError()
		}
		return LoginResult{}, apperr.WrapInternal(err)
	}
	if !user.IsEnabled {
		return LoginResult{}, invalidCredentialsError()
	}
	if bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(input.Password)) != nil {
		return LoginResult{}, invalidCredentialsError()
	}

	issuedAt := s.now().UTC()
	expiresAt := issuedAt.Add(s.cfg.JWTAccessTokenTTL)
	token, err := s.issuer.IssueToken(auth.Claims{
		UserID:   user.UserID,
		Username: user.Username,
		Role:     user.Role,
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   strconv.FormatInt(user.UserID, 10),
			IssuedAt:  jwt.NewNumericDate(issuedAt),
			ExpiresAt: jwt.NewNumericDate(expiresAt),
		},
	})
	if err != nil {
		return LoginResult{}, apperr.WrapInternal(err)
	}

	_ = s.repo.UpdateLastLoginAt(ctx, user.UserID, issuedAt)
	user.LastLoginAt = &issuedAt

	return LoginResult{
		AccessToken: token,
		ExpiresAt:   expiresAt,
		User:        user,
	}, nil
}

// Logout completes successfully because JWT logout is currently stateless.
func (s *authService) Logout(_ context.Context, _ LogoutInput) error {
	return nil
}

// ChangeMyPassword verifies the current password and persists a new bcrypt hash.
func (s *authService) ChangeMyPassword(ctx context.Context, input ChangeMyPasswordInput) error {
	var details []apperr.ErrorDetail
	if strings.TrimSpace(input.CurrentPassword) == "" {
		details = append(details, apperr.ErrorDetail{Field: "currentPassword", Message: "currentPassword is required"})
	}
	if strings.TrimSpace(input.NewPassword) == "" {
		details = append(details, apperr.ErrorDetail{Field: "newPassword", Message: "newPassword is required"})
	} else if len(input.NewPassword) < minPasswordLength {
		details = append(details, apperr.ErrorDetail{Field: "newPassword", Message: "newPassword must be at least 6 characters"})
	}
	if len(details) > 0 {
		return apperr.NewValidationError(details)
	}

	passwordHash, err := s.repo.PasswordHashByUserID(ctx, input.UserID)
	if err != nil {
		return apperr.WrapInternal(err)
	}
	if bcrypt.CompareHashAndPassword([]byte(passwordHash), []byte(input.CurrentPassword)) != nil {
		return apperr.AppError{
			HTTPStatus: http.StatusConflict,
			Code:       apperr.CodeCurrentPasswordIncorrect,
			Message:    "current password is incorrect",
		}
	}

	newHash, err := bcrypt.GenerateFromPassword([]byte(input.NewPassword), bcrypt.DefaultCost)
	if err != nil {
		return apperr.WrapInternal(err)
	}
	if err := s.repo.UpdatePasswordHash(ctx, input.UserID, string(newHash), s.now()); err != nil {
		return apperr.WrapInternal(err)
	}
	return nil
}

func invalidCredentialsError() apperr.AppError {
	return apperr.AppError{
		HTTPStatus: http.StatusUnauthorized,
		Code:       apperr.CodeInvalidCredentials,
		Message:    "帳號或密碼錯誤",
	}
}
