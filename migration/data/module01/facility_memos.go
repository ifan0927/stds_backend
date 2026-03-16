package module01

import (
	"context"
	"fmt"
	"path/filepath"
	"sort"
	"strings"

	"github.com/ifan0927/stds-backend/migration/data/shared"
	"github.com/jackc/pgx/v5/pgxpool"
)

type eavRow struct {
	mid      int64
	dataName string
	dataVal  string
	dataSort int64
}

// MigrateFacilityMemos reads 01_estate_data_center.json (EAV) and inserts into estate_facility_memos.
// Groups by (estate_id, col_name), sorts by (data_sort, mid), joins as "{data_name}：{data_value}".
func MigrateFacilityMemos(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) error {
	records, err := shared.ReadJSONL(filepath.Join(inputDir, "01_estate_data_center.json"))
	if err != nil {
		return fmt.Errorf("read 01_estate_data_center.json: %w", err)
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

	type groupKey struct {
		estateID     int64
		facilityName string
	}
	groups := map[groupKey][]eavRow{}

	skipped := 0
	for _, r := range records {
		estateID := shared.Int64Val(r, "col_id")
		facilityName := strings.TrimSpace(shared.StringVal(r, "col_name"))
		mid := shared.Int64Val(r, "mid")

		if !dryRun && !validEstates[estateID] {
			shared.Logger.Warn("skip facility_memo: estate not found", "col_id", estateID, "mid", mid)
			skipped++
			continue
		}
		if facilityName == "" {
			shared.Logger.Warn("skip facility_memo: empty col_name", "col_id", estateID, "mid", mid)
			skipped++
			continue
		}

		key := groupKey{estateID, facilityName}
		groups[key] = append(groups[key], eavRow{
			mid:      mid,
			dataName: shared.StringVal(r, "data_name"),
			dataVal:  shared.StringVal(r, "data_value"),
			dataSort: shared.Int64Val(r, "data_sort"),
		})
	}

	sum := &shared.Summary{Table: "estate_facility_memos", Total: len(groups), Skipped: skipped}

	for key, rows := range groups {
		sort.Slice(rows, func(i, j int) bool {
			if rows[i].dataSort != rows[j].dataSort {
				return rows[i].dataSort < rows[j].dataSort
			}
			return rows[i].mid < rows[j].mid
		})

		lines := make([]string, 0, len(rows))
		for _, row := range rows {
			lines = append(lines, row.dataName+"："+row.dataVal)
		}
		memo := strings.Join(lines, "\n")
		var memoPtr *string
		if memo != "" {
			memoPtr = &memo
		}

		if dryRun {
			shared.Logger.Debug("dry-run: would insert facility_memo",
				"estate_id", key.estateID, "facility_name", key.facilityName)
			sum.Inserted++
			continue
		}

		_, err := db.Exec(ctx, `
			INSERT INTO estate_facility_memos (estate_id, facility_name, memo, created_at, updated_at)
			VALUES ($1, $2, $3, now(), now())
			ON CONFLICT (estate_id, facility_name) DO NOTHING`,
			key.estateID, key.facilityName, memoPtr,
		)
		if err != nil {
			shared.Logger.Error("insert facility_memo failed",
				"estate_id", key.estateID, "facility_name", key.facilityName, "error", err)
			sum.Errors++
			continue
		}
		sum.Inserted++
	}

	sum.Log()
	return nil
}
