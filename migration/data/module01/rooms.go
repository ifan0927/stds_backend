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

// MigrateRooms reads input/01_estate_room.json and inserts into rooms.
// Orphan rooms (estate_id not in estates) are skipped and logged.
func MigrateRooms(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) error {
	records, err := shared.ReadJSONL(filepath.Join(inputDir, "01_estate_room.json"))
	if err != nil {
		return fmt.Errorf("read 01_estate_room.json: %w", err)
	}

	// Load valid estate IDs
	validEstates := map[int64]bool{}
	if !dryRun {
		rows, err := db.Query(ctx, `SELECT id FROM estates`)
		if err != nil {
			return fmt.Errorf("load estates: %w", err)
		}
		defer rows.Close()
		for rows.Next() {
			var id int64
			if err := rows.Scan(&id); err != nil {
				return err
			}
			validEstates[id] = true
		}
	}

	sum := &shared.Summary{Table: "rooms", Total: len(records)}

	for _, r := range records {
		id := shared.Int64Val(r, "estate_room_id")
		estateID := shared.Int64Val(r, "estate_id")

		if !dryRun && !validEstates[estateID] {
			shared.Logger.Warn("skip orphan room", "estate_room_id", id, "estate_id", estateID)
			sum.Skipped++
			continue
		}

		roomNumber := shared.StringVal(r, "estate_room_title")
		storey := shared.NullableString(shared.StringVal(r, "estate_room_zone")) // zone = storey in old system
		roomType := shared.NullableString(shared.StringVal(r, "estate_room_type"))
		note := shared.NullableString(shared.StringVal(r, "estate_room_note"))

		var sizePtr *float64
		if v, ok := r["estate_room_size"]; ok && v != nil {
			if f, err := strconv.ParseFloat(fmt.Sprintf("%v", v), 64); err == nil {
				sizePtr = &f
			}
		}

		// facilities: JSON object, string values → int
		facilities := "{}"
		if raw := strings.TrimSpace(shared.StringVal(r, "estate_room_facility")); raw != "" && raw != "null" {
			var obj map[string]string
			if err := json.Unmarshal([]byte(raw), &obj); err != nil {
				shared.Logger.Warn("facilities parse error", "room_id", id, "error", err)
			} else {
				converted := make(map[string]int, len(obj))
				for k, v := range obj {
					n, _ := strconv.Atoi(v)
					converted[k] = n
				}
				b, _ := json.Marshal(converted)
				facilities = string(b)
			}
		}

		// prices: old keys → new keys, money "" → null, "0" → 0
		prices := "{}"
		if raw := strings.TrimSpace(shared.StringVal(r, "estate_room_price")); raw != "" && raw != "null" {
			var obj map[string]map[string]string
			if err := json.Unmarshal([]byte(raw), &obj); err != nil {
				shared.Logger.Warn("prices parse error", "room_id", id, "error", err)
			} else {
				keyMap := map[string]string{
					"年繳": "yearly",
					"半年": "halfYearly",
					"季繳": "quarterly",
					"月繳": "monthly",
				}
				converted := map[string]any{}
				for oldKey, newKey := range keyMap {
					if period, ok := obj[oldKey]; ok {
						moneyStr := period["money"]
						if moneyStr == "" {
							converted[newKey] = nil
						} else {
							n, err := strconv.Atoi(moneyStr)
							if err != nil {
								converted[newKey] = nil
							} else {
								converted[newKey] = n
							}
						}
					} else {
						converted[newKey] = nil
					}
				}
				b, _ := json.Marshal(converted)
				prices = string(b)
			}
		}

		if dryRun {
			shared.Logger.Debug("dry-run: would insert room", "room_id", id, "estate_id", estateID)
			sum.Inserted++
			continue
		}

		_, err := db.Exec(ctx, `
			INSERT INTO rooms (
				id, estate_id, room_number, storey, room_type, size_sqm,
				facilities, prices, note, sort_order, zone,
				created_at, updated_at, deleted_at
			) VALUES (
				$1, $2, $3, $4, $5, $6,
				$7::jsonb, $8::jsonb, $9, 0, NULL,
				now(), now(), NULL
			)
			ON CONFLICT (id) DO NOTHING`,
			id, estateID, roomNumber, storey, roomType, sizePtr,
			facilities, prices, note,
		)
		if err != nil {
			shared.Logger.Error("insert room failed", "room_id", id, "error", err)
			sum.Errors++
			continue
		}
		sum.Inserted++
	}

	if !dryRun {
		if _, err := db.Exec(ctx,
			`SELECT setval(pg_get_serial_sequence('rooms','id'), coalesce(max(id),1)) FROM rooms`,
		); err != nil {
			shared.Logger.Warn("reset rooms sequence failed", "error", err)
		}
	}

	sum.Skipped = sum.Total - sum.Inserted - sum.Errors
	sum.Log()
	return nil
}
