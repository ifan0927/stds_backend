package auth

import "github.com/golang-jwt/jwt/v5"

type Claims struct {
	// Question: 資料庫內是bigint userid 這樣設定uint是對的嗎
	UserID    int    `json:"user_id"`
	Username  string `json:"username"`
	Role      string `json:"role"`
	EstateIDs []int  `json:"estate_ids"`
	jwt.RegisteredClaims
}
