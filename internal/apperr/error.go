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

// NewValidationError creates an AppError for request validation failures.
func NewValidationError(details []ErrorDetail, msg ...string) AppError {
	message := "validation error"
	if len(msg) > 0 {
		message = msg[0]
	}
	return AppError{
		HTTPStatus: http.StatusBadRequest,
		Code:       CodeValidationError,
		Message:    message,
		Details:    details,
	}
}

// NewTokenExpiredError creates an AppError for expired access tokens.
func NewTokenExpiredError(msg ...string) AppError {
	message := "authorization error: access token expired"
	if len(msg) > 0 {
		message = msg[0]
	}
	return AppError{
		HTTPStatus: http.StatusUnauthorized,
		Code:       CodeTokenExpired,
		Message:    message,
	}
}

// WrapInternal converts an unexpected error into an internal AppError while preserving the cause.
func WrapInternal(cause error) AppError {
	return AppError{
		HTTPStatus: http.StatusInternalServerError,
		Code:       CodeInternalError,
		Message:    "internal server error",
		Err:        cause, // 關鍵
	}
}
