package middleware

import (
	"log/slog"
	"net/http"

	"github.com/gin-gonic/gin"

	"github.com/ifan0927/stds-backend/internal/api"
	"github.com/ifan0927/stds-backend/internal/apperr"
)

// ErrorHandler 將 handler 寫入 gin context 的錯誤轉成 OpenAPI 錯誤回應格式。
func ErrorHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Next()

		if len(c.Errors) == 0 {
			return
		}

		requestID, ok := c.Get(requestIDContextKey)
		if !ok {
			requestID = "unknown"
		}
		err := c.Errors.Last().Err

		appErr, ok := err.(*apperr.AppError)
		if !ok {
			slog.Error("request error",
				"request_id", requestID,
				"error", err,
			)
			c.JSON(http.StatusInternalServerError, api.ErrorResponse{
				Code:    apperr.InternalError,
				Message: "伺服器內部錯誤",
			})
			return
		}

		if appErr.Err != nil {
			slog.Error("request error",
				"request_id", requestID,
				"code", appErr.Code,
				"error", appErr.Err,
			)
		}

		response := api.ErrorResponse{
			Code:    appErr.Code,
			Message: appErr.Message,
		}
		if len(appErr.Details) > 0 {
			response.Details = newErrorResponseDetails(appErr.Details)
		}

		c.JSON(appErr.HTTPStatus, response)
	}
}

// OpenAPIErrorHandler 處理 generated wrapper 在 parse/bind request 時產生的錯誤。
//
// 這條路徑發生在 request 進入真正 handler 前，因此不會經過 handler 主動寫入的 AppError。
// 目前先統一轉成 OpenAPI ErrorResponse，避免落回 codegen 預設的 {"msg": "..."} 格式。
func OpenAPIErrorHandler(c *gin.Context, err error, statusCode int) {
	requestID, ok := c.Get(requestIDContextKey)
	if !ok {
		requestID = "unknown"
	}

	if statusCode == http.StatusBadRequest {
		slog.Warn("request bind error",
			"request_id", requestID,
			"error", err,
		)
		c.JSON(statusCode, api.ErrorResponse{
			Code:    apperr.ValidationError,
			Message: "欄位驗證失敗",
			Details: newErrorResponseDetails([]apperr.ErrorDetail{{
				Field:   "request",
				Message: "request 格式錯誤，請確認 Content-Type 及欄位型別",
			}}),
		})
		return
	}

	slog.Error("openapi route error",
		"request_id", requestID,
		"status", statusCode,
		"error", err,
	)
	c.JSON(statusCode, api.ErrorResponse{
		Code:    apperr.InternalError,
		Message: "request 處理失敗",
	})
}

func newErrorResponseDetails(details []apperr.ErrorDetail) *[]struct {
	Field   string `json:"field"`
	Message string `json:"message"`
} {
	responseDetails := make([]struct {
		Field   string `json:"field"`
		Message string `json:"message"`
	}, len(details))

	for i, d := range details {
		responseDetails[i] = struct {
			Field   string `json:"field"`
			Message string `json:"message"`
		}{
			Field:   d.Field,
			Message: d.Message,
		}
	}

	return &responseDetails
}
