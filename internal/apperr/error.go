package apperr

import "net/http"

// NewInternalError creates an AppError for unexpected server-side failures.
func NewInternalError(msg ...string) AppError {
	message := "internal server error"
	if len(msg) > 0 {
		message = msg[0]
	}
	return AppError{
		HTTPStatus: http.StatusInternalServerError,
		Code:       CodeInternalError,
		Message:    message,
	}
}

// NewAuthorizationError creates an AppError for requests that require authentication.
func NewAuthorizationError(msg ...string) AppError {
	message := "authorization error"
	if len(msg) > 0 {
		message = msg[0]
	}
	return AppError{
		HTTPStatus: http.StatusUnauthorized,
		Code:       CodeAuthRequired,
		Message:    message,
	}
}

// NewForbiddenError creates an AppError for authenticated requests that lack permission.
func NewForbiddenError(msg ...string) AppError {
	message := "invalid role"
	if len(msg) > 0 {
		message = msg[0]
	}
	return AppError{
		HTTPStatus: http.StatusForbidden,
		Code:       CodeForbidden,
		Message:    message,
	}
}
