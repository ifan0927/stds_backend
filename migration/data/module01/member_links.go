package module01

import (
	"context"
	"fmt"
	"path/filepath"

	"github.com/ifan0927/stds-backend/migration/data/shared"
	"github.com/jackc/pgx/v5/pgxpool"
)

// MigrateMemberLinks reads input/01_estate_mem_link.json and inserts into estate_member_links.
// Prerequisite: both estates and users must already be migrated.
func MigrateMemberLinks(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) error {
	records, err := shared.ReadJSONL(filepath.Join(inputDir, "01_estate_mem_link.json"))
	if err != nil {
		return fmt.Errorf("read 01_estate_mem_link.json: %w", err)
	}

	validEstates := map[int64]bool{}
	validUsers := map[int64]bool{}
	estateRows, err := db.Query(ctx, `SELECT id FROM estates`)
	if err != nil {
		return fmt.Errorf("load estates: %w", err)
	}
	defer estateRows.Close()
	for estateRows.Next() {
		var id int64
		if err := estateRows.Scan(&id); err != nil {
			return err
		}
		validEstates[id] = true
	}

	userRows, err := db.Query(ctx, `SELECT id FROM users`)
	if err != nil {
		return fmt.Errorf("load users: %w", err)
	}
	defer userRows.Close()
	for userRows.Next() {
		var id int64
		if err := userRows.Scan(&id); err != nil {
			return err
		}
		validUsers[id] = true
	}

	sum := &shared.Summary{Table: "estate_member_links", Total: len(records)}
	adminCount := 0
	normalCount := 0
	readonlyCount := 0
	fkMissingCount := 0

	for _, r := range records {
		estateID := shared.Int64Val(r, "estate_id")
		userID := shared.Int64Val(r, "estate_mem_uid")
		levelRaw := shared.StringVal(r, "estate_mem_level")

		if !validEstates[estateID] || !validUsers[userID] {
			shared.Logger.Warn("skip member_link: FK not found",
				"estate_id", estateID, "user_id", userID)
			fkMissingCount++
			sum.Skipped++
			continue
		}

		var memberLevel string
		switch levelRaw {
		case "1":
			memberLevel = "admin"
			adminCount++
		case "0":
			memberLevel = "readonly"
			readonlyCount++
			shared.Logger.Warn("member_link level='0' mapped to readonly",
				"estate_id", estateID, "user_id", userID)
		default:
			shared.Logger.Error("unknown member_link level, skipped",
				"estate_id", estateID, "user_id", userID, "level", levelRaw)
			sum.Errors++
			continue
		}

		if dryRun {
			shared.Logger.Debug("dry-run: would insert member_link",
				"estate_id", estateID, "user_id", userID, "level", memberLevel)
			sum.Inserted++
			continue
		}

		_, err := db.Exec(ctx, `
			INSERT INTO estate_member_links (estate_id, user_id, member_level, created_at, updated_at)
			VALUES ($1, $2, $3, now(), now())
			ON CONFLICT (estate_id, user_id) DO NOTHING`,
			estateID, userID, memberLevel,
		)
		if err != nil {
			shared.Logger.Error("insert member_link failed",
				"estate_id", estateID, "user_id", userID, "error", err)
			sum.Errors++
			continue
		}
		sum.Inserted++
	}

	if !dryRun {
		if _, err := db.Exec(ctx,
			`SELECT setval(pg_get_serial_sequence('estate_member_links','id'), coalesce(max(id),1)) FROM estate_member_links`,
		); err != nil {
			shared.Logger.Warn("reset estate_member_links sequence failed", "error", err)
		}
	}

	sum.Log()
	shared.Logger.Info("member_link migration details",
		"table", "estate_member_links",
		"admin_count", adminCount,
		"normal_count", normalCount,
		"readonly_count", readonlyCount,
		"fk_missing_count", fkMissingCount,
		"dry_run", dryRun,
		"note", "legacy backfill does not generate normal",
	)
	return nil
}
