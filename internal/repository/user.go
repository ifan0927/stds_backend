package repository

import (
	"time"

	"github.com/ifan0927/stds-backend/internal/service"
	"gorm.io/gorm"
)

type UserRow struct {
	ID                int64          `gorm:"column:id;primaryKey"`
	Username          string         `gorm:"column:username"`
	Name              string         `gorm:"column:name"`
	Email             string         `gorm:"column:email"`
	PasswordHash      string         `gorm:"column:password_hash"`
	Occupation        *string        `gorm:"column:occupation"`
	Bio               *string        `gorm:"column:bio"`
	AvatarPath        *string        `gorm:"column:avatar_path"`
	Role              string         `gorm:"column:role"`
	IsEnabled         bool           `gorm:"column:is_enabled"`
	LastLoginAt       *time.Time     `gorm:"column:last_login_at"`
	CreatedAt         time.Time      `gorm:"column:created_at"`
	UpdatedAt         time.Time      `gorm:"column:updated_at"`
	DeletedAt         gorm.DeletedAt `gorm:"column:deleted_at"`
	PasswordChangedAt *time.Time     `gorm:"column:password_changed_at"`
}

func (UserRow) TableName() string {
	return "users"
}

type UserRepo struct {
	DB *gorm.DB
}

func NewUserRepo(db *gorm.DB) service.UserRepository {
	return &UserRepo{DB: db}
}
