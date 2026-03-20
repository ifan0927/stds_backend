package main

import (
	"fmt"
	"log/slog"
	"os"

	"github.com/caarlos0/env/v11"
	"github.com/gin-gonic/gin"
	"github.com/ifan0927/stds-backend/internal/api"
	"github.com/ifan0927/stds-backend/internal/apperr"
	"github.com/ifan0927/stds-backend/internal/config"
	"github.com/ifan0927/stds-backend/internal/db"
	"github.com/ifan0927/stds-backend/internal/handler"
	"github.com/ifan0927/stds-backend/internal/middleware"
	"github.com/joho/godotenv"
)

func main() {

	// prepare env
	var err error
	if os.Getenv("APP_ENV") == "dev" {
		err = godotenv.Load(".env")
		if err != nil {
			_, _ = fmt.Fprintf(os.Stderr, "Error loading .env file")
		}
	}

	cfg := config.Config{}
	err = env.Parse(&cfg)
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Error parsing config")
		os.Exit(1)
	}

	// initial slog
	var Loglevel slog.LevelVar
	err = Loglevel.UnmarshalText([]byte(cfg.LogLevel))
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Error parsing log level")
		os.Exit(1)
	}
	logHandler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: &Loglevel,
	})
	slog.SetDefault(slog.New(logHandler))

	// init database
	gormDB, err := db.InitDB(cfg.DB)
	if err != nil {
		slog.Warn("Error initializing database")
		os.Exit(1)
	}

	// init route and middleware
	r := gin.New()
	r.Use(middleware.Logger())
	r.Use(middleware.ErrorHandler())
	r.Use(middleware.AuthMiddleware(cfg))

	// health endpoint
	r.GET("/healthz", func(c *gin.Context) {
		sqlDB, err := gormDB.DB()
		var appErr apperr.AppError
		if err != nil {
			appErr = apperr.NewInternalError("error connecting to database")
			c.JSON(appErr.HTTPStatus, appErr)
			return
		}
		err = sqlDB.Ping()
		if err != nil {
			appErr := apperr.NewInternalError("error pinging database")
			c.JSON(appErr.HTTPStatus, appErr)
			return
		}
		c.JSON(200, gin.H{
			"status": "ok",
		})
	})

	// all endpoint
	server := handler.NewServer()

	strictHandler := api.NewStrictHandler(server, nil)

	api.RegisterHandlers(r, strictHandler)

	err = r.Run(":" + cfg.Port)
	if err != nil {
		slog.Warn("Error starting server")
		os.Exit(1)
	}
}
