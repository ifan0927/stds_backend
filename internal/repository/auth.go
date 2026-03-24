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

// AuthRepository implements auth persistence and state loading against the database.
type AuthRepository struct {
	DB *gorm.DB
}

// NewAuthRepository creates the auth repository implementation.
func NewAuthRepository(db *gorm.DB) service.AuthRepository {
	return &AuthRepository{DB: db}
}

// NewStateLoader creates the auth state loader backed by the auth repository.
func NewStateLoader(db *gorm.DB) auth.StateLoader {
	return &AuthRepository{DB: db}
}

// FindByUsername returns the auth user record for the given username.
func (r *AuthRepository) FindByUsername(ctx context.Context, username string) (service.AuthUser, error) {
	var row userRow
	err := r.DB.WithContext(ctx).Where("username = ?", username).First(&row).Error
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

// UpdateLastLoginAt stores the last successful login time for the given user.
func (r *AuthRepository) UpdateLastLoginAt(ctx context.Context, userID int64, at time.Time) error {
	_ = r.DB.WithContext(ctx).Model(&userRow{}).
		Where("id = ?", userID).
		Update("last_login_at", at).
		Error

	return nil
}

// PasswordHashByUserID returns the stored password hash for the given user.
func (r *AuthRepository) PasswordHashByUserID(ctx context.Context, userID int64) (string, error) {
	var row userRow
	err := r.DB.WithContext(ctx).Model(&userRow{}).
		Select("password_hash").
		First(&row, userID).Error
	if errors.Is(err, gorm.ErrRecordNotFound) {
		return "", auth.ErrUserNotFound
	}

	if err != nil {
		return "", err
	}
	return row.PasswordHash, nil
}

// UpdatePasswordHash replaces the user's password hash and updates the change timestamp.
func (r *AuthRepository) UpdatePasswordHash(ctx context.Context, userID int64, passwordHash string, at time.Time) error {

	err := r.DB.WithContext(ctx).Model(&userRow{}).
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

// Load returns auth state required by middleware for the given user.
func (r *AuthRepository) Load(ctx context.Context, userID int64) (auth.UserState, error) {
	var userRow userRow
	err := r.DB.WithContext(ctx).
		Select("is_enabled", "password_changed_at").
		First(&userRow, userID).Error
	if errors.Is(err, gorm.ErrRecordNotFound) {
		return auth.UserState{}, auth.ErrUserNotFound
	}
	if err != nil {
		return auth.UserState{}, err
	}

	var estateMemberRow []estateMemberLinkRow
	if err = r.DB.WithContext(ctx).Model(&estateMemberLinkRow{}).
		Where("user_id = ?", userID).
		Scan(&estateMemberRow).Error; err != nil {
		return auth.UserState{}, err
	}

	result := make(map[int64]string, len(estateMemberRow))
	for _, r := range estateMemberRow {
		result[r.EstateID] = r.MemberLevel
	}

	return auth.UserState{
		UserID:            userID,
		IsEnabled:         userRow.IsEnabled,
		PasswordChangedAt: userRow.PasswordChangedAt,
		EstateRoles:       result,
	}, nil
}
