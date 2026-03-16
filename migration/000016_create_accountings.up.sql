CREATE TABLE IF NOT EXISTS accountings (
    id                    BIGSERIAL     PRIMARY KEY,
    estate_id             BIGINT        NOT NULL REFERENCES estates(id)              ON DELETE RESTRICT,
    title_id              INTEGER       REFERENCES accounting_titles(title_id)       ON DELETE RESTRICT,
    title_name            VARCHAR(255),
    description           VARCHAR(255),
    income                INTEGER       NOT NULL DEFAULT 0,
    expenditure           INTEGER       NOT NULL DEFAULT 0,
    accounting_date       TIMESTAMPTZ   NOT NULL,
    payment_method        VARCHAR(255),
    counterparty          VARCHAR(255),
    tag                   VARCHAR(255),
    code                  VARCHAR(255),
    linked_resource_type  VARCHAR(50),
    linked_resource_id    BIGINT,
    cash_account_id       INTEGER,
    created_by_user_id    BIGINT        NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at            TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ   NOT NULL DEFAULT now(),
    deleted_at            TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_accountings_estate          ON accountings (estate_id);
CREATE INDEX IF NOT EXISTS idx_accountings_estate_date     ON accountings (estate_id, accounting_date);
CREATE INDEX IF NOT EXISTS idx_accountings_code            ON accountings (code);
CREATE INDEX IF NOT EXISTS idx_accountings_linked_resource ON accountings (linked_resource_type, linked_resource_id);
CREATE INDEX IF NOT EXISTS idx_accountings_estate_tag      ON accountings (estate_id, tag);
CREATE INDEX IF NOT EXISTS idx_accountings_estate_title    ON accountings (estate_id, title_id);
CREATE INDEX IF NOT EXISTS idx_accountings_deleted_at      ON accountings (deleted_at);

ALTER TABLE accountings
    ADD CONSTRAINT chk_accountings_income_expenditure
        CHECK (NOT (income > 0 AND expenditure > 0)),
    ADD CONSTRAINT chk_accountings_linked_resource_type
        CHECK (linked_resource_type IN ('rent', 'schedule') OR linked_resource_type IS NULL),
    ADD CONSTRAINT chk_accountings_linked_resource_pair
        CHECK (
            (linked_resource_type IS NULL AND linked_resource_id IS NULL) OR
            (linked_resource_type IS NOT NULL AND linked_resource_id IS NOT NULL)
        );
