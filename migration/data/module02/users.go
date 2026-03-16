package module02

import (
	"context"
	"fmt"
	"path/filepath"
	"strconv"
	"time"

	"github.com/ifan0927/stds-backend/migration/data/shared"
	"github.com/jackc/pgx/v5/pgxpool"
)

// MigrateUsers reads input/02_users.json and inserts into users.
// Source: xx_users (24 rows).
// Note: password hashes are kept as-is (bcrypt $2y$ → compatible with Go's bcrypt).
// Users must reset passwords on first login (MD5 hashes are not accepted, bcrypt ones are kept).
// level any non-zero value → is_enabled=true; '0' → false.
func MigrateUsers(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) error {
	records, err := shared.ReadJSONL(filepath.Join(inputDir, "02_users.json"))
	if err != nil {
		return fmt.Errorf("read 02_users.json: %w", err)
	}

	sum := &shared.Summary{Table: "users", Total: len(records)}

	for _, r := range records {
		id := shared.Int64Val(r, "uid")
		username := shared.StringVal(r, "uname")
		name := shared.StringVal(r, "name")
		email := shared.StringVal(r, "email")
		passwordHash := shared.StringVal(r, "pass")
		occupation := shared.NullableString(shared.StringVal(r, "user_occ"))
		bio := shared.NullableString(shared.StringVal(r, "bio"))
		avatarPath := shared.NullableString(shared.StringVal(r, "user_avatar"))

		// level: '0' = disabled, anything else = enabled
		isEnabled := shared.StringVal(r, "level") != "0"

		// last_login: unix timestamp string → TIMESTAMPTZ (NULL if 0 or empty)
		var lastLoginAt *time.Time
		if ts := shared.Int64Val(r, "last_login"); ts > 0 {
			t := time.Unix(ts, 0).UTC()
			lastLoginAt = &t
		}

		// user_regdate: unix timestamp string → created_at
		createdAt := time.Now().UTC()
		if ts := shared.Int64Val(r, "user_regdate"); ts > 0 {
			createdAt = time.Unix(ts, 0).UTC()
		}

		if dryRun {
			shared.Logger.Debug("dry-run: would insert user",
				"user_id", id, "username", username, "is_enabled", isEnabled)
			sum.Inserted++
			continue
		}

		_, err := db.Exec(ctx, `
			INSERT INTO users (
				id, username, name, email, password_hash,
				occupation, bio, avatar_path, is_enabled,
				last_login_at, created_at, updated_at, deleted_at
			) VALUES (
				$1, $2, $3, $4, $5,
				$6, $7, $8, $9,
				$10, $11, now(), NULL
			)
			ON CONFLICT (id) DO NOTHING`,
			id, username, name, email, passwordHash,
			occupation, bio, avatarPath, isEnabled,
			lastLoginAt, createdAt,
		)
		if err != nil {
			shared.Logger.Error("insert user failed", "user_id", id, "username", username, "error", err)
			sum.Errors++
			continue
		}
		sum.Inserted++
	}

	if !dryRun {
		if _, err := db.Exec(ctx,
			`SELECT setval(pg_get_serial_sequence('users','id'), coalesce(max(id),1)) FROM users`,
		); err != nil {
			shared.Logger.Warn("reset users sequence failed", "error", err)
		}
	}

	sum.Log()
	return nil
}

// unused import guard
var _ = strconv.Itoa
