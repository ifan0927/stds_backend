package db

import (
	"time"

	"github.com/ifan0927/stds-backend/internal/config"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
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

	sqlDB.SetMaxOpenConns(10)
	sqlDB.SetMaxIdleConns(5)
	sqlDB.SetConnMaxLifetime(30 * time.Minute)

	return db, nil

}
