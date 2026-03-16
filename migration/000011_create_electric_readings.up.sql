CREATE TABLE IF NOT EXISTS electric_readings (
    id                   BIGSERIAL     PRIMARY KEY,
    estate_id            BIGINT        NOT NULL REFERENCES estates(id) ON DELETE RESTRICT,
    room_id              BIGINT        NOT NULL REFERENCES rooms(id)   ON DELETE RESTRICT,
    year                 SMALLINT      NOT NULL,
    month                SMALLINT      NOT NULL,
    degrees              NUMERIC(10,1) NOT NULL,
    recorded_by_user_id  BIGINT        REFERENCES users(id) ON DELETE SET NULL,
    created_at           TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_electric_readings_estate_room_ym
    ON electric_readings (estate_id, room_id, year, month);
CREATE INDEX IF NOT EXISTS idx_electric_readings_estate    ON electric_readings (estate_id);
CREATE INDEX IF NOT EXISTS idx_electric_readings_estate_ym ON electric_readings (estate_id, year, month);
CREATE INDEX IF NOT EXISTS idx_electric_readings_room      ON electric_readings (room_id);

ALTER TABLE electric_readings
    ADD CONSTRAINT chk_electric_readings_month   CHECK (month  BETWEEN 1 AND 12),
    ADD CONSTRAINT chk_electric_readings_year    CHECK (year   BETWEEN 2000 AND 9999),
    ADD CONSTRAINT chk_electric_readings_degrees CHECK (degrees >= 0);
