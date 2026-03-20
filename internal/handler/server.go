package handler

// Server implements the generated strict server interface for the HTTP API.
type Server struct {
}

// NewServer creates a Server instance for route registration.
func NewServer() *Server {
	return &Server{}
}
