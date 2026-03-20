package apperr

type ErrorDetail struct {
	Field   string `json:"field"`
	Message string `json:"message"`
}

type AppError struct {
	HTTPStatus int           `json:"-"`
	Code       string        `json:"code"`
	Message    string        `json:"message"`
	Details    []ErrorDetail `json:"details,omitempty"`
	Err        error         `json:"-"`
}

func (e AppError) Error() string {
	return e.Message
}
