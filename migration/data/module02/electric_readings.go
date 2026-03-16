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

// MigrateElectricReadings reads input/02_estate_electric.json and inserts into electric_readings.
// Source: xx_estate_electric (6286 rows).
// estate_id is resolved from rooms table (room_id → estate_id).
// recorded_by_user_id: set NULL if user not found in users table.
func MigrateElectricReadings(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) error {
	records, err := shared.ReadJSONL(filepath.Join(inputDir, "02_estate_electric.json"))
	if err != nil {
		return fmt.Errorf("read 02_estate_electric.json: %w", err)
	}

	// Build room_id → estate_id map
	roomToEstate := map[int64]int64{}
	validUsers := map[int64]bool{}
	if !dryRun {
		rows, err := db.Query(ctx, `SELECT id, estate_id FROM rooms`)
		if err != nil {
			return fmt.Errorf("load rooms: %w", err)
		}
		defer rows.Close()
		for rows.Next() {
			var roomID, estateID int64
			if err := rows.Scan(&roomID, &estateID); err != nil {
				return err
			}
			roomToEstate[roomID] = estateID
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

	sum := &shared.Summary{Table: "electric_readings", Total: len(records)}

	for _, r := range records {
		roomID := shared.Int64Val(r, "estate_room_id")

		var estateID int64
		if !dryRun {
			eid, ok := roomToEstate[roomID]
			if !ok {
				shared.Logger.Warn("skip electric_reading: room not found", "room_id", roomID)
				sum.Skipped++
				continue
			}
			estateID = eid
		}

		yearStr := shared.StringVal(r, "estate_electric_year")
		monthStr := shared.StringVal(r, "estate_electric_month")
		degreesStr := shared.StringVal(r, "estate_electric_degrees")

		year, _ := strconv.ParseInt(yearStr, 10, 16)
		month, _ := strconv.ParseInt(monthStr, 10, 16)
		degrees, _ := strconv.ParseFloat(degreesStr, 64)

		// recorded_by_user_id: NULL if not found
		var recordedByUserID *int64
		if uid := shared.Int64Val(r, "estate_electric_uid"); uid > 0 {
			if dryRun || validUsers[uid] {
				recordedByUserID = &uid
			}
		}

		// estate_electric_update: DATETIME → TIMESTAMPTZ
		updatedAt := time.Now().UTC()
		if ts := shared.StringVal(r, "estate_electric_update"); ts != "" && ts != "0000-00-00 00:00:00" {
			if t, err := time.ParseInLocation("2006-01-02 15:04:05", ts, time.UTC); err == nil {
				updatedAt = t
			}
		}

		if dryRun {
			shared.Logger.Debug("dry-run: would insert electric_reading",
				"room_id", roomID, "year", year, "month", month)
			sum.Inserted++
			continue
		}

		_, err := db.Exec(ctx, `
			INSERT INTO electric_readings (
				estate_id, room_id, year, month, degrees,
				recorded_by_user_id, created_at, updated_at
			) VALUES ($1, $2, $3, $4, $5, $6, now(), $7)
			ON CONFLICT (estate_id, room_id, year, month) DO UPDATE
				SET degrees = EXCLUDED.degrees,
				    recorded_by_user_id = EXCLUDED.recorded_by_user_id,
				    updated_at = EXCLUDED.updated_at`,
			estateID, roomID, year, month, degrees,
			recordedByUserID, updatedAt,
		)
		if err != nil {
			shared.Logger.Error("insert electric_reading failed",
				"room_id", roomID, "year", year, "month", month, "error", err)
			sum.Errors++
			continue
		}
		sum.Inserted++
	}

	sum.Log()
	return nil
}
