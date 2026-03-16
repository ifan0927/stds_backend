package config

import (
	"fmt"
	"log/slog"
	"path/filepath"
	"time"

	env "github.com/caarlos0/env/v11"
)

// Config 定義應用程式啟動所需的環境設定。
type Config struct {
	AppEnv          string        `env:"APP_ENV" envDefault:"development"`
	GinMode         string        `env:"GIN_MODE" envDefault:"debug"`
	Port            string        `env:"PORT" envDefault:"8080"`
	LogLevel        string        `env:"LOG_LEVEL" envDefault:"info"`
	ShutdownTimeout time.Duration `env:"SHUTDOWN_TIMEOUT" envDefault:"10s"`

	DBURL                          string        `env:"STDS_DB_URL"`
	DBHost                         string        `env:"DB_HOST"`
	DBPort                         int           `env:"DB_PORT" envDefault:"5432"`
	DBUser                         string        `env:"DB_USER"`
	DBPassword                     string        `env:"DB_PASSWORD"`
	DBName                         string        `env:"DB_NAME"`
	DBSSLMode                      string        `env:"DB_SSLMODE" envDefault:"disable"`
	DBMaxOpenConns                 int           `env:"DB_MAX_OPEN_CONNS" envDefault:"10"`
	DBMaxIdleConns                 int           `env:"DB_MAX_IDLE_CONNS" envDefault:"5"`
	DBConnMaxLifetime              time.Duration `env:"DB_CONN_MAX_LIFETIME" envDefault:"30m"`
	DBConnMaxIdleTime              time.Duration `env:"DB_CONN_MAX_IDLE_TIME" envDefault:"5m"`
	CloudSQLInstanceConnectionName string        `env:"CLOUDSQL_INSTANCE_CONNECTION_NAME"`
	CloudSQLSocketDir              string        `env:"CLOUDSQL_SOCKET_DIR" envDefault:"/cloudsql"`
}

// Load 讀取環境變數並轉成 Config。
func Load() (Config, error) {
	cfg, err := env.ParseAs[Config]()
	if err != nil {
		return Config{}, fmt.Errorf("parse config: %w", err)
	}
	if err := cfg.Validate(); err != nil {
		return Config{}, err
	}
	return cfg, nil
}

// Validate 檢查啟動階段必要的設定是否齊備。
func (c Config) Validate() error {
	if c.DBURL != "" {
		return nil
	}
	if c.DBUser == "" {
		return fmt.Errorf("DB_USER is required when STDS_DB_URL is not set")
	}
	if c.DBName == "" {
		return fmt.Errorf("DB_NAME is required when STDS_DB_URL is not set")
	}
	if c.effectiveDBHost() == "" {
		return fmt.Errorf("DB_HOST or CLOUDSQL_INSTANCE_CONNECTION_NAME is required when STDS_DB_URL is not set")
	}
	return nil
}

// DatabaseDSN 回傳 GORM 使用的 PostgreSQL DSN。
func (c Config) DatabaseDSN() string {
	if c.DBURL != "" {
		return c.DBURL
	}

	host := c.effectiveDBHost()
	return fmt.Sprintf(
		"host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
		host,
		c.DBPort,
		c.DBUser,
		c.DBPassword,
		c.DBName,
		c.DBSSLMode,
	)
}

// LogValue 實作 slog.LogValuer，避免敏感設定直接寫入 structured log。
func (c Config) LogValue() slog.Value {
	return slog.GroupValue(
		slog.String("app_env", c.AppEnv),
		slog.String("gin_mode", c.GinMode),
		slog.String("port", c.Port),
		slog.String("log_level", c.LogLevel),
		slog.Duration("shutdown_timeout", c.ShutdownTimeout),
		slog.String("db_url", redactIfSet(c.DBURL)),
		slog.String("db_host", c.DBHost),
		slog.Int("db_port", c.DBPort),
		slog.String("db_user", c.DBUser),
		slog.String("db_password", redactIfSet(c.DBPassword)),
		slog.String("db_name", c.DBName),
		slog.String("db_sslmode", c.DBSSLMode),
		slog.Int("db_max_open_conns", c.DBMaxOpenConns),
		slog.Int("db_max_idle_conns", c.DBMaxIdleConns),
		slog.Duration("db_conn_max_lifetime", c.DBConnMaxLifetime),
		slog.Duration("db_conn_max_idle_time", c.DBConnMaxIdleTime),
		slog.String("cloudsql_instance_connection_name", c.CloudSQLInstanceConnectionName),
		slog.String("cloudsql_socket_dir", c.CloudSQLSocketDir),
	)
}

func (c Config) effectiveDBHost() string {
	if c.CloudSQLInstanceConnectionName != "" {
		return filepath.Join(c.CloudSQLSocketDir, c.CloudSQLInstanceConnectionName)
	}
	return c.DBHost
}

func redactIfSet(v string) string {
	if v == "" {
		return ""
	}
	return "[REDACTED]"
}
