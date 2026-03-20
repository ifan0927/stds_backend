package handler

import (
	"context"

	"github.com/ifan0927/stds-backend/internal/api"
)

// Login handles the login endpoint defined by the generated strict server interface.
func (s *Server) Login(ctx context.Context, request api.LoginRequestObject) (api.LoginResponseObject, error) {
	panic("not implemented")
}

// Logout handles the logout endpoint defined by the generated strict server interface.
func (s *Server) Logout(ctx context.Context, request api.LogoutRequestObject) (api.LogoutResponseObject, error) {
	panic("not implemented")
}
