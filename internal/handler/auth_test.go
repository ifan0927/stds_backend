package handler

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/ifan0927/stds-backend/internal/api"
	"github.com/ifan0927/stds-backend/internal/apperr"
	"github.com/ifan0927/stds-backend/internal/service"
)

func TestLogin_Success(t *testing.T) {
	t.Parallel()

	server := newAuthTestServer(authHandlerServiceStub{
		loginFunc: func(ctx context.Context, input service.LoginInput) (service.LoginResult, error) {
			expected := service.LoginInput{
				Username: "alice",
				Password: "secret123",
			}
			if input != expected {
				t.Fatalf("Login() input = %#v, want %#v", input, expected)
			}

			expiresAt := time.Date(2026, 3, 22, 6, 0, 0, 0, time.UTC)
			return service.LoginResult{
				AccessToken: "jwt-token",
				ExpiresAt:   expiresAt,
				User: service.AuthUser{
					UserID:      42,
					Username:    "alice",
					Name:        "Alice",
					Role:        "admin",
					IsEnabled:   true,
					LastLoginAt: &expiresAt,
				},
			}, nil
		},
	})

	response, err := server.Login(context.Background(), api.LoginRequestObject{
		Body: &api.LoginRequest{
			Username: "alice",
			Password: "secret123",
		},
	})

	if err != nil {
		t.Fatalf("Login() error = %v", err)
	}
	loginResponse, ok := response.(api.Login200JSONResponse)
	if !ok {
		t.Fatalf("response type = %T, want api.Login200JSONResponse", response)
	}
	if loginResponse.AccessToken != "jwt-token" {
		t.Fatalf("AccessToken = %q, want %q", loginResponse.AccessToken, "jwt-token")
	}
	if loginResponse.User.UserId != 42 {
		t.Fatalf("UserId = %d, want 42", loginResponse.User.UserId)
	}
	if loginResponse.User.Username != "alice" {
		t.Fatalf("Username = %q, want %q", loginResponse.User.Username, "alice")
	}
}

func TestLogin_ServiceError(t *testing.T) {
	t.Parallel()

	server := newAuthTestServer(authHandlerServiceStub{
		loginFunc: func(ctx context.Context, input service.LoginInput) (service.LoginResult, error) {
			return service.LoginResult{}, apperr.AppError{
				HTTPStatus: 401,
				Code:       apperr.CodeInvalidCredentials,
				Message:    "帳號或密碼錯誤",
			}
		},
	})

	response, err := server.Login(context.Background(), api.LoginRequestObject{
		Body: &api.LoginRequest{
			Username: "alice",
			Password: "wrong-password",
		},
	})

	if response != nil {
		t.Fatalf("response = %#v, want nil", response)
	}
	var appErr apperr.AppError
	if !errors.As(err, &appErr) {
		t.Fatalf("Login() error = %v, want apperr.AppError", err)
	}
	if appErr.Code != apperr.CodeInvalidCredentials {
		t.Fatalf("appErr.Code = %q, want %q", appErr.Code, apperr.CodeInvalidCredentials)
	}
}

func TestLogout_Success(t *testing.T) {
	t.Parallel()

	server := newAuthTestServer(authHandlerServiceStub{
		logoutFunc: func(ctx context.Context, input service.LogoutInput) error {
			return nil
		},
	})

	response, err := server.Logout(context.Background(), api.LogoutRequestObject{})

	if err != nil {
		t.Fatalf("Logout() error = %v", err)
	}
	_, ok := response.(api.Logout204Response)
	if !ok {
		t.Fatalf("response type = %T, want api.Logout204Response", response)
	}
}

type authHandlerService interface {
	Login(ctx context.Context, input service.LoginInput) (service.LoginResult, error)
	Logout(ctx context.Context, input service.LogoutInput) error
	ChangeMyPassword(ctx context.Context, input service.ChangeMyPasswordInput) error
}

type authHandlerServiceStub struct {
	loginFunc            func(ctx context.Context, input service.LoginInput) (service.LoginResult, error)
	logoutFunc           func(ctx context.Context, input service.LogoutInput) error
	changeMyPasswordFunc func(ctx context.Context, input service.ChangeMyPasswordInput) error
}

func (s authHandlerServiceStub) Login(ctx context.Context, input service.LoginInput) (service.LoginResult, error) {
	return s.loginFunc(ctx, input)
}

func (s authHandlerServiceStub) Logout(ctx context.Context, input service.LogoutInput) error {
	return s.logoutFunc(ctx, input)
}

func (s authHandlerServiceStub) ChangeMyPassword(ctx context.Context, input service.ChangeMyPasswordInput) error {
	return s.changeMyPasswordFunc(ctx, input)
}

func newAuthTestServer(authService authHandlerService) *Server {
	return &Server{
		authService: authService,
	}
}
