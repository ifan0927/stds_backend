// Data migration program for STDS backend.
// Reads JSONL files from migration_input/ and inserts into PostgreSQL.
//
// Usage:
//
//	DATABASE_URL=postgres://... go run ./migration/data/... \
//	  --module=01       # estates, rooms, facility_memos
//	  --module=01post   # member_profiles, member_links (requires users done)
//	  --module=02       # groups, users, user_group_links, tenants, electric_readings, rents, rent_tenant_links, schedules, schedule_replies
//	  --module=seed     # development auth seed data
//	  --module=all      # 01 -> 02 -> 01post in order
//	  --input=./migration_input
//	  --dry-run         # log actions without writing to DB
package main

import (
	"context"
	"flag"
	"fmt"
	"log/slog"
	"os"
	"path/filepath"

	"github.com/ifan0927/stds-backend/migration/data/module01"
	"github.com/ifan0927/stds-backend/migration/data/module02"
	"github.com/ifan0927/stds-backend/migration/data/seed"
	"github.com/ifan0927/stds-backend/migration/data/shared"
	"github.com/jackc/pgx/v5/pgxpool"
)

func main() {
	module := flag.String("module", "", "module to run: 01 | 01post | 02 | seed | all")
	inputDir := flag.String("input", "./migration_input", "path to migration_input directory")
	dryRun := flag.Bool("dry-run", false, "log actions without writing to DB")
	flag.Parse()

	if *module == "" {
		fmt.Fprintln(os.Stderr, "error: --module is required (01 | 01post | 02 | seed | all)")
		os.Exit(1)
	}

	ctx := context.Background()

	var pool *pgxpool.Pool
	if !*dryRun {
		var err error
		pool, err = shared.NewDB(ctx)
		if err != nil {
			slog.Error("db connection failed", "error", err)
			os.Exit(1)
		}
		defer pool.Close()
	}

	switch *module {
	case "01":
		runModule01(ctx, pool, *inputDir, *dryRun)
	case "01post":
		runModule01Post(ctx, pool, *inputDir, *dryRun)
	case "02":
		runModule02(ctx, pool, *inputDir, *dryRun)
	case "seed":
		runSeed(ctx, pool, *dryRun)
	case "all":
		runModule01(ctx, pool, *inputDir, *dryRun)
		runModule02(ctx, pool, *inputDir, *dryRun)
		runModule01Post(ctx, pool, *inputDir, *dryRun)
	default:
		fmt.Fprintf(os.Stderr, "unknown module: %s\n", *module)
		os.Exit(1)
	}

	slog.Info("migration done")
}

func runModule01(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) {
	must("estates", module01.MigrateEstates(ctx, db, inputDir, dryRun))
	must("rooms", module01.MigrateRooms(ctx, db, inputDir, dryRun))
	must("facility_memos", module01.MigrateFacilityMemos(ctx, db, inputDir, dryRun))
}

func runModule01Post(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) {
	if !fileExists(filepath.Join(inputDir, "01_estate_mems.json")) {
		slog.Warn("skip step: input file not found", "step", "member_profiles", "file", filepath.Join(inputDir, "01_estate_mems.json"))
	} else {
		must("member_profiles", module01.MigrateMemberProfiles(ctx, db, inputDir, dryRun))
	}

	if !fileExists(filepath.Join(inputDir, "01_estate_mem_link.json")) {
		slog.Warn("skip step: input file not found", "step", "member_links", "file", filepath.Join(inputDir, "01_estate_mem_link.json"))
	} else {
		must("member_links", module01.MigrateMemberLinks(ctx, db, inputDir, dryRun))
	}
}

func runModule02(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) {
	must("groups", module02.MigrateGroups(ctx, db, inputDir, dryRun))
	must("users", module02.MigrateUsers(ctx, db, inputDir, dryRun))
	must("user_group_links", module02.MigrateUserGroupLinks(ctx, db, inputDir, dryRun))
	must("tenants", module02.MigrateTenants(ctx, db, inputDir, dryRun))
	must("electric_readings", module02.MigrateElectricReadings(ctx, db, inputDir, dryRun))
	must("rents", module02.MigrateRents(ctx, db, inputDir, dryRun))
	must("rent_tenant_links", module02.MigrateRentTenantLinks(ctx, db, inputDir, dryRun))
	must("schedules", module02.MigrateSchedules(ctx, db, inputDir, dryRun))
	must("schedule_replies", module02.MigrateScheduleReplies(ctx, db, inputDir, dryRun))
}

func runSeed(ctx context.Context, db *pgxpool.Pool, dryRun bool) {
	must("seed_auth", seed.SeedAuth(ctx, db, dryRun))
	must("seed_estate", seed.SeedEstate(ctx, db, dryRun))
}

func must(step string, err error) {
	if err != nil {
		slog.Error("step failed", "step", step, "error", err)
		os.Exit(1)
	}
	slog.Info("step done", "step", step)
}

func fileExists(path string) bool {
	info, err := os.Stat(path)
	if err != nil {
		return false
	}
	return !info.IsDir()
}
