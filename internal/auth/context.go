package auth

import (
	"context"

	"github.com/ifan0927/stds-backend/internal/apperr"
)

type ContextKey string

const ClaimsKey ContextKey = "claims"
const UserKey ContextKey = "user"

func GetClaims(c context.Context) (*Claims, error) {
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

func GetCurrentUserState(c context.Context) (*UserState, error) {
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
