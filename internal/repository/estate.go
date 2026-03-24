package repository

import (
	"context"
	"errors"
	"time"

	"github.com/ifan0927/stds-backend/internal/service"
	"github.com/shopspring/decimal"
	"gorm.io/gorm"
)

type EstateRow struct {
	ID                      int64           `gorm:"column:id;primaryKey"`
	Title                   string          `gorm:"column:title"`
	ShortTitle              string          `gorm:"column:short_title"`
	OwnerUserID             *int64          `gorm:"column:owner_user_id"`
	OwnerName               string          `gorm:"column:owner_name"`
	OwnerEmail              string          `gorm:"column:owner_email"`
	Address                 *string         `gorm:"column:address"`
	Phone                   *string         `gorm:"column:phone"`
	Website                 *string         `gorm:"column:website"`
	Facebook                *string         `gorm:"column:facebook"`
	Note                    *string         `gorm:"column:note"`
	Facilities              []string        `gorm:"column:facilities;type:jsonb;serializer:json"`
	ElectricityRate         decimal.Decimal `gorm:"column:electricity_rate"`
	ElectricityBillingCycle string          `gorm:"column:electricity_billing_cycle"`
	Zones                   []string        `gorm:"column:zones;type:jsonb;serializer:json"`
	CreatedAt               time.Time       `gorm:"column:created_at"`
	UpdatedAt               time.Time       `gorm:"column:updated_at"`
	DeletedAt               gorm.DeletedAt  `gorm:"column:deleted_at"`
}

func (EstateRow) TableName() string {
	return "estates"
}

type EstateRepo struct {
	DB *gorm.DB
}

func NewEstateRepo(db *gorm.DB) service.EstateRepository {
	return &EstateRepo{DB: db}
}
