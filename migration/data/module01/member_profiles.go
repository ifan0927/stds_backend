package module01

import (
	"context"
	"fmt"
	"path/filepath"

	"github.com/ifan0927/stds-backend/migration/data/shared"
	"github.com/jackc/pgx/v5/pgxpool"
)

// MigrateMemberProfiles reads input/01_estate_mems.json and inserts into estate_member_profiles.
// Prerequisite: users must already be migrated.
func MigrateMemberProfiles(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) error {
	records, err := shared.ReadJSONL(filepath.Join(inputDir, "01_estate_mems.json"))
	if err != nil {
		return fmt.Errorf("read 01_estate_mems.json: %w", err)
	}

	// Load valid user IDs
	validUsers := map[int64]bool{}
	if !dryRun {
		rows, err := db.Query(ctx, `SELECT id FROM users`)
		if err != nil {
			return fmt.Errorf("load users: %w", err)
		}
		defer rows.Close()
		for rows.Next() {
			var id int64
			if err := rows.Scan(&id); err != nil {
				return err
			}
			validUsers[id] = true
		}
	}

	sum := &shared.Summary{Table: "estate_member_profiles", Total: len(records)}

	for _, r := range records {
		userID := shared.Int64Val(r, "estate_mem_uid")

		if !dryRun && !validUsers[userID] {
			shared.Logger.Warn("skip member_profile: user not found", "user_id", userID)
			sum.Skipped++
			continue
		}

		unit := shared.NullableString(shared.StringVal(r, "estate_mem_unit"))
		title := shared.NullableString(shared.StringVal(r, "estate_mem_title"))

		textColor := shared.StringVal(r, "estate_cal_color")
		if textColor == "" {
			textColor = "#FFFFFF"
		}
		bgColor := shared.StringVal(r, "estate_cal_bg_color")
		if bgColor == "" {
			bgColor = "#6EB3E5"
		}

		if dryRun {
			shared.Logger.Debug("dry-run: would insert member_profile", "user_id", userID)
			sum.Inserted++
			continue
		}

		_, err := db.Exec(ctx, `
			INSERT INTO estate_member_profiles
				(user_id, unit, title, calendar_text_color, calendar_bg_color, created_at, updated_at)
			VALUES ($1, $2, $3, $4, $5, now(), now())
			ON CONFLICT (user_id) DO NOTHING`,
			userID, unit, title, textColor, bgColor,
		)
		if err != nil {
			shared.Logger.Error("insert member_profile failed", "user_id", userID, "error", err)
			sum.Errors++
			continue
		}
		sum.Inserted++
	}

	sum.Log()
	return nil
}
