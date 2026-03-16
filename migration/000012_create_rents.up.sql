CREATE TABLE IF NOT EXISTS rents (
    id                        BIGSERIAL      PRIMARY KEY,
    estate_id                 BIGINT         NOT NULL REFERENCES estates(id) ON DELETE RESTRICT,
    room_id                   BIGINT         NOT NULL REFERENCES rooms(id)   ON DELETE RESTRICT,
    start_date                DATE           NOT NULL,
    end_date                  DATE           NOT NULL,
    early_move_in_date        DATE,
    deposit                   NUMERIC(10,0)  NOT NULL DEFAULT 0,
    payment_method            VARCHAR(20)    NOT NULL,
    initial_electric_reading  NUMERIC(10,1)  NOT NULL DEFAULT 0.0,
    renewal_status            VARCHAR(20)    NOT NULL DEFAULT 'unset',
    note                      TEXT,
    pet_info                  VARCHAR(255),
    status                    VARCHAR(20)    NOT NULL DEFAULT 'active',
    termination_info          JSONB,
    created_at                TIMESTAMPTZ    NOT NULL DEFAULT now(),
    updated_at                TIMESTAMPTZ    NOT NULL DEFAULT now(),
    deleted_at                TIMESTAMPTZ
);

CREATE        INDEX IF NOT EXISTS idx_rents_estate        ON rents (estate_id);
CREATE        INDEX IF NOT EXISTS idx_rents_estate_status ON rents (estate_id, status);
CREATE        INDEX IF NOT EXISTS idx_rents_room          ON rents (room_id);
CREATE        INDEX IF NOT EXISTS idx_rents_estate_room_active
    ON rents (estate_id, room_id) WHERE status = 'active' AND deleted_at IS NULL;

ALTER TABLE rents
    ADD CONSTRAINT chk_rents_payment_method
        CHECK (payment_method IN ('yearly', 'halfYearly', 'quarterly', 'monthly')),
    ADD CONSTRAINT chk_rents_renewal_status
        CHECK (renewal_status IN ('unset', 'renew', 'no_renew')),
    ADD CONSTRAINT chk_rents_status
        CHECK (status IN ('active', 'archived')),
    ADD CONSTRAINT chk_rents_dates
        CHECK (end_date > start_date),
    ADD CONSTRAINT chk_rents_early_move_in
        CHECK (early_move_in_date IS NULL OR early_move_in_date <= start_date);
