package apperr

// ErrorDetail describes a field-level validation error returned to API clients.
type ErrorDetail struct {
	Field   string `json:"field"`
	Message string `json:"message"`
}

// AppError represents a structured application error exposed through the API layer.
type AppError struct {
	HTTPStatus int           `json:"-"`
	Code       string        `json:"code"`
	Message    string        `json:"message"`
	Details    []ErrorDetail `json:"details,omitempty"`
	Err        error         `json:"-"`
}

// Error returns the public error message for AppError.
func (e AppError) Error() string {
	return e.Message
}

// Unwrap returns the underlying internal error carried by AppError.
func (e AppError) Unwrap() error {
	return e.Err
}
