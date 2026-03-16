CREATE TABLE IF NOT EXISTS estate_facility_memos (
    id            BIGSERIAL     PRIMARY KEY,
    estate_id     BIGINT        NOT NULL REFERENCES estates(id) ON DELETE CASCADE,
    facility_name VARCHAR(255)  NOT NULL,
    memo          TEXT,
    created_at    TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_facility_memos_estate_name ON estate_facility_memos (estate_id, facility_name);
CREATE        INDEX IF NOT EXISTS idx_facility_memos_estate      ON estate_facility_memos (estate_id);
