package module02

import (
	"context"
	"fmt"
	"path/filepath"
	"time"

	"github.com/ifan0927/stds-backend/migration/data/shared"
	"github.com/jackc/pgx/v5/pgxpool"
)

// MigrateScheduleReplies reads input/02_estate_reply.json and inserts into schedule_replies.
// Source: xx_estate_reply (116 rows).
// estate_reply_date → replied_at (TIMESTAMPTZ).
func MigrateScheduleReplies(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) error {
	records, err := shared.ReadJSONL(filepath.Join(inputDir, "02_estate_reply.json"))
	if err != nil {
		return fmt.Errorf("read 02_estate_reply.json: %w", err)
	}

	validSchedules := map[int64]bool{}
	validUsers := map[int64]bool{}
	if !dryRun {
		sRows, err := db.Query(ctx, `SELECT id FROM schedules`)
		if err != nil {
			return fmt.Errorf("load schedules: %w", err)
		}
		defer sRows.Close()
		for sRows.Next() {
			var id int64
			if err := sRows.Scan(&id); err != nil {
				return err
			}
			validSchedules[id] = true
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

	sum := &shared.Summary{Table: "schedule_replies", Total: len(records)}

	for _, r := range records {
		id := shared.Int64Val(r, "estate_reply_id")
		scheduleID := shared.Int64Val(r, "estate_schedule_id")
		authorUserID := shared.Int64Val(r, "estate_reply_uid")
		content := shared.StringVal(r, "estate_reply_content")

		if !dryRun && !validSchedules[scheduleID] {
			shared.Logger.Warn("skip schedule_reply: schedule not found",
				"reply_id", id, "schedule_id", scheduleID)
			sum.Skipped++
			continue
		}
		if !dryRun && !validUsers[authorUserID] {
			shared.Logger.Warn("skip schedule_reply: author user not found",
				"reply_id", id, "author_user_id", authorUserID)
			sum.Skipped++
			continue
		}

		// replied_at: DATETIME → TIMESTAMPTZ
		repliedAt := time.Now().UTC()
		if ts := shared.StringVal(r, "estate_reply_date"); ts != "" {
			if t, err := time.ParseInLocation("2006-01-02 15:04:05", ts, time.UTC); err == nil {
				repliedAt = t
			}
		}

		if dryRun {
			shared.Logger.Debug("dry-run: would insert schedule_reply",
				"reply_id", id, "schedule_id", scheduleID)
			sum.Inserted++
			continue
		}

		_, err := db.Exec(ctx, `
			INSERT INTO schedule_replies (
				id, schedule_id, content, author_user_id,
				replied_at, created_at, updated_at, deleted_at
			) VALUES ($1, $2, $3, $4, $5, now(), now(), NULL)
			ON CONFLICT (id) DO NOTHING`,
			id, scheduleID, content, authorUserID, repliedAt,
		)
		if err != nil {
			shared.Logger.Error("insert schedule_reply failed", "reply_id", id, "error", err)
			sum.Errors++
			continue
		}
		sum.Inserted++
	}

	if !dryRun {
		if _, err := db.Exec(ctx,
			`SELECT setval(pg_get_serial_sequence('schedule_replies','id'), coalesce(max(id),1)) FROM schedule_replies`,
		); err != nil {
			shared.Logger.Warn("reset schedule_replies sequence failed", "error", err)
		}
	}

	sum.Log()
	return nil
}
