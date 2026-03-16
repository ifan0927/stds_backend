CREATE TABLE IF NOT EXISTS users (
    id             BIGSERIAL     PRIMARY KEY,
    username       VARCHAR(25)   NOT NULL,
    name           VARCHAR(60)   NOT NULL,
    email          VARCHAR(60)   NOT NULL,
    password_hash  VARCHAR(255)  NOT NULL,
    occupation     VARCHAR(100),
    bio            TEXT,
    avatar_path    VARCHAR(255),
    is_enabled     BOOLEAN       NOT NULL DEFAULT TRUE,
    last_login_at  TIMESTAMPTZ,
    created_at     TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ   NOT NULL DEFAULT now(),
    deleted_at     TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username   ON users (username);
CREATE        INDEX IF NOT EXISTS idx_users_email      ON users (email);
CREATE        INDEX IF NOT EXISTS idx_users_is_enabled ON users (is_enabled);
CREATE        INDEX IF NOT EXISTS idx_users_deleted_at ON users (deleted_at);
