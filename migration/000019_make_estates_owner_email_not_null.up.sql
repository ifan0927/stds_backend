DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM estates
        WHERE owner_email IS NULL
    ) THEN
        RAISE EXCEPTION 'cannot set estates.owner_email NOT NULL: found rows with NULL owner_email';
    END IF;
END $$;

ALTER TABLE estates
    ALTER COLUMN owner_email SET NOT NULL;
