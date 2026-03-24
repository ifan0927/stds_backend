ALTER TABLE estate_member_links
    DROP CONSTRAINT IF EXISTS chk_estate_member_links_member_level;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM estate_member_links
        WHERE member_level = 'normal'
    ) THEN
        RAISE EXCEPTION 'cannot downgrade estate_member_links.member_level while rows with level=normal exist';
    END IF;
END $$;

ALTER TABLE estate_member_links
    ADD CONSTRAINT chk_estate_member_links_member_level
    CHECK (member_level IN ('admin', 'readonly'));
