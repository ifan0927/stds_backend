package auth

import (
	"context"

	"github.com/ifan0927/stds-backend/internal/apperr"
)

// CheckEstateAccess returns the caller's estate role when the current auth state grants access.
func CheckEstateAccess(ctx context.Context, estateID int64) (accessLevel string, err error) {
	claims, err := ClaimsFromContext(ctx)
	if err != nil {
		return "", err
	}
	if claims.Role == "admin" {
		return "admin", nil
	}

	userState, err := UserStateFromContext(ctx)
	if err != nil {
		return "", err
	}

	accessLevel, ok := userState.EstateRoles[estateID]
	if !ok {
		return "", apperr.NewEstateAccessDeniedError()
	}
	return accessLevel, nil
}
