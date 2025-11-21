-- Strategic Match Database Schema Update
-- Adds tier system, date tracking, and search type classification

-- Add new columns
ALTER TABLE jobs ADD COLUMN tier INTEGER DEFAULT 3;
ALTER TABLE jobs ADD COLUMN date_added DATE DEFAULT CURRENT_DATE;
ALTER TABLE jobs ADD COLUMN search_type TEXT DEFAULT 'corporate';

-- Create indexes for fast filtering
CREATE INDEX IF NOT EXISTS idx_tier ON jobs(tier);
CREATE INDEX IF NOT EXISTS idx_date_added ON jobs(date_added);
CREATE INDEX IF NOT EXISTS idx_search_type ON jobs(search_type);

-- Update existing jobs with default date
UPDATE jobs SET date_added = CURRENT_DATE WHERE date_added IS NULL;
UPDATE jobs SET search_type = CASE 
    WHEN job_type = 'Corporate' THEN 'corporate'
    WHEN job_type = 'Nonprofit' THEN 'nonprofit'
    ELSE 'corporate'
END WHERE search_type = 'corporate';
