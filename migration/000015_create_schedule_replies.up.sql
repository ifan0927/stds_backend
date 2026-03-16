CREATE TABLE IF NOT EXISTS schedule_replies (
    id              BIGSERIAL    PRIMARY KEY,
    schedule_id     BIGINT       NOT NULL REFERENCES schedules(id) ON DELETE CASCADE,
    content         TEXT         NOT NULL,
    author_user_id  BIGINT       NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    replied_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_schedule_replies_schedule ON schedule_replies (schedule_id);
CREATE INDEX IF NOT EXISTS idx_schedule_replies_author   ON schedule_replies (author_user_id);
