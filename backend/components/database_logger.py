"""
Database Logger component for the Intelligent Digital Fraud Awareness and Detection Platform.

This module provides SQLite-based persistence for analysis results with retry logic,
analytics aggregation, and privacy controls.
"""

import sqlite3
import json
import logging
import time
from typing import Optional
from datetime import datetime
from pathlib import Path

from backend.models.data_models import AnalysisResult, AnalyticsData
from backend.config import Config


# Configure logging
logger = logging.getLogger(__name__)


class DatabaseLogger:
    """
    Persists analysis results to SQLite database with retry logic and analytics support.
    
    Features:
    - Automatic schema creation with constraints and indexes
    - Retry logic for database lock handling (up to 3 retries with exponential backoff)
    - Aggregated analytics for dashboard visualization
    - Privacy controls for clearing history
    - Comprehensive logging for all operations
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initializes database connection and creates schema if needed.
        
        Args:
            db_path: Path to SQLite database file. Defaults to Config.DB_PATH.
        """
        self.db_path = db_path or str(Config.DB_PATH)
        logger.info(f"Initializing DatabaseLogger with path: {self.db_path}")
        
        try:
            # Initialize connection
            self.conn = sqlite3.connect(
                self.db_path,
                timeout=Config.DB_TIMEOUT,
                check_same_thread=False
            )
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            self.cursor = self.conn.cursor()
            
            # Create schema
            self._create_schema()
            
            logger.info("DatabaseLogger initialized successfully")
            
        except sqlite3.Error as e:
            logger.critical(f"Database connection failed: {e}", exc_info=True)
            raise
    
    def _create_schema(self) -> None:
        """
        Creates database schema with tables, constraints, and indexes.
        
        Schema includes:
        - analyses table with all required columns
        - CHECK constraints for score ranges and valid risk levels
        - Indexes on timestamp, risk_level, and fraud_category for query performance
        """
        try:
            # Create analyses table with constraints
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_text TEXT NOT NULL,
                    rule_score REAL NOT NULL,
                    ai_probability REAL NOT NULL,
                    final_risk_score REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    fraud_category TEXT NOT NULL,
                    triggered_keywords TEXT NOT NULL,
                    awareness_score REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    
                    CHECK (rule_score >= 0 AND rule_score <= 100),
                    CHECK (ai_probability >= 0 AND ai_probability <= 100),
                    CHECK (final_risk_score >= 0 AND final_risk_score <= 100),
                    CHECK (risk_level IN ('Safe', 'Suspicious', 'High Risk')),
                    CHECK (awareness_score >= 0 AND awareness_score <= 100)
                )
            """)
            
            # Create indexes for query performance
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON analyses(timestamp)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_risk_level 
                ON analyses(risk_level)
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_fraud_category 
                ON analyses(fraud_category)
            """)
            
            self.conn.commit()
            logger.info("Database schema created successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Schema creation failed: {e}", exc_info=True)
            raise
    
    def log_analysis(self, analysis_result: AnalysisResult) -> bool:
        """
        Stores analysis result in database with retry logic.
        
        Args:
            analysis_result: Complete analysis results to persist
            
        Returns:
            True if successful, False otherwise
            
        Note:
            Retries up to 3 times on database lock errors with exponential backoff.
        """
        max_retries = Config.DB_MAX_RETRIES
        
        for attempt in range(1, max_retries + 1):
            try:
                # Convert triggered_keywords dict to JSON string
                triggered_keywords_json = json.dumps(analysis_result.triggered_keywords)
                
                # Insert analysis record
                self.cursor.execute("""
                    INSERT INTO analyses (
                        message_text,
                        rule_score,
                        ai_probability,
                        final_risk_score,
                        risk_level,
                        fraud_category,
                        triggered_keywords,
                        awareness_score,
                        timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis_result.message_text,
                    analysis_result.rule_score,
                    analysis_result.ai_probability,
                    analysis_result.final_risk_score,
                    analysis_result.risk_level,
                    analysis_result.fraud_category,
                    triggered_keywords_json,
                    analysis_result.awareness_score,
                    analysis_result.timestamp.isoformat()
                ))
                
                self.conn.commit()
                record_id = self.cursor.lastrowid
                
                logger.info(
                    f"Analysis logged successfully: "
                    f"id={record_id}, "
                    f"risk_score={analysis_result.final_risk_score:.2f}, "
                    f"category={analysis_result.fraud_category}"
                )
                
                return True
                
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and attempt < max_retries:
                    # Database is locked, retry with exponential backoff
                    backoff_time = 0.1 * (2 ** (attempt - 1))  # 0.1s, 0.2s, 0.4s
                    logger.warning(
                        f"Database locked, retry attempt {attempt}/{max_retries} "
                        f"after {backoff_time}s"
                    )
                    time.sleep(backoff_time)
                else:
                    # Max retries reached or different error
                    logger.error(
                        f"Database operation failed after {attempt} attempts: {e}",
                        exc_info=True
                    )
                    return False
                    
            except sqlite3.Error as e:
                logger.error(f"Database write failed: {e}", exc_info=True)
                return False
            except Exception as e:
                logger.error(f"Unexpected error during log_analysis: {e}", exc_info=True)
                return False
        
        return False
    
    def get_analytics(self) -> AnalyticsData:
        """
        Retrieves aggregated statistics for dashboard visualization.
        
        Returns:
            AnalyticsData containing:
                - total_messages: Total count of analyzed messages
                - risk_distribution: Count by risk level
                - category_distribution: Count by fraud category
                - average_risk_score: Mean risk score
                - top_keywords: Top 10 most common keywords
                - risk_trend: Risk scores over time
        """
        try:
            logger.info("Retrieving analytics data")
            
            # Total messages
            self.cursor.execute("SELECT COUNT(*) FROM analyses")
            total_messages = self.cursor.fetchone()[0]
            
            # Risk distribution
            self.cursor.execute("""
                SELECT risk_level, COUNT(*) as count
                FROM analyses
                GROUP BY risk_level
            """)
            risk_distribution = {
                row['risk_level']: row['count'] 
                for row in self.cursor.fetchall()
            }
            
            # Ensure all risk levels are present
            for level in ['Safe', 'Suspicious', 'High Risk']:
                if level not in risk_distribution:
                    risk_distribution[level] = 0
            
            # Category distribution
            self.cursor.execute("""
                SELECT fraud_category, COUNT(*) as count
                FROM analyses
                GROUP BY fraud_category
            """)
            category_distribution = {
                row['fraud_category']: row['count']
                for row in self.cursor.fetchall()
            }
            
            # Average risk score
            self.cursor.execute("SELECT AVG(final_risk_score) FROM analyses")
            avg_score = self.cursor.fetchone()[0]
            average_risk_score = float(avg_score) if avg_score is not None else 0.0
            
            # Top keywords (extract from JSON and count)
            self.cursor.execute("SELECT triggered_keywords FROM analyses")
            keyword_counts = {}
            for row in self.cursor.fetchall():
                try:
                    keywords_dict = json.loads(row['triggered_keywords'])
                    for category, keywords in keywords_dict.items():
                        for keyword in keywords:
                            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
                except (json.JSONDecodeError, TypeError):
                    logger.warning(f"Failed to parse triggered_keywords: {row['triggered_keywords']}")
                    continue
            
            # Get top 10 keywords
            top_keywords = sorted(
                keyword_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # Risk trend (last 100 analyses)
            self.cursor.execute("""
                SELECT timestamp, final_risk_score
                FROM analyses
                ORDER BY timestamp DESC
                LIMIT 100
            """)
            risk_trend = [
                {
                    'timestamp': row['timestamp'],
                    'score': row['final_risk_score']
                }
                for row in reversed(list(self.cursor.fetchall()))
            ]
            
            logger.info(
                f"Analytics retrieved: "
                f"total_messages={total_messages}, "
                f"avg_risk_score={average_risk_score:.2f}"
            )
            
            return AnalyticsData(
                total_messages=total_messages,
                risk_distribution=risk_distribution,
                category_distribution=category_distribution,
                average_risk_score=average_risk_score,
                top_keywords=top_keywords,
                risk_trend=risk_trend
            )
            
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve analytics: {e}", exc_info=True)
            # Return empty analytics on error
            return AnalyticsData(
                total_messages=0,
                risk_distribution={'Safe': 0, 'Suspicious': 0, 'High Risk': 0},
                category_distribution={},
                average_risk_score=0.0,
                top_keywords=[],
                risk_trend=[]
            )
    
    def clear_history(self, confirm: bool = False) -> bool:
        """
        Clears all stored analysis history (privacy feature).
        
        This operation is irreversible and permanently deletes all analysis records.
        Requires explicit confirmation for safety.
        
        Args:
            confirm: Safety flag requiring explicit confirmation (must be True)
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If confirm is not True
        """
        if not confirm:
            logger.warning("Clear history attempted without confirmation")
            raise ValueError("Confirmation required to clear history. Set confirm=True.")
        
        try:
            # Get count before deletion for logging
            self.cursor.execute("SELECT COUNT(*) FROM analyses")
            count = self.cursor.fetchone()[0]
            
            # Delete all records
            self.cursor.execute("DELETE FROM analyses")
            self.conn.commit()
            
            logger.info(f"User history cleared: {count} records deleted")
            
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Failed to clear history: {e}", exc_info=True)
            return False
    
    def close(self) -> None:
        """
        Closes database connection.
        
        Should be called when the DatabaseLogger is no longer needed.
        """
        try:
            if self.conn:
                self.conn.close()
                logger.info("Database connection closed")
        except sqlite3.Error as e:
            logger.error(f"Error closing database connection: {e}", exc_info=True)
    
    def __del__(self):
        """Ensures database connection is closed on object destruction."""
        self.close()
