package service

import (
	"context"

	"github.com/google/uuid"
	"github.com/ifan0927/stds-backend/internal/api"
	"github.com/shopspring/decimal"
)

type EstateRepository interface {
	ListEstates(ctx context.Context, page int, pagesize int) (PageInfo, []EstateSummary, error)
	CreateEstate(ctx context.Context, estate CreateEstateInput) (*EstateRow, error)
	DeleteEstate(ctx context.Context, estateID int64) error
	GetEstate(ctx context.Context, estateID int64) (*EstateRow, error)
	UpdateEstate(ctx context.Context, estateID int64, estate UpdateEstateInput) (*EstateRow, error)
}

type EstateSummary struct {
	estateID   int64
	title      string
	shortTitle string
}

type PageInfo struct {
	total    int
	page     int
	pagesize int
}

type CreateEstateInput struct {
	title                   string
	shortTitle              string
	ownerName               string
	ownerEmail              string
	address                 *string
	phone                   *string
	website                 *string
	facebook                *string
	note                    *string
	facilities              *[]string
	electricityRate         decimal.Decimal
	electricityBillingCycle string
	zones                   *[]string
}

type UpdateEstateInput = CreateEstateInput
