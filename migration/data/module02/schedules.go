package module02

import (
	"context"
	"fmt"
	"path/filepath"
	"time"

	"github.com/ifan0927/stds-backend/migration/data/shared"
	"github.com/jackc/pgx/v5/pgxpool"
)

// MigrateSchedules reads input/02_estate_schedule.json and inserts into schedules.
// Source: xx_estate_schedule (5643 rows).
// estate_room_id=0 → room_id=NULL (estate-level schedule).
// estate_schedule_assist=-1 → assist_user_id=NULL.
// status_color is always NULL (old system stored status name only, color in module config).
// kind and status empty string → kept as '' (NOT NULL, empty string is valid).
func MigrateSchedules(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) error {
	records, err := shared.ReadJSONL(filepath.Join(inputDir, "02_estate_schedule.json"))
	if err != nil {
		return fmt.Errorf("read 02_estate_schedule.json: %w", err)
	}

	validEstates := map[int64]bool{}
	validRooms := map[int64]bool{}
	validUsers := map[int64]bool{}
	if !dryRun {
		eRows, err := db.Query(ctx, `SELECT id FROM estates`)
		if err != nil {
			return fmt.Errorf("load estates: %w", err)
		}
		defer eRows.Close()
		for eRows.Next() {
			var id int64
			if err := eRows.Scan(&id); err != nil {
				return err
			}
			validEstates[id] = true
		}

		rRows, err := db.Query(ctx, `SELECT id FROM rooms`)
		if err != nil {
			return fmt.Errorf("load rooms: %w", err)
		}
		defer rRows.Close()
		for rRows.Next() {
			var id int64
			if err := rRows.Scan(&id); err != nil {
				return err
			}
			validRooms[id] = true
		}

		uRows, err := db.Query(ctx, `SELECT id FROM users`)
		if err != nil {
			return fmt.Errorf("load users: %w", err)
		}
		defer uRows.Close()
		for uRows.Next() {
			var id int64
			if err := uRows.Scan(&id); err != nil {
				return err
			}
			validUsers[id] = true
		}
	}

	sum := &shared.Summary{Table: "schedules", Total: len(records)}

	for _, r := range records {
		id := shared.Int64Val(r, "estate_schedule_id")
		estateID := shared.Int64Val(r, "estate_id")
		reporterUserID := shared.Int64Val(r, "estate_schedule_uid")

		if !dryRun && !validEstates[estateID] {
			shared.Logger.Warn("skip schedule: estate not found", "schedule_id", id, "estate_id", estateID)
			sum.Skipped++
			continue
		}
		if !dryRun && !validUsers[reporterUserID] {
			shared.Logger.Warn("skip schedule: reporter user not found",
				"schedule_id", id, "reporter_user_id", reporterUserID)
			sum.Skipped++
			continue
		}

		// room_id: 0 → NULL (estate-level)
		var roomID *int64
		if rid := shared.Int64Val(r, "estate_room_id"); rid != 0 {
			if dryRun || validRooms[rid] {
				roomID = &rid
			} else {
				shared.Logger.Warn("schedule room not found, setting NULL",
					"schedule_id", id, "room_id", rid)
			}
		}

		// scheduled_at: DATETIME → TIMESTAMPTZ
		scheduledAt := time.Now().UTC()
		if ts := shared.StringVal(r, "estate_schedule_date"); ts != "" {
			if t, err := time.ParseInLocation("2006-01-02 15:04:05", ts, time.UTC); err == nil {
				scheduledAt = t
			}
		}

		kind := shared.StringVal(r, "estate_schedule_kind")     // keep '' as ''
		status := shared.StringVal(r, "estate_schedule_status") // keep '' as ''
		content := shared.StringVal(r, "estate_schedule_content")

		// assist_user_id: '-1' → NULL, '0' → 0 (all members), '>0' → user_id
		var assistUserID *int64
		assistRaw := shared.Int64Val(r, "estate_schedule_assist")
		if assistRaw >= 0 {
			assistUserID = &assistRaw
		}

		if dryRun {
			shared.Logger.Debug("dry-run: would insert schedule",
				"schedule_id", id, "estate_id", estateID)
			sum.Inserted++
			continue
		}

		_, err := db.Exec(ctx, `
			INSERT INTO schedules (
				id, estate_id, room_id, scheduled_at,
				kind, status, status_color, content,
				reporter_user_id, assist_user_id,
				created_at, updated_at, deleted_at
			) VALUES (
				$1, $2, $3, $4,
				$5, $6, NULL, $7,
				$8, $9,
				now(), now(), NULL
			)
			ON CONFLICT (id) DO NOTHING`,
			id, estateID, roomID, scheduledAt,
			kind, status, content,
			reporterUserID, assistUserID,
		)
		if err != nil {
			shared.Logger.Error("insert schedule failed", "schedule_id", id, "error", err)
			sum.Errors++
			continue
		}
		sum.Inserted++
	}

	if !dryRun {
		if _, err := db.Exec(ctx,
			`SELECT setval(pg_get_serial_sequence('schedules','id'), coalesce(max(id),1)) FROM schedules`,
		); err != nil {
			shared.Logger.Warn("reset schedules sequence failed", "error", err)
		}
	}

	sum.Log()
	return nil
}
