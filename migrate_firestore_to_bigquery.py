"""Script to migrate data from Firestore to BigQuery (optional)."""
from google.cloud import firestore
from google.cloud import bigquery
from config import settings
from utils.logger import setup_logger
import sys

logger = setup_logger(__name__)


def migrate_cases():
    """Migrate cases from Firestore to BigQuery."""
    try:
        # Initialize Firestore client
        db = firestore.Client(project=settings.gcp_project_id)
        cases_ref = db.collection("legal_cases")
        
        # Initialize BigQuery client
        bq_client = bigquery.Client(project=settings.gcp_project_id)
        table_id = f"{settings.gcp_project_id}.{settings.bigquery_dataset}.{settings.bigquery_case_table}"
        
        # Get all cases from Firestore
        logger.info("Fetching cases from Firestore...")
        firestore_cases = cases_ref.stream()
        
        rows_to_insert = []
        count = 0
        
        for doc in firestore_cases:
            case_data = doc.to_dict()
            case_id = doc.id
            
            # Format for BigQuery
            row = {
                "case_id": case_id,
                "case_title": case_data.get("case_title", ""),
                "court": case_data.get("court", ""),
                "year": case_data.get("year"),
                "citation_count": case_data.get("citation_count", 0),
                "articles": case_data.get("articles", ""),
                "sections": case_data.get("sections", ""),
                "summary": case_data.get("summary", ""),
                "full_text_url": case_data.get("full_text_url", ""),
                "jurisdiction": case_data.get("jurisdiction", ""),
                "case_type": case_data.get("case_type", ""),
                "parties": case_data.get("parties", ""),
                "judgment_date": case_data.get("judgment_date")
            }
            
            rows_to_insert.append(row)
            count += 1
            
            # Insert in batches of 1000
            if len(rows_to_insert) >= 1000:
                errors = bq_client.insert_rows_json(table_id, rows_to_insert)
                if errors:
                    logger.error(f"Errors inserting rows: {errors}")
                else:
                    logger.info(f"Inserted {len(rows_to_insert)} cases")
                rows_to_insert = []
        
        # Insert remaining rows
        if rows_to_insert:
            errors = bq_client.insert_rows_json(table_id, rows_to_insert)
            if errors:
                logger.error(f"Errors inserting rows: {errors}")
            else:
                logger.info(f"Inserted {len(rows_to_insert)} cases")
        
        logger.info(f"Migration complete! Migrated {count} cases from Firestore to BigQuery")
        
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise


def migrate_statutes():
    """Migrate statutes from Firestore to BigQuery."""
    try:
        # Initialize Firestore client
        db = firestore.Client(project=settings.gcp_project_id)
        statutes_ref = db.collection("statutes")
        
        # Initialize BigQuery client
        bq_client = bigquery.Client(project=settings.gcp_project_id)
        table_id = f"{settings.gcp_project_id}.{settings.bigquery_dataset}.{settings.bigquery_statute_table}"
        
        # Get all statutes from Firestore
        logger.info("Fetching statutes from Firestore...")
        firestore_statutes = statutes_ref.stream()
        
        rows_to_insert = []
        count = 0
        
        for doc in firestore_statutes:
            statute_data = doc.to_dict()
            statute_id = doc.id
            
            # Format for BigQuery
            row = {
                "statute_id": statute_id,
                "act_name": statute_data.get("act_name", ""),
                "section_number": statute_data.get("section_number", ""),
                "section_title": statute_data.get("section_title", ""),
                "section_text": statute_data.get("section_text", ""),
                "jurisdiction": statute_data.get("jurisdiction", ""),
                "effective_date": statute_data.get("effective_date"),
                "related_cases": statute_data.get("related_cases", ""),
                "amendments": statute_data.get("amendments", "")
            }
            
            rows_to_insert.append(row)
            count += 1
            
            # Insert in batches of 1000
            if len(rows_to_insert) >= 1000:
                errors = bq_client.insert_rows_json(table_id, rows_to_insert)
                if errors:
                    logger.error(f"Errors inserting rows: {errors}")
                else:
                    logger.info(f"Inserted {len(rows_to_insert)} statutes")
                rows_to_insert = []
        
        # Insert remaining rows
        if rows_to_insert:
            errors = bq_client.insert_rows_json(table_id, rows_to_insert)
            if errors:
                logger.error(f"Errors inserting rows: {errors}")
            else:
                logger.info(f"Inserted {len(rows_to_insert)} statutes")
        
        logger.info(f"Migration complete! Migrated {count} statutes from Firestore to BigQuery")
        
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "cases":
            migrate_cases()
        elif sys.argv[1] == "statutes":
            migrate_statutes()
        elif sys.argv[1] == "all":
            migrate_cases()
            migrate_statutes()
        else:
            print("Usage: python migrate_firestore_to_bigquery.py [cases|statutes|all]")
    else:
        print("Usage: python migrate_firestore_to_bigquery.py [cases|statutes|all]")
        print("This script migrates data from Firestore to BigQuery")
        print("Note: This is optional - you can use Firestore directly by setting DATA_SOURCE=firestore")

