CREATE TABLE IF NOT EXISTS rooms (
    id          BIGSERIAL     PRIMARY KEY,
    estate_id   BIGINT        NOT NULL REFERENCES estates(id) ON DELETE RESTRICT,
    room_number VARCHAR(255)  NOT NULL,
    storey      VARCHAR(255),
    room_type   VARCHAR(255),
    size_sqm    NUMERIC(7,2),
    facilities  JSONB         NOT NULL DEFAULT '{}',
    prices      JSONB         NOT NULL DEFAULT '{}',
    note        TEXT,
    sort_order  INTEGER       NOT NULL DEFAULT 0,
    zone        VARCHAR(255),
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ   NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ
);

CREATE        INDEX IF NOT EXISTS idx_rooms_estate      ON rooms (estate_id);
CREATE        INDEX IF NOT EXISTS idx_rooms_estate_zone ON rooms (estate_id, zone);
CREATE        INDEX IF NOT EXISTS idx_rooms_estate_sort ON rooms (estate_id, sort_order);
CREATE UNIQUE INDEX IF NOT EXISTS idx_rooms_estate_room_number
    ON rooms (estate_id, room_number) WHERE deleted_at IS NULL;
