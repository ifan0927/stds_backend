CREATE TABLE IF NOT EXISTS rent_tenant_links (
    id         BIGSERIAL    PRIMARY KEY,
    rent_id    BIGINT       NOT NULL REFERENCES rents(id)   ON DELETE CASCADE,
    tenant_id  BIGINT       NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_rent_tenant_links_pair   ON rent_tenant_links (rent_id, tenant_id);
CREATE        INDEX IF NOT EXISTS idx_rent_tenant_links_rent   ON rent_tenant_links (rent_id);
CREATE        INDEX IF NOT EXISTS idx_rent_tenant_links_tenant ON rent_tenant_links (tenant_id);
