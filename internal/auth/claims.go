package auth

import "github.com/golang-jwt/jwt/v5"

type Claims struct {
	UserID    int    `json:"user_id"`
	Username  string `json:"username"`
	Role      string `json:"role"`
	EstateIDs []int  `json:"estate_ids"`
	jwt.RegisteredClaims
}
