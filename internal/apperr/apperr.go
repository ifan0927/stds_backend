package apperr

import (
	"fmt"
	"net/http"
)

// AppError 表示對外 API 錯誤資訊，以及僅供內部 logging 使用的原始錯誤。
type AppError struct {
	HTTPStatus int
	Code       string
	Message    string
	Details    []ErrorDetail
	Err        error
}

// ErrorDetail 表示單一欄位的驗證錯誤明細。
type ErrorDetail struct {
	Field   string
	Message string
}

// New 建立不包含原始錯誤的 AppError。
func New(httpStatus int, code string, message string) *AppError {
	return &AppError{
		HTTPStatus: httpStatus,
		Code:       code,
		Message:    message,
	}
}

// NewValidation 建立帶有標準 validation code 與訊息的 AppError。
func NewValidation(details []ErrorDetail) *AppError {
	return &AppError{
		HTTPStatus: http.StatusBadRequest,
		Code:       ValidationError,
		Message:    "欄位驗證失敗",
		Details:    details,
	}
}

// Wrap 建立保留原始錯誤的 AppError，供內部 logging 使用。
func Wrap(httpStatus int, code string, message string, err error) *AppError {
	return &AppError{
		HTTPStatus: httpStatus,
		Code:       code,
		Message:    message,
		Err:        err,
	}
}

// Error 實作 error 介面。
func (e *AppError) Error() string {
	if e == nil {
		return "<nil>"
	}
	if e.Err != nil {
		return fmt.Sprintf("%s: %v", e.Message, e.Err)
	}
	return e.Message
}
