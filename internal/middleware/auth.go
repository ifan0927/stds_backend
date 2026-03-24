package middleware

import (
	"context"
	"errors"
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"github.com/ifan0927/stds-backend/internal/apperr"
	"github.com/ifan0927/stds-backend/internal/auth"
	"github.com/ifan0927/stds-backend/internal/config"
)

const (
	authorizationKey = "Authorization"
)

// AuthMiddleware validates bearer JWTs for protected routes and stores parsed claims in the Gin context.
func AuthMiddleware(cfg config.Config, loader auth.StateLoader) gin.HandlerFunc {
	return authMiddleware(cfg, loader, time.Now)
}

func authMiddleware(cfg config.Config, loader auth.StateLoader, now func() time.Time) gin.HandlerFunc {
	publicPaths := []string{"/v1/auth/login", "/healthz"}
	return func(c *gin.Context) {
		if isPublicPath(c.Request.URL.Path, publicPaths) {
			c.Next()
			return
		}

		var appErr apperr.AppError
		header := c.Request.Header.Get(authorizationKey)
		scheme, bearerToken, found := strings.Cut(header, " ")
		if !found || scheme != "Bearer" || bearerToken == "" {
			appErr = apperr.NewAuthorizationError()
			c.AbortWithStatusJSON(appErr.HTTPStatus, appErr)
			return
		}
		secret := []byte(cfg.JWTSecret)
		token, ok := extractToken(c, bearerToken, secret, now)
		if !ok {
			return
		}

		claims, ok := token.Claims.(*auth.Claims)
		if !ok {
			appErr = apperr.NewAuthorizationError("authorization error: invalid claims")
			c.AbortWithStatusJSON(appErr.HTTPStatus, appErr)
			return
		}
		if !validateClaims(c, claims) {
			return
		}

		userState, ok := extractUserState(c, loader, claims)
		if !ok {
			return
		}

		if !validateUserState(c, userState, claims) {
			return
		}

		ctx := context.WithValue(c.Request.Context(), auth.ClaimsKey, claims)
		ctx = context.WithValue(ctx, auth.UserKey, &userState)
		c.Request = c.Request.WithContext(ctx)
		c.Next()
	}
}

func extractToken(c *gin.Context, bearerToken string, secret []byte, now func() time.Time) (*jwt.Token, bool) {
	token, err := jwt.ParseWithClaims(
		bearerToken,
		&auth.Claims{},
		func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("authorization error: unexpected signing method")
			}
			return secret, nil
		},
		jwt.WithTimeFunc(now),
	)
	if errors.Is(err, jwt.ErrTokenExpired) {
		appErr := apperr.NewTokenExpiredError()
		c.AbortWithStatusJSON(appErr.HTTPStatus, appErr)
		return nil, false
	}
	if err != nil {
		appErr := apperr.NewAuthorizationError("authorization error: error parsing token")
		c.AbortWithStatusJSON(appErr.HTTPStatus, appErr)
		return nil, false
	}
	if !token.Valid {
		appErr := apperr.NewAuthorizationError("authorization error: invalid token")
		c.AbortWithStatusJSON(appErr.HTTPStatus, appErr)
		return nil, false
	}
	return token, true
}

func extractUserState(c *gin.Context, loader auth.StateLoader, claims *auth.Claims) (auth.UserState, bool) {
	userState, err := loader.Load(c.Request.Context(), claims.UserID)
	if errors.Is(err, auth.ErrUserNotFound) {
		appErr := apperr.NewAuthorizationError("authorization error: user not found")
		c.AbortWithStatusJSON(appErr.HTTPStatus, appErr)
		return auth.UserState{}, false
	}
	if err != nil {
		appErr := apperr.WrapInternal(err)
		c.AbortWithStatusJSON(appErr.HTTPStatus, appErr)
		return auth.UserState{}, false
	}
	return userState, true
}

func validateUserState(c *gin.Context, userState auth.UserState, claims *auth.Claims) bool {
	if !userState.IsEnabled {
		appErr := apperr.NewAuthorizationError("authorization error: user is disabled")
		c.AbortWithStatusJSON(appErr.HTTPStatus, appErr)
		return false
	}

	if userState.PasswordChangedAt != nil && !claims.IssuedAt.After(*userState.PasswordChangedAt) {
		appErr := apperr.NewTokenExpiredError()
		c.AbortWithStatusJSON(appErr.HTTPStatus, appErr)
		return false
	}
	return true
}

func validateClaims(c *gin.Context, claims *auth.Claims) bool {
	if claims.Subject != strconv.FormatInt(claims.UserID, 10) {
		appErr := apperr.NewAuthorizationError("authorization error: invalid claims")
		c.AbortWithStatusJSON(appErr.HTTPStatus, appErr)
		return false
	}
	return true
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
