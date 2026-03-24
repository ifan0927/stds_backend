package service

import (
	"context"
	"time"

	"github.com/ifan0927/stds-backend/internal/config"
	"github.com/shopspring/decimal"
	"gorm.io/gorm"
)

type EstateService interface {
	ListEstates(ctx context.Context, page int, pagesize int) (PageInfo, []EstateSummary, error)
	CreateEstate(ctx context.Context, estate CreateEstateInput) (*EstateRow, error)
	DeleteEstate(ctx context.Context, estateID int64) error
	GetEstate(ctx context.Context, estateID int64) (*EstateRow, error)
	UpdateEstate(ctx context.Context, estateID int64, estate UpdateEstateInput) (*EstateRow, error)
}

type EstateRepository interface {
	ListEstates(ctx context.Context, page int, pagesize int) (PageInfo, []EstateSummary, error)
	CreateEstate(ctx context.Context, estate CreateEstateInput) (*EstateRow, error)
	DeleteEstate(ctx context.Context, estateID int64) error
	GetEstate(ctx context.Context, estateID int64) (*EstateRow, error)
	UpdateEstate(ctx context.Context, estateID int64, estate UpdateEstateInput) (*EstateRow, error)
}

type UserRepository interface {
	FindOrCreateByUsername(ctx context.Context, input FindOrCreateUserInput) (*UserRow, error)
}

type EstateRow struct {
	ID                      int64
	Title                   string
	ShortTitle              string
	OwnerUserID             *int64
	OwnerName               string
	OwnerEmail              string
	Address                 *string
	Phone                   *string
	Website                 *string
	Facebook                *string
	Note                    *string
	Facilities              []string
	ElectricityRate         decimal.Decimal
	ElectricityBillingCycle string
	Zones                   []string
	CreatedAt               time.Time
	UpdatedAt               time.Time
	DeletedAt               *time.Time
}

type UserRow struct {
	ID                int64
	Username          string
	Name              string
	Email             string
	PasswordHash      string
	Occupation        *string
	Bio               *string
	AvatarPath        *string
	Role              string
	IsEnabled         bool
	LastLoginAt       *time.Time
	CreatedAt         time.Time
	UpdatedAt         time.Time
	DeletedAt         *time.Time
	PasswordChangedAt *time.Time
}

type EstateSummary struct {
	EstateID   int64
	Title      string
	ShortTitle string
}

type PageInfo struct {
	Total    int
	Page     int
	PageSize int
}

type CreateEstateInput struct {
	Title                   string
	ShortTitle              string
	OwnerName               string
	OwnerUsername           string
	OwnerEmail              string
	Address                 *string
	Phone                   *string
	Website                 *string
	Facebook                *string
	Note                    *string
	Facilities              *[]string
	ElectricityRate         decimal.Decimal
	ElectricityBillingCycle string
	Zones                   *[]string
}

type UpdateEstateInput struct {
	Title                   string
	ShortTitle              string
	OwnerName               string
	OwnerEmail              string
	Address                 *string
	Phone                   *string
	Website                 *string
	Facebook                *string
	Note                    *string
	Facilities              *[]string
	ElectricityRate         decimal.Decimal
	ElectricityBillingCycle string
	Zones                   *[]string
}

type FindOrCreateUserInput struct {
	Username     string
	Name         string
	Email        string
	PasswordHash string
	Role         string
}

type estateService struct {
	db         *gorm.DB
	estateRepo func(*gorm.DB) EstateRepository
	userRepo   func(*gorm.DB) UserRepository
	cfg        config.Config
}

func NewEstateService(
	db *gorm.DB,
	estateRepo func(*gorm.DB) EstateRepository,
	userRepo func(*gorm.DB) UserRepository,
	cfg config.Config) EstateService {
	return &estateService{
		db:         db,
		estateRepo: estateRepo,
		userRepo:   userRepo,
		cfg:        cfg,
	}
}

func (s *estateService) ListEstates(ctx context.Context, page int, pagesize int) (PageInfo, []EstateSummary, error) {
	return s.estateRepo(s.db).ListEstates(ctx, page, pagesize)
}

func (s *estateService) CreateEstate(ctx context.Context, estate CreateEstateInput) (*EstateRow, error) {
	return s.estateRepo(s.db).CreateEstate(ctx, estate)
}

func (s *estateService) DeleteEstate(ctx context.Context, estateID int64) error {
	return s.estateRepo(s.db).DeleteEstate(ctx, estateID)
}

func (s *estateService) GetEstate(ctx context.Context, estateID int64) (*EstateRow, error) {
	return s.estateRepo(s.db).GetEstate(ctx, estateID)
}

func (s *estateService) UpdateEstate(ctx context.Context, estateID int64, estate UpdateEstateInput) (*EstateRow, error) {
	return s.estateRepo(s.db).UpdateEstate(ctx, estateID, estate)
}
