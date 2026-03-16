CREATE TABLE IF NOT EXISTS groups (
    id          BIGSERIAL    PRIMARY KEY,
    name        VARCHAR(50)  NOT NULL,
    description TEXT,
    group_type  VARCHAR(20)  NOT NULL DEFAULT 'Global',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    deleted_at  TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_groups_name      ON groups (name);
CREATE        INDEX IF NOT EXISTS idx_groups_group_type ON groups (group_type);
CREATE        INDEX IF NOT EXISTS idx_groups_deleted_at ON groups (deleted_at);

ALTER TABLE groups
    ADD CONSTRAINT chk_groups_group_type
    CHECK (group_type IN ('Global', 'Anonymous'));
