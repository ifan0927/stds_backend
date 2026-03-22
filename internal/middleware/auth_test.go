package middleware

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"github.com/ifan0927/stds-backend/internal/auth"
	"github.com/ifan0927/stds-backend/internal/config"
)

func TestAuthMiddleware(t *testing.T) {
	t.Parallel()

	gin.SetMode(gin.TestMode)

	now := time.Date(2026, 3, 21, 12, 0, 0, 0, time.UTC)
	cfg := config.Config{
		JWTSecret: "jwt-secret",
	}

	tests := []struct {
		name           string
		path           string
		token          string
		loader         authStateLoaderStub
		expectedStatus int
		expectedCode   string
		expectContext  bool
	}{
		{
			name:           "public path bypasses auth",
			path:           "/v1/auth/login",
			expectedStatus: http.StatusOK,
		},
		{
			name:           "missing token returns unauthorized",
			path:           "/v1/auth/logout",
			expectedStatus: http.StatusUnauthorized,
			expectedCode:   "AUTH_REQUIRED",
		},
		{
			name:           "expired token returns token expired",
			path:           "/v1/auth/logout",
			token:          signedToken(t, cfg.JWTSecret, 42, "42", now.Add(-2*time.Hour), now.Add(-1*time.Hour)),
			expectedStatus: http.StatusUnauthorized,
			expectedCode:   "TOKEN_EXPIRED",
		},
		{
			name:           "subject and user id mismatch returns unauthorized",
			path:           "/v1/auth/logout",
			token:          signedToken(t, cfg.JWTSecret, 42, "7", now, now.Add(time.Hour)),
			expectedStatus: http.StatusUnauthorized,
			expectedCode:   "AUTH_REQUIRED",
		},
		{
			name:  "disabled user returns unauthorized",
			path:  "/v1/auth/logout",
			token: signedToken(t, cfg.JWTSecret, 42, "42", now, now.Add(time.Hour)),
			loader: authStateLoaderStub{
				loadFunc: func(ctx context.Context, userID int64) (auth.UserState, error) {
					return auth.UserState{UserID: 42, IsEnabled: false}, nil
				},
			},
			expectedStatus: http.StatusUnauthorized,
			expectedCode:   "AUTH_REQUIRED",
		},
		{
			name:  "password changed after token issue returns unauthorized",
			path:  "/v1/auth/logout",
			token: signedToken(t, cfg.JWTSecret, 42, "42", now, now.Add(time.Hour)),
			loader: authStateLoaderStub{
				loadFunc: func(ctx context.Context, userID int64) (auth.UserState, error) {
					changedAt := now
					return auth.UserState{
						UserID:            42,
						IsEnabled:         true,
						PasswordChangedAt: &changedAt,
					}, nil
				},
			},
			expectedStatus: http.StatusUnauthorized,
			expectedCode:   "TOKEN_EXPIRED",
		},
		{
			name:  "valid token stores claims and current user",
			path:  "/v1/auth/logout",
			token: signedToken(t, cfg.JWTSecret, 42, "42", now.Add(time.Minute), now.Add(time.Hour)),
			loader: authStateLoaderStub{
				loadFunc: func(ctx context.Context, userID int64) (auth.UserState, error) {
					return auth.UserState{UserID: 42, IsEnabled: true}, nil
				},
			},
			expectedStatus: http.StatusOK,
			expectContext:  true,
		},
	}

	for _, tt := range tests {
		tt := tt
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()

			router := gin.New()
			router.Use(authMiddleware(cfg, tt.loader, func() time.Time { return now }))
			router.GET("/*path", func(c *gin.Context) {
				_, claimsErr := auth.ClaimsFromContext(c.Request.Context())
				_, currentUserErr := auth.UserStateFromContext(c.Request.Context())
				c.JSON(http.StatusOK, gin.H{
					"claimsFound":      claimsErr == nil,
					"currentUserFound": currentUserErr == nil,
				})
			})

			request := httptest.NewRequest(http.MethodGet, tt.path, nil)
			if tt.token != "" {
				request.Header.Set("Authorization", "Bearer "+tt.token)
			}
			recorder := httptest.NewRecorder()

			router.ServeHTTP(recorder, request)

			if recorder.Code != tt.expectedStatus {
				t.Fatalf("status = %d, want %d", recorder.Code, tt.expectedStatus)
			}
			if tt.expectedCode == "" {
				if tt.expectContext {
					var body map[string]bool
					err := json.Unmarshal(recorder.Body.Bytes(), &body)
					if err != nil {
						t.Fatalf("Unmarshal() error = %v", err)
					}
					if !body["claimsFound"] {
						t.Fatal("claimsFound = false, want true")
					}
					if !body["currentUserFound"] {
						t.Fatal("currentUserFound = false, want true")
					}
				}
				return
			}

			var body map[string]any
			err := json.Unmarshal(recorder.Body.Bytes(), &body)
			if err != nil {
				t.Fatalf("Unmarshal() error = %v", err)
			}
			if body["code"] != tt.expectedCode {
				t.Fatalf("body[code] = %v, want %q", body["code"], tt.expectedCode)
			}
		})
	}
}

type authStateLoaderStub struct {
	loadFunc func(ctx context.Context, userID int64) (auth.UserState, error)
}

func (s authStateLoaderStub) Load(ctx context.Context, userID int64) (auth.UserState, error) {
	if s.loadFunc == nil {
		return auth.UserState{}, nil
	}
	return s.loadFunc(ctx, userID)
}

func signedToken(t *testing.T, secret string, userID int64, subject string, issuedAt, expiresAt time.Time) string {
	t.Helper()

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, auth.Claims{
		UserID:    userID,
		Username:  "alice",
		Role:      "admin",
		EstateIDs: []int64{1001},
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   subject,
			IssuedAt:  jwt.NewNumericDate(issuedAt),
			ExpiresAt: jwt.NewNumericDate(expiresAt),
		},
	})

	signed, err := token.SignedString([]byte(secret))
	if err != nil {
		t.Fatalf("SignedString() error = %v", err)
	}
	return signed
}
