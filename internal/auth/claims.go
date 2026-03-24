package auth

import "github.com/golang-jwt/jwt/v5"

// Claims stores the JWT payload used by STDS access tokens.
type Claims struct {
	UserID   int64  `json:"user_id"`
	Username string `json:"username"`
	Role     string `json:"role"`
	jwt.RegisteredClaims
}
