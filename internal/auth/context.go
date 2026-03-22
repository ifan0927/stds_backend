package auth

import (
	"context"

	"github.com/ifan0927/stds-backend/internal/apperr"
)

// ContextKey identifies auth values stored on the request context.
type ContextKey string

// ClaimsKey stores auth claims on the request context.
const ClaimsKey ContextKey = "claims"

// UserKey stores the current user state on the request context.
const UserKey ContextKey = "user"

// ClaimsFromContext returns the auth claims stored on the request context.
func ClaimsFromContext(c context.Context) (*Claims, error) {
	val := c.Value(ClaimsKey)
	if val == nil {
		return nil, apperr.NewInternalError("no claims found")
	}
	claims, ok := val.(*Claims)
	if !ok {
		return nil, apperr.NewInternalError("claims type mismatch")
	}
	return claims, nil
}

// UserStateFromContext returns the current user state stored on the request context.
func UserStateFromContext(c context.Context) (*UserState, error) {
	val := c.Value(UserKey)
	if val == nil {
		return nil, apperr.NewInternalError("no user state")
	}
	userState, ok := val.(*UserState)
	if !ok {
		return nil, apperr.NewInternalError("userState type mismatch")
	}
	return userState, nil
}
