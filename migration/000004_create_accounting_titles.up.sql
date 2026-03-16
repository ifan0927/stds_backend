CREATE TABLE IF NOT EXISTS accounting_titles (
    id         BIGSERIAL     PRIMARY KEY,
    title_id   INTEGER       NOT NULL,
    kind       VARCHAR(10)   NOT NULL,
    title      VARCHAR(255)  NOT NULL,
    created_at TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_accounting_titles_title_id ON accounting_titles (title_id);
CREATE        INDEX IF NOT EXISTS idx_accounting_titles_kind     ON accounting_titles (kind);

ALTER TABLE accounting_titles
    ADD CONSTRAINT chk_accounting_titles_kind
    CHECK (kind IN ('expense', 'income'));

-- Seed data: 科目清單 (120 筆)
-- TODO: 在此加入 INSERT 科目 seed data
