package seed

import (
	"context"
	"errors"
	"fmt"

	"github.com/ifan0927/stds-backend/migration/data/shared"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

// SeedEstate inserts the minimal development estate seed data:
// one estate (陽光大廈), three rooms across two zones, estate member
// profiles and links for alice (admin) and bob (readonly), and one
// facility memo. Idempotent: skips records that already exist.
func SeedEstate(ctx context.Context, db *pgxpool.Pool, dryRun bool) error {
	if dryRun {
		shared.Logger.Info("dry-run: would seed estate, rooms, member profiles, member links, facility memos")
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

	// Resolve alice and bob user IDs (must already exist from SeedAuth).
	var aliceID, bobID int64
	if err := tx.QueryRow(ctx, `SELECT id FROM users WHERE username = 'alice'`).Scan(&aliceID); err != nil {
		return fmt.Errorf("look up alice: %w", err)
	}
	if err := tx.QueryRow(ctx, `SELECT id FROM users WHERE username = 'bob'`).Scan(&bobID); err != nil {
		return fmt.Errorf("look up bob: %w", err)
	}

	// Insert estate — check by title first to stay idempotent without a
	// unique index on the column.
	estateID, err := upsertEstate(ctx, tx, aliceID)
	if err != nil {
		return err
	}
	shared.Logger.Info("seeded estate", "estate_id", estateID)

	// Insert rooms.
	roomCount, err := seedRooms(ctx, tx, estateID)
	if err != nil {
		return err
	}

	// Upsert estate_member_profiles for alice and bob.
	if err := seedMemberProfiles(ctx, tx, aliceID, bobID); err != nil {
		return err
	}

	// Upsert estate_member_links.
	if err := seedMemberLinks(ctx, tx, estateID, aliceID, bobID); err != nil {
		return err
	}

	// Upsert one facility memo.
	if _, err := tx.Exec(ctx, `
		INSERT INTO estate_facility_memos (estate_id, facility_name, memo, created_at, updated_at)
		VALUES ($1, '電梯', '每月定期保養，聯絡廠商：快速電梯 02-1234-5678', now(), now())
		ON CONFLICT (estate_id, facility_name) DO UPDATE
		SET memo = EXCLUDED.memo, updated_at = now()
	`, estateID); err != nil {
		return fmt.Errorf("upsert facility memo: %w", err)
	}

	if err := tx.Commit(ctx); err != nil {
		return fmt.Errorf("commit seed transaction: %w", err)
	}

	shared.Logger.Info("estate seed complete",
		"estate_id", estateID,
		"rooms", roomCount,
	)
	return nil
}

func upsertEstate(ctx context.Context, tx pgx.Tx, ownerUserID int64) (int64, error) {
	var id int64
	err := tx.QueryRow(ctx,
		`SELECT id FROM estates WHERE title = '陽光大廈' AND deleted_at IS NULL LIMIT 1`,
	).Scan(&id)
	if err == nil {
		shared.Logger.Info("estate already exists, skipping insert", "estate_id", id)
		return id, nil
	}
	if !errors.Is(err, pgx.ErrNoRows) {
		return 0, fmt.Errorf("check existing estate: %w", err)
	}

	if err := tx.QueryRow(ctx, `
		INSERT INTO estates (
			title, short_title, owner_user_id, owner_name, owner_email,
			address, phone,
			facilities, electricity_rate, electricity_billing_cycle, zones,
			created_at, updated_at
		) VALUES (
			'陽光大廈', '陽光', $1, '王大明', 'wang@example.com',
			'台北市大安區和平東路一段100號', '02-2345-6789',
			'["電梯","停車場"]'::jsonb, 4.5, 'bimonthly', '["A棟","B棟"]'::jsonb,
			now(), now()
		)
		RETURNING id
	`, ownerUserID).Scan(&id); err != nil {
		return 0, fmt.Errorf("insert estate: %w", err)
	}
	return id, nil
}

type seedRoom struct {
	roomNumber string
	storey     string
	roomType   string
	sizeSqm    float64
	facilities string
	prices     string
	zone       string
	sortOrder  int
}

var estateSeedRooms = []seedRoom{
	{"A101", "2F", "2房1廳", 25.5, `{"床組":1,"書桌":1,"冷氣":1}`, `{"monthly":15000}`, "A棟", 1},
	{"A102", "2F", "1房", 18.0, `{"床組":1,"冷氣":1}`, `{"monthly":10000}`, "A棟", 2},
	{"B201", "2F", "3房2廳", 40.0, `{"床組":3,"書桌":1,"冷氣":2}`, `{"monthly":20000,"yearly":220000}`, "B棟", 3},
}

func seedRooms(ctx context.Context, tx pgx.Tx, estateID int64) (int, error) {
	inserted := 0
	for _, r := range estateSeedRooms {
		var roomID int64
		// The partial unique index on (estate_id, room_number) WHERE deleted_at IS NULL
		// lets us use ON CONFLICT with the index predicate.
		err := tx.QueryRow(ctx, `
			INSERT INTO rooms (
				estate_id, room_number, storey, room_type, size_sqm,
				facilities, prices, zone, sort_order,
				created_at, updated_at
			) VALUES (
				$1, $2, $3, $4, $5,
				$6::jsonb, $7::jsonb, $8, $9,
				now(), now()
			)
			ON CONFLICT (estate_id, room_number) WHERE deleted_at IS NULL DO NOTHING
			RETURNING id
		`, estateID, r.roomNumber, r.storey, r.roomType, r.sizeSqm,
			r.facilities, r.prices, r.zone, r.sortOrder,
		).Scan(&roomID)
		if errors.Is(err, pgx.ErrNoRows) {
			shared.Logger.Info("room already exists, skipping", "room_number", r.roomNumber)
			continue
		}
		if err != nil {
			return inserted, fmt.Errorf("insert room %s: %w", r.roomNumber, err)
		}
		shared.Logger.Info("seeded room", "room_id", roomID, "room_number", r.roomNumber)
		inserted++
	}
	return inserted, nil
}

func seedMemberProfiles(ctx context.Context, tx pgx.Tx, aliceID, bobID int64) error {
	profiles := []struct {
		userID             int64
		unit, title        string
		textColor, bgColor string
	}{
		{aliceID, "管理部", "主承辦人", "#FFFFFF", "#6EB3E5"},
		{bobID, "業主", "業主代表", "#FFFFFF", "#F5A623"},
	}
	for _, p := range profiles {
		if _, err := tx.Exec(ctx, `
			INSERT INTO estate_member_profiles
				(user_id, unit, title, calendar_text_color, calendar_bg_color, created_at, updated_at)
			VALUES ($1, $2, $3, $4, $5, now(), now())
			ON CONFLICT (user_id) DO UPDATE
			SET unit               = EXCLUDED.unit,
			    title              = EXCLUDED.title,
			    calendar_text_color = EXCLUDED.calendar_text_color,
			    calendar_bg_color  = EXCLUDED.calendar_bg_color,
			    updated_at         = now()
		`, p.userID, p.unit, p.title, p.textColor, p.bgColor); err != nil {
			return fmt.Errorf("upsert member profile user_id=%d: %w", p.userID, err)
		}
		shared.Logger.Info("seeded member profile", "user_id", p.userID)
	}
	return nil
}

func seedMemberLinks(ctx context.Context, tx pgx.Tx, estateID, aliceID, bobID int64) error {
	links := []struct {
		userID      int64
		memberLevel string
	}{
		{aliceID, "admin"},
		{bobID, "readonly"},
	}
	for _, l := range links {
		if _, err := tx.Exec(ctx, `
			INSERT INTO estate_member_links (estate_id, user_id, member_level, created_at, updated_at)
			VALUES ($1, $2, $3, now(), now())
			ON CONFLICT (estate_id, user_id) DO UPDATE
			SET member_level = EXCLUDED.member_level,
			    updated_at   = now()
		`, estateID, l.userID, l.memberLevel); err != nil {
			return fmt.Errorf("upsert member link estate_id=%d user_id=%d: %w", estateID, l.userID, err)
		}
		shared.Logger.Info("seeded member link", "estate_id", estateID, "user_id", l.userID, "level", l.memberLevel)
	}
	return nil
}
