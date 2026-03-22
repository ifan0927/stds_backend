package handler

import "github.com/ifan0927/stds-backend/internal/service"

// Server implements the generated strict server interface for the HTTP API.
type Server struct {
	authService service.AuthService
}

// NewServer creates a Server instance for route registration.
func NewServer(authService service.AuthService) *Server {
	return &Server{authService: authService}
}
