ALTER TABLE estate_member_links
    DROP CONSTRAINT IF EXISTS chk_estate_member_links_member_level;

ALTER TABLE estate_member_links
    ADD CONSTRAINT chk_estate_member_links_member_level
    CHECK (member_level IN ('admin', 'normal', 'readonly'));
