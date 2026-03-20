package middleware

import (
	"errors"

	"github.com/gin-gonic/gin"
	"github.com/ifan0927/stds-backend/internal/apperr"
)

// ErrorHandler converts Gin context errors into a unified AppError JSON response.
func ErrorHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Next()
		if c.Errors != nil {
			ginErr := c.Errors.Last()
			var appErr apperr.AppError
			ok := errors.As(ginErr.Err, &appErr)
			if !ok {
				appErr = apperr.NewInternalError()
			}
			c.JSON(appErr.HTTPStatus, appErr)
		}
	}
}
