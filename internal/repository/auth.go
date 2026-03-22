package repository

import (
	"context"
	"errors"
	"time"

	"github.com/ifan0927/stds-backend/internal/auth"
	"github.com/ifan0927/stds-backend/internal/service"
	"gorm.io/gorm"
)

type userRow struct {
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

func (userRow) TableName() string {
	return "users"
}

type estateMemberLinkRow struct {
	ID          int64     `gorm:"column:id;primaryKey"`
	EstateID    int64     `gorm:"column:estate_id"`
	UserID      int64     `gorm:"column:user_id"`
	MemberLevel string    `gorm:"column:member_level"`
	CreatedAt   time.Time `gorm:"column:created_at"`
	UpdatedAt   time.Time `gorm:"column:updated_at"`
}

func (estateMemberLinkRow) TableName() string {
	return "estate_member_links"
}

type AuthRepository struct {
	Db *gorm.DB
}

func NewAuthRepository(db *gorm.DB) service.AuthRepository {
	return &AuthRepository{Db: db}
}

func NewStateLoader(db *gorm.DB) auth.StateLoader {
	return &AuthRepository{Db: db}
}

func (r *AuthRepository) FindByUsername(ctx context.Context, username string) (service.AuthUser, error) {
	var row userRow
	err := r.Db.WithContext(ctx).Where("username = ?", username).First(&row).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return service.AuthUser{}, service.ErrNotFound
		}
		return service.AuthUser{}, err
	}
	return toServiceUser(row), nil
}

func toServiceUser(row userRow) service.AuthUser {
	return service.AuthUser{
		UserID:       row.ID,
		Username:     row.Username,
		Name:         row.Name,
		Email:        row.Email,
		Role:         row.Role,
		IsEnabled:    row.IsEnabled,
		PasswordHash: row.PasswordHash,
		Bio:          row.Bio,
		Occupation:   row.Occupation,
		CreatedAt:    row.CreatedAt,
		LastLoginAt:  row.LastLoginAt,
	}
}

func (r *AuthRepository) ListEstateIDsByUserID(ctx context.Context, userID int64) ([]int64, error) {
	var estateIds []int64
	err := r.Db.WithContext(ctx).Model(&estateMemberLinkRow{}).
		Where("user_id = ?", userID).
		Pluck("estate_id", &estateIds).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, service.ErrNotFound
		}
		return nil, err
	}

	return estateIds, nil
}

func (r *AuthRepository) UpdateLastLoginAt(ctx context.Context, userID int64, at time.Time) error {
	_ = r.Db.WithContext(ctx).Model(&userRow{}).
		Where("id = ?", userID).
		Update("last_login_at", at).
		Error

	return nil
}

func (r *AuthRepository) GetPasswordHashByUserID(ctx context.Context, userID int64) (string, error) {
	var hash string
	err := r.Db.WithContext(ctx).Model(&userRow{}).
		Where("id = ?", userID).
		Select("password_hash").
		Scan(&hash).
		Error
	if err != nil {
		return "", err
	}
	return hash, nil
}

func (r *AuthRepository) UpdatePasswordHash(ctx context.Context, userID int64, passwordHash string, at time.Time) error {

	err := r.Db.WithContext(ctx).Model(&userRow{}).
		Where("id = ?", userID).
		Updates(map[string]interface{}{
			"password_hash":       passwordHash,
			"password_changed_at": at,
		}).
		Error
	if err != nil {
		return err
	}

	return nil
}

func (r *AuthRepository) Load(ctx context.Context, userID int64) (auth.UserState, error) {
	var row userRow
	err := r.Db.WithContext(ctx).
		Select("is_enabled", "password_changed_at").
		First(&row, userID).Error

	if errors.Is(err, gorm.ErrRecordNotFound) {
		return auth.UserState{}, auth.ErrUserNotFound
	}
	if err != nil {
		return auth.UserState{}, err
	}
	return auth.UserState{
		UserID:            userID,
		IsEnabled:         row.IsEnabled,
		PasswordChangedAt: row.PasswordChangedAt,
	}, nil
}

type authFields struct {
	IsEnabled         bool
	PasswordChangedAt *time.Time
}
