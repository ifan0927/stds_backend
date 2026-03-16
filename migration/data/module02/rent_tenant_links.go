package module02

import (
	"context"
	"fmt"
	"path/filepath"

	"github.com/ifan0927/stds-backend/migration/data/shared"
	"github.com/jackc/pgx/v5/pgxpool"
)

// MigrateRentTenantLinks reads input/02_estate_rent_user.json and inserts into rent_tenant_links.
// Source: xx_estate_rent_user (607 rows).
// Field mapping: estate_rent_id→rent_id, estate_user_id→tenant_id.
func MigrateRentTenantLinks(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) error {
	records, err := shared.ReadJSONL(filepath.Join(inputDir, "02_estate_rent_user.json"))
	if err != nil {
		return fmt.Errorf("read 02_estate_rent_user.json: %w", err)
	}

	validRents := map[int64]bool{}
	validTenants := map[int64]bool{}
	if !dryRun {
		rows, err := db.Query(ctx, `SELECT id FROM rents`)
		if err != nil {
			return fmt.Errorf("load rents: %w", err)
		}
		defer rows.Close()
		for rows.Next() {
			var id int64
			if err := rows.Scan(&id); err != nil {
				return err
			}
			validRents[id] = true
		}

		tRows, err := db.Query(ctx, `SELECT id FROM tenants`)
		if err != nil {
			return fmt.Errorf("load tenants: %w", err)
		}
		defer tRows.Close()
		for tRows.Next() {
			var id int64
			if err := tRows.Scan(&id); err != nil {
				return err
			}
			validTenants[id] = true
		}
	}

	sum := &shared.Summary{Table: "rent_tenant_links", Total: len(records)}

	for _, r := range records {
		rentID := shared.Int64Val(r, "estate_rent_id")
		tenantID := shared.Int64Val(r, "estate_user_id")

		if !dryRun && (!validRents[rentID] || !validTenants[tenantID]) {
			shared.Logger.Warn("skip rent_tenant_link: FK not found",
				"rent_id", rentID, "tenant_id", tenantID)
			sum.Skipped++
			continue
		}

		if dryRun {
			shared.Logger.Debug("dry-run: would insert rent_tenant_link",
				"rent_id", rentID, "tenant_id", tenantID)
			sum.Inserted++
			continue
		}

		_, err := db.Exec(ctx, `
			INSERT INTO rent_tenant_links (rent_id, tenant_id, created_at, updated_at)
			VALUES ($1, $2, now(), now())
			ON CONFLICT (rent_id, tenant_id) DO NOTHING`,
			rentID, tenantID,
		)
		if err != nil {
			shared.Logger.Error("insert rent_tenant_link failed",
				"rent_id", rentID, "tenant_id", tenantID, "error", err)
			sum.Errors++
			continue
		}
		sum.Inserted++
	}

	if !dryRun {
		if _, err := db.Exec(ctx,
			`SELECT setval(pg_get_serial_sequence('rent_tenant_links','id'), coalesce(max(id),1)) FROM rent_tenant_links`,
		); err != nil {
			shared.Logger.Warn("reset rent_tenant_links sequence failed", "error", err)
		}
	}

	sum.Log()
	return nil
}
