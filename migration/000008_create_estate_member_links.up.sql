CREATE TABLE IF NOT EXISTS estate_member_links (
    id           BIGSERIAL    PRIMARY KEY,
    estate_id    BIGINT       NOT NULL REFERENCES estates(id) ON DELETE CASCADE,
    user_id      BIGINT       NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
    member_level VARCHAR(20)  NOT NULL DEFAULT 'readonly',
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_estate_member_links_pair   ON estate_member_links (estate_id, user_id);
CREATE        INDEX IF NOT EXISTS idx_estate_member_links_estate ON estate_member_links (estate_id);
CREATE        INDEX IF NOT EXISTS idx_estate_member_links_user   ON estate_member_links (user_id);

ALTER TABLE estate_member_links
    ADD CONSTRAINT chk_estate_member_links_member_level
    CHECK (member_level IN ('admin', 'readonly'));
