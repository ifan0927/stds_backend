package handler

import (
	"context"

	"github.com/ifan0927/stds-backend/internal/api"
	"github.com/ifan0927/stds-backend/internal/service"
	openapi_types "github.com/oapi-codegen/runtime/types"
)

// Login handles the login endpoint defined by the generated strict server interface.
func (s *Server) Login(ctx context.Context, request api.LoginRequestObject) (api.LoginResponseObject, error) {
	loginInput := service.LoginInput{
		Username: request.Body.Username,
		Password: request.Body.Password,
	}
	loginResult, err := s.authService.Login(ctx, loginInput)
	if err != nil {
		return nil, err
	}
	email := openapi_types.Email(loginResult.User.Email)
	userDetail := api.UserDetail{
		Bio:         loginResult.User.Bio,
		CreatedAt:   &loginResult.User.CreatedAt,
		Email:       &email,
		Groups:      nil,
		IsEnabled:   loginResult.User.IsEnabled,
		LastLoginAt: loginResult.User.LastLoginAt,
		Name:       &loginResult.User.Name,
		Occupation: loginResult.User.Occupation,
		Role:       api.UserDetailRole(loginResult.User.Role),
		UserId:     int(loginResult.User.UserID),
		Username:   loginResult.User.Username,
	}
	return api.Login200JSONResponse{
		AccessToken: loginResult.AccessToken,
		ExpiresAt:   loginResult.ExpiresAt,
		User:        userDetail,
	}, nil

}

// Logout handles the logout endpoint defined by the generated strict server interface.
func (s *Server) Logout(ctx context.Context, request api.LogoutRequestObject) (api.LogoutResponseObject, error) {
	err := s.authService.Logout(ctx, service.LogoutInput{})
	if err != nil {
		return nil, err
	}
	return api.Logout204Response{}, nil
}
