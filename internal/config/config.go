package config

type Config struct {
	Port      string `env:"PORT" envDefault:"8080"`
	JWTSecret string `env:"JWT_SECRET,required"`
	LogLevel  string `env:"LOG_LEVEL" envDefault:"info"`
	DB        DBconfig
}

type DBconfig struct {
	DSN string `env:"DATABASE_DSN,required"`
}
