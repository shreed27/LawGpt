"""BigQuery client for querying legal data."""
from google.cloud import bigquery
from typing import List, Dict, Any, Optional
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BigQueryClient:
    """Client for interacting with BigQuery legal data."""
    
    def __init__(self):
        self.client = bigquery.Client(project=settings.gcp_project_id)
        self.dataset_id = settings.bigquery_dataset
        self.case_table = settings.bigquery_case_table
        self.statute_table = settings.bigquery_statute_table
    
    def search_cases(
        self,
        topic: str,
        jurisdiction: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for legal cases by topic.
        
        Args:
            topic: Search topic/keywords
            jurisdiction: Optional jurisdiction filter
            limit: Maximum number of results
            
        Returns:
            List of case records with metadata
        """
        query = f"""
        SELECT 
            case_id,
            case_title,
            court,
            year,
            citation_count,
            articles,
            sections,
            summary,
            full_text_url,
            jurisdiction,
            case_type,
            parties,
            judgment_date
        FROM `{settings.gcp_project_id}.{self.dataset_id}.{self.case_table}`
        WHERE 
            LOWER(case_title) LIKE LOWER('%{topic}%')
            OR LOWER(summary) LIKE LOWER('%{topic}%')
            OR LOWER(articles) LIKE LOWER('%{topic}%')
            OR LOWER(sections) LIKE LOWER('%{topic}%')
            {"AND jurisdiction = @jurisdiction" if jurisdiction else ""}
        ORDER BY citation_count DESC, year DESC
        LIMIT @limit
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("limit", "INT64", limit),
            ]
        )
        
        if jurisdiction:
            job_config.query_parameters.append(
                bigquery.ScalarQueryParameter("jurisdiction", "STRING", jurisdiction)
            )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            cases = []
            for row in results:
                cases.append({
                    "case_id": row.case_id,
                    "case_title": row.case_title,
                    "court": row.court,
                    "year": row.year,
                    "citation_count": row.citation_count,
                    "articles": row.articles.split(",") if row.articles else [],
                    "sections": row.sections.split(",") if row.sections else [],
                    "summary": row.summary,
                    "full_text_url": row.full_text_url,
                    "jurisdiction": row.jurisdiction,
                    "case_type": row.case_type,
                    "parties": row.parties,
                    "judgment_date": str(row.judgment_date) if row.judgment_date else None
                })
            
            logger.info(f"Retrieved {len(cases)} cases for topic: {topic}")
            return cases
            
        except Exception as e:
            logger.error(f"Error querying BigQuery: {str(e)}")
            raise
    
    def get_statutes(
        self,
        topic: str,
        jurisdiction: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for statutes/acts by topic.
        
        Args:
            topic: Search topic/keywords
            jurisdiction: Optional jurisdiction filter
            limit: Maximum number of results
            
        Returns:
            List of statute records
        """
        query = f"""
        SELECT 
            statute_id,
            act_name,
            section_number,
            section_title,
            section_text,
            jurisdiction,
            effective_date,
            related_cases,
            amendments
        FROM `{settings.gcp_project_id}.{self.dataset_id}.{self.statute_table}`
        WHERE 
            LOWER(act_name) LIKE LOWER('%{topic}%')
            OR LOWER(section_text) LIKE LOWER('%{topic}%')
            OR LOWER(section_title) LIKE LOWER('%{topic}%')
            {"AND jurisdiction = @jurisdiction" if jurisdiction else ""}
        LIMIT @limit
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("limit", "INT64", limit),
            ]
        )
        
        if jurisdiction:
            job_config.query_parameters.append(
                bigquery.ScalarQueryParameter("jurisdiction", "STRING", jurisdiction)
            )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            statutes = []
            for row in results:
                statutes.append({
                    "statute_id": row.statute_id,
                    "act_name": row.act_name,
                    "section_number": row.section_number,
                    "section_title": row.section_title,
                    "section_text": row.section_text,
                    "jurisdiction": row.jurisdiction,
                    "effective_date": str(row.effective_date) if row.effective_date else None,
                    "related_cases": row.related_cases.split(",") if row.related_cases else [],
                    "amendments": row.amendments.split(",") if row.amendments else []
                })
            
            logger.info(f"Retrieved {len(statutes)} statutes for topic: {topic}")
            return statutes
            
        except Exception as e:
            logger.error(f"Error querying BigQuery for statutes: {str(e)}")
            raise
    
    def get_case_by_id(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get full case details by case ID."""
        query = f"""
        SELECT *
        FROM `{settings.gcp_project_id}.{self.dataset_id}.{self.case_table}`
        WHERE case_id = @case_id
        LIMIT 1
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("case_id", "STRING", case_id),
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                return dict(row)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching case by ID: {str(e)}")
            raise

