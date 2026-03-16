CREATE TABLE IF NOT EXISTS estate_member_profiles (
    user_id              BIGINT       NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    unit                 VARCHAR(255),
    title                VARCHAR(255),
    calendar_text_color  VARCHAR(7)   NOT NULL DEFAULT '#FFFFFF',
    calendar_bg_color    VARCHAR(7)   NOT NULL DEFAULT '#6EB3E5',
    created_at           TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ  NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id)
);
