-- BigQuery schema setup for Legal Search & Legal-ai system
-- Run this in BigQuery to create the necessary tables

-- Create dataset (if it doesn't exist)
CREATE SCHEMA IF NOT EXISTS `legal_data`
OPTIONS(
  description="Legal cases and statutes data for Legal Search & Legal-ai chatbot"
);

-- Legal Cases Table
CREATE TABLE IF NOT EXISTS `legal_data.legal_cases` (
  case_id STRING NOT NULL,
  case_title STRING NOT NULL,
  court STRING,
  year INT64,
  citation_count INT64,
  articles STRING,  -- Comma-separated list
  sections STRING,  -- Comma-separated list
  summary STRING,
  full_text_url STRING,
  jurisdiction STRING,
  case_type STRING,
  parties STRING,
  judgment_date DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY year
CLUSTER BY jurisdiction, case_type
OPTIONS(
  description="Legal cases with metadata for retrieval and analysis"
);

-- Statutes Table
CREATE TABLE IF NOT EXISTS `legal_data.statutes` (
  statute_id STRING NOT NULL,
  act_name STRING NOT NULL,
  section_number STRING,
  section_title STRING,
  section_text STRING,
  jurisdiction STRING,
  effective_date DATE,
  related_cases STRING,  -- Comma-separated case IDs
  amendments STRING,  -- Comma-separated amendment IDs
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE_TRUNC(effective_date, YEAR)
CLUSTER BY jurisdiction, act_name
OPTIONS(
  description="Statutes, acts, and regulations for legal analysis"
);

-- Create indexes (BigQuery uses clustering instead)
-- The tables are already clustered by jurisdiction and other key fields

-- Sample data insertion (for testing)
-- INSERT INTO `legal_data.legal_cases` VALUES
-- ('CASE001', 'Justice K.S. Puttaswamy v. Union of India', 'Supreme Court of India', 2017, 540, 'Article 21', 'Section 43A IT Act', 'Landmark case on right to privacy', 'https://example.com/case001', 'India', 'Constitutional', 'K.S. Puttaswamy, Union of India', '2017-08-24');

