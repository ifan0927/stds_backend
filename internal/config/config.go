package config

import "log/slog"

// Config contains application settings loaded from environment variables.
type Config struct {
	Port      string `env:"PORT" envDefault:"8080"`
	JWTSecret string `env:"JWT_SECRET,required"`
	LogLevel  string `env:"LOG_LEVEL" envDefault:"info"`
	DB        DBconfig
}

// DBconfig contains database connection settings loaded from environment variables.
type DBconfig struct {
	DSN string `env:"DATABASE_DSN,required"`
}

// LogValue returns a redacted structured log representation of Config.
func (c Config) LogValue() slog.Value {
	return slog.GroupValue(
		slog.String("port", c.Port),
		slog.String("log_level", c.LogLevel))
}

// LogValue returns a redacted structured log representation of DBconfig.
func (c DBconfig) LogValue() slog.Value {
	return slog.GroupValue(slog.String("dsn", "[REDACTED]"))
}
