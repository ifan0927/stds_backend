CREATE TABLE IF NOT EXISTS schedules (
    id                 BIGSERIAL     PRIMARY KEY,
    estate_id          BIGINT        NOT NULL REFERENCES estates(id) ON DELETE RESTRICT,
    room_id            BIGINT        REFERENCES rooms(id) ON DELETE RESTRICT,
    scheduled_at       TIMESTAMPTZ   NOT NULL,
    kind               VARCHAR(255)  NOT NULL DEFAULT '',
    status             VARCHAR(255)  NOT NULL DEFAULT '',
    status_color       VARCHAR(20),
    content            TEXT          NOT NULL,
    reporter_user_id   BIGINT        NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    assist_user_id     BIGINT,
    created_at         TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ   NOT NULL DEFAULT now(),
    deleted_at         TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_schedules_estate           ON schedules (estate_id);
CREATE INDEX IF NOT EXISTS idx_schedules_estate_scheduled ON schedules (estate_id, scheduled_at DESC);
CREATE INDEX IF NOT EXISTS idx_schedules_estate_kind      ON schedules (estate_id, kind);
CREATE INDEX IF NOT EXISTS idx_schedules_estate_room      ON schedules (estate_id, room_id);
CREATE INDEX IF NOT EXISTS idx_schedules_deleted_at       ON schedules (deleted_at);

ALTER TABLE schedules
    ADD CONSTRAINT chk_schedules_assist_user_id
    CHECK (assist_user_id IS NULL OR assist_user_id >= 0);
