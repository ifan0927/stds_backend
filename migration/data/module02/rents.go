package module02

import (
	"context"
	"encoding/json"
	"fmt"
	"path/filepath"
	"strconv"

	"github.com/ifan0927/stds-backend/migration/data/shared"
	"github.com/jackc/pgx/v5/pgxpool"
)

var paymentMethodMap = map[string]string{
	"年繳": "yearly",
	"半年": "halfYearly",
	"季繳": "quarterly",
	"月繳": "monthly",
}

var renewalStatusMap = map[string]string{
	"":  "unset",
	"0": "no_renew",
	"1": "renew",
}

// MigrateRents reads input/02_estate_rent.json and inserts into rents.
// estate_id is resolved from rooms table. 9 orphan rents are skipped.
// termination_info keys are renamed to camelCase per schema.md.
func MigrateRents(ctx context.Context, db *pgxpool.Pool, inputDir string, dryRun bool) error {
	records, err := shared.ReadJSONL(filepath.Join(inputDir, "02_estate_rent.json"))
	if err != nil {
		return fmt.Errorf("read 02_estate_rent.json: %w", err)
	}

	roomToEstate := map[int64]int64{}
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
	}

	sum := &shared.Summary{Table: "rents", Total: len(records)}

	for _, r := range records {
		id := shared.Int64Val(r, "estate_rent_id")
		roomID := shared.Int64Val(r, "estate_room_id")

		var estateID int64
		if !dryRun {
			eid, ok := roomToEstate[roomID]
			if !ok {
				shared.Logger.Warn("skip rent: room not found (orphan)", "rent_id", id, "room_id", roomID)
				sum.Skipped++
				continue
			}
			estateID = eid
		}

		startDate := shared.StringVal(r, "estate_rent_start")
		endDate := shared.StringVal(r, "estate_rent_end")

		var earlyMoveInDate *string
		if d := shared.StringVal(r, "estate_rent_early"); d != "" && d != "0000-00-00" {
			earlyMoveInDate = &d
		}

		deposit := shared.Int64Val(r, "estate_rent_deposit")

		paymentMethod, ok := paymentMethodMap[shared.StringVal(r, "estate_rent_money")]
		if !ok {
			shared.Logger.Error("unknown payment method, skipping",
				"rent_id", id, "value", shared.StringVal(r, "estate_rent_money"))
			sum.Errors++
			continue
		}

		initialElectric, _ := strconv.ParseFloat(shared.StringVal(r, "estate_rent_electric"), 64)

		renewalStatus, ok := renewalStatusMap[shared.StringVal(r, "estate_rent_continue")]
		if !ok {
			renewalStatus = "unset"
		}

		note := shared.NullableString(shared.StringVal(r, "estate_rent_note"))
		petInfo := shared.NullableString(shared.StringVal(r, "estate_rent_pet"))

		status := "archived"
		if shared.StringVal(r, "estate_rent_enable") == "1" {
			status = "active"
		}

		// termination_info: rename keys from old to new
		var terminationInfo *string
		if raw := shared.StringVal(r, "estate_rent_stop"); raw != "" {
			var old map[string]any
			if err := json.Unmarshal([]byte(raw), &old); err == nil {
				newInfo := map[string]any{}
				if v, ok := old["reason"]; ok {
					newInfo["reason"] = v
				}
				if v, ok := old["date"]; ok {
					newInfo["terminationDate"] = v
				}
				if v, ok := old["uid"]; ok {
					newInfo["operatorUserId"] = v
				}
				if v, ok := old["last_electric"]; ok {
					newInfo["initialElectricReading"] = v
				}
				if v, ok := old["electric"]; ok {
					newInfo["finalElectricReading"] = v
				}
				if v, ok := old["electric_money"]; ok {
					newInfo["electricityCost"] = v
				}
				if v, ok := old["rent_deposit"]; ok {
					newInfo["depositRefund"] = v
				}
				if v, ok := old["refund_total"]; ok {
					newInfo["totalRefund"] = v
				}
				if v, ok := old["estate_user_name"]; ok {
					newInfo["primaryTenantName"] = v
				}
				if money, ok := old["money"].(map[string]any); ok {
					newInfo["additionalCharges"] = map[string]any{
						"damageFee":   money["lost"],
						"cleaningFee": money["clean"],
						"otherFee":    money["other"],
						"rentBack":    money["rent_back"],
					}
				}
				if b, err := json.Marshal(newInfo); err == nil {
					s := string(b)
					terminationInfo = &s
				}
			} else {
				shared.Logger.Warn("termination_info parse error", "rent_id", id, "error", err)
			}
		}

		if dryRun {
			shared.Logger.Debug("dry-run: would insert rent",
				"rent_id", id, "room_id", roomID, "status", status)
			sum.Inserted++
			continue
		}

		var terminationInfoJSON *[]byte
		if terminationInfo != nil {
			b := []byte(*terminationInfo)
			terminationInfoJSON = &b
		}

		_, err := db.Exec(ctx, `
			INSERT INTO rents (
				id, estate_id, room_id, start_date, end_date, early_move_in_date,
				deposit, payment_method, initial_electric_reading, renewal_status,
				note, pet_info, status, termination_info,
				created_at, updated_at, deleted_at
			) VALUES (
				$1, $2, $3, $4, $5, $6,
				$7, $8, $9, $10,
				$11, $12, $13, $14,
				now(), now(), NULL
			)
			ON CONFLICT (id) DO NOTHING`,
			id, estateID, roomID, startDate, endDate, earlyMoveInDate,
			deposit, paymentMethod, initialElectric, renewalStatus,
			note, petInfo, status, terminationInfoJSON,
		)
		if err != nil {
			shared.Logger.Error("insert rent failed", "rent_id", id, "error", err)
			sum.Errors++
			continue
		}
		sum.Inserted++
	}

	if !dryRun {
		if _, err := db.Exec(ctx,
			`SELECT setval(pg_get_serial_sequence('rents','id'), coalesce(max(id),1)) FROM rents`,
		); err != nil {
			shared.Logger.Warn("reset rents sequence failed", "error", err)
		}
	}

	sum.Log()
	return nil
}
