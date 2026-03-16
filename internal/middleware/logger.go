package middleware

import (
	"log/slog"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

const requestIDContextKey = "request_id"

// Logger 為每個 HTTP request 輸出一筆 structured slog 紀錄。
func Logger() gin.HandlerFunc {
	return func(c *gin.Context) {
		requestID := c.GetHeader("X-Request-Id")
		if requestID == "" {
			requestID = uuid.NewString()
		}

		c.Set(requestIDContextKey, requestID)
		c.Header("X-Request-Id", requestID)

		start := time.Now()
		c.Next()

		path := c.FullPath()
		if path == "" {
			path = c.Request.URL.Path
		}

		slog.Info("request completed",
			"request_id", requestID,
			"method", c.Request.Method,
			"path", path,
			"status", c.Writer.Status(),
			"latency_ms", time.Since(start).Milliseconds(),
			"client_ip", c.ClientIP(),
			"trace", c.GetHeader("X-Cloud-Trace-Context"),
		)
	}
}
