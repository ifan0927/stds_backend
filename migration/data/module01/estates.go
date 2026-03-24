package module01

import (
	"context"
	"encoding/json"
	"fmt"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/ifan0927/stds-backend/migration/data/shared"
	"github.com/jackc/pgx/v5/pgxpool"
)

// MigrateEstates reads input/01_estate.json and inserts into estates.
// FK owner_user_id is left NULL here; backfilled after users migration.
func MigrateEstates(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) error {
	records, err := shared.ReadJSONL(filepath.Join(inputDir, "01_estate.json"))
	if err != nil {
		return fmt.Errorf("read 01_estate.json: %w", err)
	}

	sum := &shared.Summary{Table: "estates", Total: len(records)}

	for _, r := range records {
		id := shared.Int64Val(r, "estate_id")

		title := shared.StringVal(r, "estate_title")
		shortTitle := shared.StringVal(r, "estate_stitle")

		// owner_name: fallback to title if empty
		ownerName := strings.TrimSpace(shared.StringVal(r, "estate_name"))
		if ownerName == "" {
			ownerName = title
			shared.Logger.Warn("estate_name empty, fallback to title", "estate_id", id)
		}

		ownerEmail := strings.TrimSpace(shared.StringVal(r, "estate_email"))
		if ownerEmail == "" {
			shared.Logger.Error("estate_email is required by current schema", "estate_id", id)
			sum.Errors++
			continue
		}
		address := shared.NullableString(shared.StringVal(r, "estate_addr"))
		phone := shared.NullableString(shared.StringVal(r, "estate_tel"))
		website := shared.NullableString(shared.StringVal(r, "estate_web"))
		facebook := shared.NullableString(shared.StringVal(r, "estate_fb"))
		note := shared.NullableString(shared.StringVal(r, "estate_note"))

		// facilities: JSON string array → JSONB
		facilities := "[]"
		if raw := strings.TrimSpace(shared.StringVal(r, "estate_facility")); raw != "" && raw != "null" {
			var parsed any
			if err := json.Unmarshal([]byte(raw), &parsed); err != nil {
				shared.Logger.Error("estate_facility parse error", "estate_id", id, "error", err)
			} else {
				facilities = raw
			}
		}

		// electricity_rate: NULL → 4.50
		electricityRate := 4.50
		if v, ok := r["electric_money"]; ok && v != nil {
			if f, err := strconv.ParseFloat(fmt.Sprintf("%v", v), 64); err == nil {
				electricityRate = f
			}
		}

		// electricity_billing_cycle: 單月→monthly, 雙月→bimonthly
		cycle := shared.StringVal(r, "electric_month")
		billingCycle := ""
		switch cycle {
		case "單月":
			billingCycle = "monthly"
		case "雙月":
			billingCycle = "bimonthly"
		default:
			shared.Logger.Error("unknown electric_month", "estate_id", id, "value", cycle)
			sum.Errors++
			continue
		}

		// zones: ';' split → JSONB array, empty → '[]'
		zones := "[]"
		if raw := strings.TrimSpace(shared.StringVal(r, "estate_zone")); raw != "" {
			parts := strings.Split(raw, ";")
			filtered := make([]string, 0, len(parts))
			for _, p := range parts {
				if p = strings.TrimSpace(p); p != "" {
					filtered = append(filtered, p)
				}
			}
			if len(filtered) > 0 {
				b, _ := json.Marshal(filtered)
				zones = string(b)
			}
		}
		shared.Logger.Info("estate zones", "estate_id", id, "zones", zones)

		if dryRun {
			shared.Logger.Debug("dry-run: would insert estate", "estate_id", id, "title", title)
			sum.Inserted++
			continue
		}

		_, err := db.Exec(ctx, `
			INSERT INTO estates (
				id, title, short_title, owner_user_id, owner_name, owner_email,
				address, phone, website, facebook, note,
				facilities, electricity_rate, electricity_billing_cycle, zones,
				created_at, updated_at, deleted_at
			) VALUES (
				$1, $2, $3, NULL, $4, $5,
				$6, $7, $8, $9, $10,
				$11::jsonb, $12, $13, $14::jsonb,
				now(), now(), NULL
			)
			ON CONFLICT (id) DO NOTHING`,
			id, title, shortTitle, ownerName, ownerEmail,
			address, phone, website, facebook, note,
			facilities, electricityRate, billingCycle, zones,
		)
		if err != nil {
			shared.Logger.Error("insert estate failed", "estate_id", id, "error", err)
			sum.Errors++
			continue
		}
		sum.Inserted++
	}

	// Reset sequence after backfill
	if !dryRun {
		if _, err := db.Exec(ctx,
			`SELECT setval(pg_get_serial_sequence('estates','id'), coalesce(max(id),1)) FROM estates`,
		); err != nil {
			shared.Logger.Warn("reset estates sequence failed", "error", err)
		}
	}

	sum.Skipped = sum.Total - sum.Inserted - sum.Errors
	sum.Log()
	return nil
}
