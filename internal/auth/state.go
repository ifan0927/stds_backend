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

type StateLoader interface {
	Load(ctx context.Context, userID int64) (UserState, error)
}

type UserState struct {
	UserID            int64
	IsEnabled         bool
	PasswordChangedAt *time.Time
}
