# Firestore Setup Guide

Since your data is already in Firebase/Firestore, the system now supports Firestore as the primary data source!

## Quick Setup

### 1. Update Configuration

In your `.env` file, set:

```env
DATA_SOURCE=firestore
GCP_PROJECT_ID=your-project-id
```

The system will automatically use Firestore instead of BigQuery.

### 2. Firestore Collection Structure

Your Firestore collections should be named:
- `legal_cases` - for legal cases
- `statutes` - for statutes/acts

### 3. Document Structure

**Legal Cases Collection (`legal_cases`):**

Each document should have these fields:
```json
{
  "case_title": "Justice K.S. Puttaswamy v. Union of India",
  "court": "Supreme Court of India",
  "year": 2017,
  "citation_count": 540,
  "articles": "Article 21",
  "sections": "Section 43A IT Act",
  "summary": "Landmark case on right to privacy",
  "full_text_url": "https://example.com/case001",
  "jurisdiction": "India",
  "case_type": "Constitutional",
  "parties": "K.S. Puttaswamy, Union of India",
  "judgment_date": "2017-08-24"
}
```

**Statutes Collection (`statutes`):**

Each document should have these fields:
```json
{
  "act_name": "Information Technology Act",
  "section_number": "43A",
  "section_title": "Compensation for failure to protect data",
  "section_text": "Where a body corporate...",
  "jurisdiction": "India",
  "effective_date": "2000-10-17",
  "related_cases": "CASE001,CASE002",
  "amendments": ""
}
```

## Using Firestore

The system will automatically:
- Query Firestore collections
- Search by topic/keywords in title, summary, articles, sections
- Filter by jurisdiction
- Sort by citation count and year

## Migration to BigQuery (Optional)

If you want to migrate your Firestore data to BigQuery later:

```bash
# Migrate cases
python migrate_firestore_to_bigquery.py cases

# Migrate statutes
python migrate_firestore_to_bigquery.py statutes

# Migrate both
python migrate_firestore_to_bigquery.py all
```

Then update `.env`:
```env
DATA_SOURCE=bigquery
```

## Benefits of Using Firestore

✅ **Already have data there** - No migration needed
✅ **Real-time updates** - Changes reflect immediately
✅ **Flexible schema** - Easy to add new fields
✅ **Integrated with Firebase** - If you're using other Firebase services

## Benefits of Using BigQuery

✅ **Better for analytics** - SQL queries, aggregations
✅ **Handles large datasets** - Better for millions of records
✅ **Partitioning & clustering** - Optimized for queries
✅ **Cost-effective** - For large-scale data

## Switching Between Data Sources

Simply change `DATA_SOURCE` in `.env`:
- `DATA_SOURCE=firestore` - Use Firestore
- `DATA_SOURCE=bigquery` - Use BigQuery

No code changes needed! The system automatically adapts.

