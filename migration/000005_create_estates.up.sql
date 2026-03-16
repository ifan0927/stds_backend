CREATE TABLE IF NOT EXISTS estates (
    id                         BIGSERIAL     PRIMARY KEY,
    title                      VARCHAR(255)  NOT NULL,
    short_title                VARCHAR(255)  NOT NULL,
    owner_user_id              BIGINT        REFERENCES users(id) ON DELETE SET NULL,
    owner_name                 VARCHAR(255)  NOT NULL,
    owner_email                VARCHAR(255),
    address                    VARCHAR(255),
    phone                      VARCHAR(255),
    website                    VARCHAR(255),
    facebook                   VARCHAR(255),
    note                       TEXT,
    facilities                 JSONB         NOT NULL DEFAULT '[]',
    electricity_rate           NUMERIC(6,2)  NOT NULL DEFAULT 4.50,
    electricity_billing_cycle  VARCHAR(20)   NOT NULL DEFAULT 'bimonthly',
    zones                      JSONB         NOT NULL DEFAULT '[]',
    created_at                 TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at                 TIMESTAMPTZ   NOT NULL DEFAULT now(),
    deleted_at                 TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_estates_owner_user ON estates (owner_user_id);
CREATE INDEX IF NOT EXISTS idx_estates_deleted_at ON estates (deleted_at);

ALTER TABLE estates
    ADD CONSTRAINT chk_estates_electricity_billing_cycle
    CHECK (electricity_billing_cycle IN ('monthly', 'bimonthly'));
