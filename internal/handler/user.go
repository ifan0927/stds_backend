package handler

import (
	"context"

	"github.com/ifan0927/stds-backend/internal/api"
	"github.com/ifan0927/stds-backend/internal/auth"
	"github.com/ifan0927/stds-backend/internal/service"
)

// ListUsers handles the list users endpoint defined by the generated strict server interface.
func (s *Server) ListUsers(ctx context.Context, request api.ListUsersRequestObject) (api.ListUsersResponseObject, error) {
	panic("not implemented")
}

// CreateUser handles the create user endpoint defined by the generated strict server interface.
func (s *Server) CreateUser(ctx context.Context, request api.CreateUserRequestObject) (api.CreateUserResponseObject, error) {
	panic("not implemented")
}

// BatchAddUsersToGroup handles the batch add users to group endpoint defined by the generated strict server interface.
func (s *Server) BatchAddUsersToGroup(ctx context.Context, request api.BatchAddUsersToGroupRequestObject) (api.BatchAddUsersToGroupResponseObject, error) {
	panic("not implemented")
}

// BatchRemoveUsersFromGroup handles the batch remove users from group endpoint defined by the generated strict server interface.
func (s *Server) BatchRemoveUsersFromGroup(ctx context.Context, request api.BatchRemoveUsersFromGroupRequestObject) (api.BatchRemoveUsersFromGroupResponseObject, error) {
	panic("not implemented")
}

// BatchUpdateUsersField handles the batch update users field endpoint defined by the generated strict server interface.
func (s *Server) BatchUpdateUsersField(ctx context.Context, request api.BatchUpdateUsersFieldRequestObject) (api.BatchUpdateUsersFieldResponseObject, error) {
	panic("not implemented")
}

// ListAvailableMembers handles the list available members endpoint defined by the generated strict server interface.
func (s *Server) ListAvailableMembers(ctx context.Context, request api.ListAvailableMembersRequestObject) (api.ListAvailableMembersResponseObject, error) {
	panic("not implemented")
}

// BatchCreateUsers handles the batch create users endpoint defined by the generated strict server interface.
func (s *Server) BatchCreateUsers(ctx context.Context, request api.BatchCreateUsersRequestObject) (api.BatchCreateUsersResponseObject, error) {
	panic("not implemented")
}

// CheckUsername handles the username availability endpoint defined by the generated strict server interface.
func (s *Server) CheckUsername(ctx context.Context, request api.CheckUsernameRequestObject) (api.CheckUsernameResponseObject, error) {
	panic("not implemented")
}

// ImportUsers handles the import users endpoint defined by the generated strict server interface.
func (s *Server) ImportUsers(ctx context.Context, request api.ImportUsersRequestObject) (api.ImportUsersResponseObject, error) {
	panic("not implemented")
}

// ChangeMyPassword handles the current user password change endpoint defined by the generated strict server interface.
func (s *Server) ChangeMyPassword(ctx context.Context, request api.ChangeMyPasswordRequestObject) (api.ChangeMyPasswordResponseObject, error) {
	userState, err := auth.UserStateFromContext(ctx)
	if err != nil {
		return nil, err
	}
	input := service.ChangeMyPasswordInput{
		UserID:          userState.UserID,
		CurrentPassword: request.Body.CurrentPassword,
		NewPassword:     request.Body.NewPassword,
	}
	err = s.authService.ChangeMyPassword(ctx, input)
	if err != nil {
		return nil, err
	}
	return api.ChangeMyPassword204Response{}, nil
}

// GetUser handles the get user endpoint defined by the generated strict server interface.
func (s *Server) GetUser(ctx context.Context, request api.GetUserRequestObject) (api.GetUserResponseObject, error) {
	panic("not implemented")
}

// UpdateUser handles the update user endpoint defined by the generated strict server interface.
func (s *Server) UpdateUser(ctx context.Context, request api.UpdateUserRequestObject) (api.UpdateUserResponseObject, error) {
	panic("not implemented")
}
