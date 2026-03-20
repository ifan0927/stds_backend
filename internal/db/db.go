package db

import (
	"time"

	"github.com/ifan0927/stds-backend/internal/config"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

const (
	defaultMaxOpenConns    = 10
	defaultMaxIdleConns    = 5
	defaultConnMaxLifetime = 30 * time.Minute
)

// InitDB opens the primary PostgreSQL connection and applies the default pool settings.
func InitDB(cfg config.DBconfig) (*gorm.DB, error) {
	db, err := gorm.Open(postgres.Open(cfg.DSN), &gorm.Config{})
	if err != nil {
		return nil, err
	}

	sqlDB, err := db.DB()
	if err != nil {
		return nil, err
	}

	sqlDB.SetMaxOpenConns(defaultMaxOpenConns)
	sqlDB.SetMaxIdleConns(defaultMaxIdleConns)
	sqlDB.SetConnMaxLifetime(defaultConnMaxLifetime)

	return db, nil

}
