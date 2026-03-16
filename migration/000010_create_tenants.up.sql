CREATE TABLE IF NOT EXISTS tenants (
    id                   BIGSERIAL     PRIMARY KEY,
    name                 VARCHAR(255)  NOT NULL,
    birthday             DATE,
    national_id          VARCHAR(255),
    registered_address   VARCHAR(255),
    phone                VARCHAR(255),
    occupation           VARCHAR(255),
    emergency_contact    VARCHAR(255),
    email                VARCHAR(255),
    note                 TEXT,
    created_at           TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ   NOT NULL DEFAULT now(),
    deleted_at           TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_tenants_name       ON tenants (name);
CREATE INDEX IF NOT EXISTS idx_tenants_deleted_at ON tenants (deleted_at);
