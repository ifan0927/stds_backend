package module02

import (
	"context"
	"fmt"
	"path/filepath"

	"github.com/ifan0927/stds-backend/migration/data/shared"
	"github.com/jackc/pgx/v5/pgxpool"
)

// MigrateGroups reads input/02_groups.json and inserts into groups.
// Source: xx_groups (6 rows).
// Field mapping: groupid→id, name, description, group_type.
func MigrateGroups(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) error {
	records, err := shared.ReadJSONL(filepath.Join(inputDir, "02_groups.json"))
	if err != nil {
		return fmt.Errorf("read 02_groups.json: %w", err)
	}

	sum := &shared.Summary{Table: "groups", Total: len(records)}

	for _, r := range records {
		id := shared.Int64Val(r, "groupid")
		name := shared.StringVal(r, "name")
		description := shared.NullableString(shared.StringVal(r, "description"))
		groupTypeRaw := shared.StringVal(r, "group_type")

		var groupType string
		switch groupTypeRaw {
		case "", "Admin", "User":
			groupType = "Global"
		case "Anonymous":
			groupType = "Anonymous"
		default:
			shared.Logger.Error("unknown group_type, skipped", "group_id", id, "group_type", groupTypeRaw)
			sum.Errors++
			continue
		}

		if dryRun {
			shared.Logger.Debug("dry-run: would insert group", "group_id", id, "name", name)
			sum.Inserted++
			continue
		}

		_, err := db.Exec(ctx, `
			INSERT INTO groups (id, name, description, group_type, created_at, updated_at)
			VALUES ($1, $2, $3, $4, now(), now())
			ON CONFLICT (id) DO NOTHING`,
			id, name, description, groupType,
		)
		if err != nil {
			shared.Logger.Error("insert group failed", "group_id", id, "error", err)
			sum.Errors++
			continue
		}
		sum.Inserted++
	}

	if !dryRun {
		if _, err := db.Exec(ctx,
			`SELECT setval(pg_get_serial_sequence('groups','id'), coalesce(max(id),1)) FROM groups`,
		); err != nil {
			shared.Logger.Warn("reset groups sequence failed", "error", err)
		}
	}

	sum.Log()
	return nil
}
