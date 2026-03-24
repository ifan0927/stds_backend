package service

import "errors"

var (
	// ErrNotFound marks repository lookups that did not match any row.
	ErrNotFound = errors.New("not found")
)
