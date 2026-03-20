package middleware

import (
	"fmt"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"github.com/ifan0927/stds-backend/internal/apperr"
	"github.com/ifan0927/stds-backend/internal/auth"
	"github.com/ifan0927/stds-backend/internal/config"
)

// AuthMiddleware validates bearer JWTs for protected routes and stores parsed claims in the Gin context.
func AuthMiddleware(cfg config.Config) gin.HandlerFunc {
	publicPaths := []string{"/v1/auth/login", "/healthz"}
	return func(c *gin.Context) {
		if isPublicPath(c.Request.URL.Path, publicPaths) {
			c.Next()
			return
		}

		var appErr apperr.AppError
		header := c.Request.Header.Get("Authorization")
		scheme, bearerToken, found := strings.Cut(header, " ")
		if !found || scheme != "Bearer" || bearerToken == "" {
			appErr = apperr.NewAuthorizationError()
			c.AbortWithStatusJSON(appErr.HTTPStatus, appErr)
			return
		}
		secret := []byte(cfg.JWTSecret)
		token, err := jwt.ParseWithClaims(
			bearerToken,
			&auth.Claims{},
			func(token *jwt.Token) (interface{}, error) {
				if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
					return nil, fmt.Errorf("authorization error: unexpected signing method")
				}
				return secret, nil
			})
		if err != nil {
			appErr = apperr.NewAuthorizationError("authorization error: error parsing token")
			c.AbortWithStatusJSON(appErr.HTTPStatus, appErr)
			return
		}
		if !token.Valid {
			appErr = apperr.NewAuthorizationError("authorization error: invalid token")
			c.AbortWithStatusJSON(appErr.HTTPStatus, appErr)
			return
		}
		claims, ok := token.Claims.(*auth.Claims)
		if !ok {
			appErr = apperr.NewAuthorizationError("authorization error: invalid claims")
			c.AbortWithStatusJSON(appErr.HTTPStatus, appErr)
			return
		}
		c.Set("claims", claims)
		c.Next()
	}
}

// isPublicPath reports whether the request path is excluded from JWT authentication.
func isPublicPath(path string, publicPaths []string) bool {
	for _, p := range publicPaths {
		if p == path {
			return true
		}
	}
	return false
}
