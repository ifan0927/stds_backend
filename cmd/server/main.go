package main

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/caarlos0/env/v11"
	"github.com/ifan0927/stds-backend/internal/config"
	"github.com/ifan0927/stds-backend/internal/db"
	"github.com/joho/godotenv"
)

func main() {

	// prepare env
	var err error
	if os.Getenv("APP_ENV") == "dev" {
		err = godotenv.Load(".env")
		if err != nil {
			_, _ = fmt.Fprintf(os.Stderr, "Error loading .env file: %s\n", err.Error())
		}
	}
	cfg := config.Config{}
	err = env.Parse(&cfg)
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Error parsing config: %s\n", err.Error())
		os.Exit(1)
	}

	// init logger
	logger, err := initLogger(cfg)
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Error initializing logger: %s\n", err.Error())
		os.Exit(1)
	}
	slog.SetDefault(logger)

	// init database
	gormDB, err := db.InitDB(cfg.DB)
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Error initializing database: %s\n", err.Error())
		os.Exit(1)
	}

	// init Router
	r := initRouter(cfg, gormDB)

	// init server & graceful shutdown
	srv := &http.Server{
		Addr:    ":" + cfg.Port,
		Handler: r,
	}
	go func() {
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			_, _ = fmt.Fprintf(os.Stderr, "Error starting server: %s\n", err.Error())
			os.Exit(1)
		}
	}()

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	<-ctx.Done()
	shutdownCtx, cancel :=
		context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Shutdown(shutdownCtx); err != nil {
		slog.Error("graceful shutdown failed", "err", err)
	}
	slog.Info("server shutdown")

}
