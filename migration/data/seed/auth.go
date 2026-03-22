package seed

import (
	"context"
	"fmt"
	"time"

	"github.com/ifan0927/stds-backend/migration/data/shared"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"golang.org/x/crypto/bcrypt"
)

type authSeedUser struct {
	Username  string
	Name      string
	Email     string
	Password  string
	Role      string
	GroupName string
}

var authSeedUsers = []authSeedUser{
	{
		Username:  "alice",
		Name:      "Alice Admin",
		Email:     "alice@example.com",
		Password:  "secret123",
		Role:      "admin",
		GroupName: "Administrators",
	},
	{
		Username:  "bob",
		Name:      "Bob Member",
		Email:     "bob@example.com",
		Password:  "secret123",
		Role:      "user",
		GroupName: "Members",
	},
}

// SeedAuth inserts the minimal development auth seed data.
func SeedAuth(ctx context.Context, db *pgxpool.Pool, dryRun bool) error {
	if dryRun {
		for _, user := range authSeedUsers {
			shared.Logger.Info("dry-run: would seed auth user",
				"username", user.Username,
				"role", user.Role,
				"group", user.GroupName,
			)
		}
		return nil
	}
	if db == nil {
		return fmt.Errorf("db is required")
	}

	tx, err := db.BeginTx(ctx, pgx.TxOptions{})
	if err != nil {
		return fmt.Errorf("begin seed transaction: %w", err)
	}
	defer tx.Rollback(ctx)

	now := time.Now().UTC()

	for _, user := range authSeedUsers {
		groupID, err := upsertGroup(ctx, tx, user.GroupName)
		if err != nil {
			return err
		}

		passwordHash, err := bcrypt.GenerateFromPassword([]byte(user.Password), bcrypt.DefaultCost)
		if err != nil {
			return fmt.Errorf("hash password for %s: %w", user.Username, err)
		}

		userID, err := upsertUser(ctx, tx, user, string(passwordHash), now)
		if err != nil {
			return err
		}

		if err := upsertUserGroupLink(ctx, tx, userID, groupID); err != nil {
			return err
		}

		shared.Logger.Info("seeded auth user",
			"username", user.Username,
			"role", user.Role,
			"group", user.GroupName,
		)
	}

	if _, err := tx.Exec(ctx, `SELECT setval(pg_get_serial_sequence('groups','id'), coalesce(max(id), 1)) FROM groups`); err != nil {
		return fmt.Errorf("reset groups sequence: %w", err)
	}
	if _, err := tx.Exec(ctx, `SELECT setval(pg_get_serial_sequence('users','id'), coalesce(max(id), 1)) FROM users`); err != nil {
		return fmt.Errorf("reset users sequence: %w", err)
	}
	if _, err := tx.Exec(ctx, `SELECT setval(pg_get_serial_sequence('user_group_links','id'), coalesce(max(id), 1)) FROM user_group_links`); err != nil {
		return fmt.Errorf("reset user_group_links sequence: %w", err)
	}

	if err := tx.Commit(ctx); err != nil {
		return fmt.Errorf("commit seed transaction: %w", err)
	}

	shared.Logger.Info("auth seed complete", "users", len(authSeedUsers))
	return nil
}

func upsertGroup(ctx context.Context, tx pgx.Tx, name string) (int64, error) {
	const query = `
		INSERT INTO groups (name, description, group_type, created_at, updated_at, deleted_at)
		VALUES ($1, $2, 'Global', now(), now(), NULL)
		ON CONFLICT (name) DO UPDATE
		SET description = EXCLUDED.description,
			group_type = EXCLUDED.group_type,
			updated_at = now(),
			deleted_at = NULL
		RETURNING id
	`

	var groupID int64
	description := fmt.Sprintf("Development auth seed group for %s", name)
	if err := tx.QueryRow(ctx, query, name, description).Scan(&groupID); err != nil {
		return 0, fmt.Errorf("upsert group %s: %w", name, err)
	}

	return groupID, nil
}

func upsertUser(ctx context.Context, tx pgx.Tx, user authSeedUser, passwordHash string, now time.Time) (int64, error) {
	const query = `
		INSERT INTO users (
			username, name, email, password_hash,
			role, is_enabled, last_login_at, created_at, updated_at, deleted_at, password_changed_at
		) VALUES (
			$1, $2, $3, $4,
			$5, TRUE, NULL, $6, $6, NULL, $6
		)
		ON CONFLICT (username) DO UPDATE
		SET name = EXCLUDED.name,
			email = EXCLUDED.email,
			password_hash = EXCLUDED.password_hash,
			role = EXCLUDED.role,
			is_enabled = EXCLUDED.is_enabled,
			deleted_at = NULL,
			password_changed_at = EXCLUDED.password_changed_at,
			updated_at = now()
		RETURNING id
	`

	var userID int64
	if err := tx.QueryRow(
		ctx,
		query,
		user.Username,
		user.Name,
		user.Email,
		passwordHash,
		user.Role,
		now,
	).Scan(&userID); err != nil {
		return 0, fmt.Errorf("upsert user %s: %w", user.Username, err)
	}

	return userID, nil
}

func upsertUserGroupLink(ctx context.Context, tx pgx.Tx, userID, groupID int64) error {
	const query = `
		INSERT INTO user_group_links (user_id, group_id, created_at, updated_at)
		VALUES ($1, $2, now(), now())
		ON CONFLICT (user_id, group_id) DO UPDATE
		SET updated_at = now()
	`

	if _, err := tx.Exec(ctx, query, userID, groupID); err != nil {
		return fmt.Errorf("upsert user_group_link user_id=%d group_id=%d: %w", userID, groupID, err)
	}

	return nil
}
