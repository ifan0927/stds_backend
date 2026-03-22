package handler

import (
	"context"
	"testing"

	"github.com/ifan0927/stds-backend/internal/api"
	"github.com/ifan0927/stds-backend/internal/apperr"
	"github.com/ifan0927/stds-backend/internal/auth"
	"github.com/ifan0927/stds-backend/internal/service"
)

func TestChangeMyPassword_Success(t *testing.T) {
	t.Parallel()

	ctx := context.WithValue(context.Background(), auth.UserKey, &auth.UserState{
		UserID:    42,
		IsEnabled: true,
	})
	server := newAuthTestServer(authHandlerServiceStub{
		changeMyPasswordFunc: func(ctx context.Context, input service.ChangeMyPasswordInput) error {
			expected := service.ChangeMyPasswordInput{
				UserID:          42,
				CurrentPassword: "old-password",
				NewPassword:     "new-password",
			}
			if input != expected {
				t.Fatalf("ChangeMyPassword() input = %#v, want %#v", input, expected)
			}
			return nil
		},
	})

	response, err := server.ChangeMyPassword(ctx, api.ChangeMyPasswordRequestObject{
		Body: &api.ChangePasswordRequest{
			CurrentPassword: "old-password",
			NewPassword:     "new-password",
		},
	})

	if err != nil {
		t.Fatalf("ChangeMyPassword() error = %v", err)
	}
	_, ok := response.(api.ChangeMyPassword204Response)
	if !ok {
		t.Fatalf("response type = %T, want api.ChangeMyPassword204Response", response)
	}
}

func TestChangeMyPassword_ServiceError(t *testing.T) {
	t.Parallel()

	ctx := context.WithValue(context.Background(), auth.UserKey, &auth.UserState{
		UserID:    42,
		IsEnabled: true,
	})
	server := newAuthTestServer(authHandlerServiceStub{
		changeMyPasswordFunc: func(ctx context.Context, input service.ChangeMyPasswordInput) error {
			return apperr.AppError{
				HTTPStatus: 409,
				Code:       apperr.CodeCurrentPasswordIncorrect,
				Message:    "current password is incorrect",
			}
		},
	})

	response, err := server.ChangeMyPassword(ctx, api.ChangeMyPasswordRequestObject{
		Body: &api.ChangePasswordRequest{
			CurrentPassword: "wrong-password",
			NewPassword:     "new-password",
		},
	})

	if response != nil {
		t.Fatalf("response = %#v, want nil", response)
	}
	var appErr apperr.AppError
	if !errorAs(err, &appErr) {
		t.Fatalf("ChangeMyPassword() error = %v, want apperr.AppError", err)
	}
	if appErr.Code != apperr.CodeCurrentPasswordIncorrect {
		t.Fatalf("appErr.Code = %q, want %q", appErr.Code, apperr.CodeCurrentPasswordIncorrect)
	}
}
