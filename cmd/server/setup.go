package main

import (
	"log/slog"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/ifan0927/stds-backend/internal/api"
	"github.com/ifan0927/stds-backend/internal/apperr"
	"github.com/ifan0927/stds-backend/internal/config"
	"github.com/ifan0927/stds-backend/internal/handler"
	"github.com/ifan0927/stds-backend/internal/middleware"
	"github.com/ifan0927/stds-backend/internal/repository"
	"github.com/ifan0927/stds-backend/internal/service"
	"github.com/lmittmann/tint"
	"gorm.io/gorm"
)

// initLogger builds the application logger from runtime configuration.
func initLogger(cfg config.Config) (*slog.Logger, error) {
	w := os.Stdout
	var loglevel slog.LevelVar
	err := loglevel.UnmarshalText([]byte(cfg.LogLevel))
	if err != nil {
		return nil, err
	}
	var logHandler slog.Handler
	if os.Getenv("APP_ENV") == "dev" {
		logHandler = tint.NewHandler(w, &tint.Options{
			Level: &loglevel,
		})
	} else {
		logHandler = slog.NewJSONHandler(w, &slog.HandlerOptions{
			Level: &loglevel,
		})
	}

	return slog.New(logHandler), nil
}

// initRouter configures the Gin engine, shared middleware, health check, and API handlers.
func initRouter(cfg config.Config, gormDB *gorm.DB) *gin.Engine {

	repo := repository.NewAuthRepository(gormDB)
	issuer := service.JWTIssuer{Secret: []byte(cfg.JWTSecret)}
	loader := repository.NewStateLoader(gormDB)

	authSvc := service.NewAuthService(repo, issuer, nil, cfg)
	server := handler.NewServer(authSvc)

	r := gin.New()
	r.Use(middleware.Logger())
	r.Use(middleware.ErrorHandler())
	r.Use(middleware.AuthMiddleware(cfg, loader))
	r.Use(gin.Recovery())

	r.GET("/healthz", func(c *gin.Context) {
		sqlDB, err := gormDB.DB()
		var appErr apperr.AppError
		if err != nil {
			appErr = apperr.WrapInternal(err)
			c.JSON(appErr.HTTPStatus, appErr)
			return
		}
		err = sqlDB.Ping()
		if err != nil {
			appErr := apperr.WrapInternal(err)
			c.JSON(appErr.HTTPStatus, appErr)
			return
		}
		c.JSON(http.StatusOK, gin.H{
			"status": "ok",
		})
	})

	strictHandler := api.NewStrictHandler(server, nil)

	api.RegisterHandlers(r, strictHandler)
	return r
}
