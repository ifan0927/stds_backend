package middleware

import (
	"log/slog"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// Logger returns a Gin middleware that assigns a request ID and logs request metadata.
func Logger() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()

		requestID := c.Request.Header.Get("X-Request-Id")
		if requestID == "" {
			requestID = uuid.New().String()
		}
		c.Header("X-Request-Id", requestID)
		c.Set("request_id", requestID)

		c.Next()

		latency := time.Since(start).Milliseconds()
		statusCode := c.Writer.Status()
		method := c.Request.Method
		path := c.FullPath()
		ip := c.ClientIP()
		trace := c.Request.Header.Get("X-Cloud-Trace-Context")

		slog.Info("request",
			"method", method,
			"requestID", requestID,
			"path", path,
			"status", statusCode,
			"latency_ms", latency,
			"client_ip", ip,
			"trace", trace,
		)
	}
}
