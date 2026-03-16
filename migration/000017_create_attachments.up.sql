CREATE TYPE attachment_resource_type AS ENUM (
    'room',
    'facility',
    'rent',
    'schedule',
    'schedule_reply',
    'estate'
);

CREATE TABLE IF NOT EXISTS attachments (
    id                    BIGSERIAL                  PRIMARY KEY,
    estate_id             BIGINT                     NOT NULL REFERENCES estates(id) ON DELETE CASCADE,
    resource_type         attachment_resource_type   NOT NULL,
    resource_id           BIGINT                     NOT NULL,
    file_name             VARCHAR(512)               NOT NULL,
    mime_type             VARCHAR(255)               NOT NULL,
    file_size             BIGINT                     NOT NULL,
    storage_object_path   VARCHAR(1024)              NOT NULL,
    description           TEXT,
    sort_order            INTEGER                    NOT NULL DEFAULT 0,
    download_count        INTEGER                    NOT NULL DEFAULT 0,
    tag                   VARCHAR(255),
    uploaded_by_user_id   BIGINT                     NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at            TIMESTAMPTZ                NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ                NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_attachments_estate        ON attachments (estate_id);
CREATE INDEX IF NOT EXISTS idx_attachments_resource      ON attachments (estate_id, resource_type, resource_id, sort_order);
CREATE INDEX IF NOT EXISTS idx_attachments_uploaded_by   ON attachments (uploaded_by_user_id);
CREATE INDEX IF NOT EXISTS idx_attachments_resource_type_id ON attachments (resource_type, resource_id);
