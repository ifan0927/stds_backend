package module02

import (
	"context"
	"fmt"
	"path/filepath"

	"github.com/ifan0927/stds-backend/migration/data/shared"
	"github.com/jackc/pgx/v5/pgxpool"
)

// MigrateUserGroupLinks reads input/02_groups_users_link.json and inserts into user_group_links.
// Source: xx_groups_users_link (97 rows, may contain orphans).
// Field mapping: linkid→id, uid→user_id, groupid→group_id.
func MigrateUserGroupLinks(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) error {
	records, err := shared.ReadJSONL(filepath.Join(inputDir, "02_groups_users_link.json"))
	if err != nil {
		return fmt.Errorf("read 02_groups_users_link.json: %w", err)
	}

	validUsers := map[int64]bool{}
	validGroups := map[int64]bool{}
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

		gRows, err := db.Query(ctx, `SELECT id FROM groups`)
		if err != nil {
			return fmt.Errorf("load groups: %w", err)
		}
		defer gRows.Close()
		for gRows.Next() {
			var id int64
			if err := gRows.Scan(&id); err != nil {
				return err
			}
			validGroups[id] = true
		}
	}

	sum := &shared.Summary{Table: "user_group_links", Total: len(records)}

	for _, r := range records {
		id := shared.Int64Val(r, "linkid")
		userID := shared.Int64Val(r, "uid")
		groupID := shared.Int64Val(r, "groupid")

		if !dryRun && (!validUsers[userID] || !validGroups[groupID]) {
			shared.Logger.Warn("skip user_group_link: FK not found",
				"linkid", id, "user_id", userID, "group_id", groupID)
			sum.Skipped++
			continue
		}

		if dryRun {
			shared.Logger.Debug("dry-run: would insert user_group_link",
				"linkid", id, "user_id", userID, "group_id", groupID)
			sum.Inserted++
			continue
		}

		_, err := db.Exec(ctx, `
			INSERT INTO user_group_links (id, user_id, group_id, created_at, updated_at)
			VALUES ($1, $2, $3, now(), now())
			ON CONFLICT (user_id, group_id) DO NOTHING`,
			id, userID, groupID,
		)
		if err != nil {
			shared.Logger.Error("insert user_group_link failed",
				"linkid", id, "user_id", userID, "group_id", groupID, "error", err)
			sum.Errors++
			continue
		}
		sum.Inserted++
	}

	if !dryRun {
		if _, err := db.Exec(ctx,
			`SELECT setval(pg_get_serial_sequence('user_group_links','id'), coalesce(max(id),1)) FROM user_group_links`,
		); err != nil {
			shared.Logger.Warn("reset user_group_links sequence failed", "error", err)
		}
	}

	sum.Log()
	return nil
}
