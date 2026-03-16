package module02

import (
	"context"
	"fmt"
	"path/filepath"

	"github.com/ifan0927/stds-backend/migration/data/shared"
	"github.com/jackc/pgx/v5/pgxpool"
)

// MigrateTenants reads input/02_estate_user.json and inserts into tenants.
// Source: xx_estate_user (608 rows).
// birthday '0000-00-00' → NULL.
func MigrateTenants(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) error {
	records, err := shared.ReadJSONL(filepath.Join(inputDir, "02_estate_user.json"))
	if err != nil {
		return fmt.Errorf("read 02_estate_user.json: %w", err)
	}

	sum := &shared.Summary{Table: "tenants", Total: len(records)}

	for _, r := range records {
		id := shared.Int64Val(r, "estate_user_id")
		name := shared.StringVal(r, "estate_user_name")

		var birthday *string
		if b := shared.StringVal(r, "estate_user_birthday"); b != "" && b != "0000-00-00" {
			birthday = &b
		}

		nationalID := shared.NullableString(shared.StringVal(r, "estate_user_pid"))
		registeredAddress := shared.NullableString(shared.StringVal(r, "estate_user_addr"))
		phone := shared.NullableString(shared.StringVal(r, "estate_user_tel"))
		occupation := shared.NullableString(shared.StringVal(r, "estate_user_job"))
		emergencyContact := shared.NullableString(shared.StringVal(r, "estate_user_contact"))
		email := shared.NullableString(shared.StringVal(r, "estate_user_email"))
		note := shared.NullableString(shared.StringVal(r, "estate_user_note"))

		if dryRun {
			shared.Logger.Debug("dry-run: would insert tenant", "tenant_id", id, "name", name)
			sum.Inserted++
			continue
		}

		_, err := db.Exec(ctx, `
			INSERT INTO tenants (
				id, name, birthday, national_id, registered_address,
				phone, occupation, emergency_contact, email, note,
				created_at, updated_at, deleted_at
			) VALUES (
				$1, $2, $3, $4, $5,
				$6, $7, $8, $9, $10,
				now(), now(), NULL
			)
			ON CONFLICT (id) DO NOTHING`,
			id, name, birthday, nationalID, registeredAddress,
			phone, occupation, emergencyContact, email, note,
		)
		if err != nil {
			shared.Logger.Error("insert tenant failed", "tenant_id", id, "error", err)
			sum.Errors++
			continue
		}
		sum.Inserted++
	}

	if !dryRun {
		if _, err := db.Exec(ctx,
			`SELECT setval(pg_get_serial_sequence('tenants','id'), coalesce(max(id),1)) FROM tenants`,
		); err != nil {
			shared.Logger.Warn("reset tenants sequence failed", "error", err)
		}
	}

	sum.Log()
	return nil
}
