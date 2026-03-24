package auth

import (
	"context"
	"errors"
	"time"
)

var (
	// ErrUserNotFound marks repository lookups that did not match any user.
	ErrUserNotFound = errors.New("user not found")
)

// StateLoader loads the current auth-related user state used by middleware checks.
type StateLoader interface {
	Load(ctx context.Context, userID int64) (UserState, error)
}

// UserState contains the persisted user flags and estate roles required for request authorization.
type UserState struct {
	UserID            int64
	IsEnabled         bool
	PasswordChangedAt *time.Time
	EstateRoles       map[int64]string
}
