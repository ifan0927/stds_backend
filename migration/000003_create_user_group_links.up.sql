CREATE TABLE IF NOT EXISTS user_group_links (
    id         BIGSERIAL    PRIMARY KEY,
    user_id    BIGINT       NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
    group_id   BIGINT       NOT NULL REFERENCES groups(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_group_links_pair  ON user_group_links (user_id, group_id);
CREATE        INDEX IF NOT EXISTS idx_user_group_links_group ON user_group_links (group_id);
CREATE        INDEX IF NOT EXISTS idx_user_group_links_user  ON user_group_links (user_id);
