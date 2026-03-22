package handler

import (
	"context"

	"github.com/ifan0927/stds-backend/internal/api"
	"github.com/ifan0927/stds-backend/internal/auth"
	"github.com/ifan0927/stds-backend/internal/service"
)

func (s *Server) ListUsers(ctx context.Context, request api.ListUsersRequestObject) (api.ListUsersResponseObject, error) {
	panic("not implemented")
}

func (s *Server) CreateUser(ctx context.Context, request api.CreateUserRequestObject) (api.CreateUserResponseObject, error) {
	panic("not implemented")
}

func (s *Server) BatchAddUsersToGroup(ctx context.Context, request api.BatchAddUsersToGroupRequestObject) (api.BatchAddUsersToGroupResponseObject, error) {
	panic("not implemented")
}

func (s *Server) BatchRemoveUsersFromGroup(ctx context.Context, request api.BatchRemoveUsersFromGroupRequestObject) (api.BatchRemoveUsersFromGroupResponseObject, error) {
	panic("not implemented")
}

func (s *Server) BatchUpdateUsersField(ctx context.Context, request api.BatchUpdateUsersFieldRequestObject) (api.BatchUpdateUsersFieldResponseObject, error) {
	panic("not implemented")
}

func (s *Server) ListAvailableMembers(ctx context.Context, request api.ListAvailableMembersRequestObject) (api.ListAvailableMembersResponseObject, error) {
	panic("not implemented")
}

func (s *Server) BatchCreateUsers(ctx context.Context, request api.BatchCreateUsersRequestObject) (api.BatchCreateUsersResponseObject, error) {
	panic("not implemented")
}

func (s *Server) CheckUsername(ctx context.Context, request api.CheckUsernameRequestObject) (api.CheckUsernameResponseObject, error) {
	panic("not implemented")
}

func (s *Server) ImportUsers(ctx context.Context, request api.ImportUsersRequestObject) (api.ImportUsersResponseObject, error) {
	panic("not implemented")
}

func (s *Server) ChangeMyPassword(ctx context.Context, request api.ChangeMyPasswordRequestObject) (api.ChangeMyPasswordResponseObject, error) {
	userState, err := auth.GetCurrentUserState(ctx)
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

func (s *Server) GetUser(ctx context.Context, request api.GetUserRequestObject) (api.GetUserResponseObject, error) {
	panic("not implemented")
}

func (s *Server) UpdateUser(ctx context.Context, request api.UpdateUserRequestObject) (api.UpdateUserResponseObject, error) {
	panic("not implemented")
}
