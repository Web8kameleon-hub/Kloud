"""
DuckDB Analytics Engine for Kloud
Ultra-fast columnar analytics, zero server overhead

Features:
- Direct Parquet/CSV/JSON reading
- SIMD-optimized queries
- In-memory or disk-based
- 10-100x faster than PostgreSQL for analytics
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DuckDBAnalyticsEngine:
    """Ultra-fast analytics on telemetry data"""
    
    def __init__(self, data_dir: str = "/data/kloud/analytics"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            import duckdb
            self.duckdb = duckdb.connect(str(self.data_dir / "analytics.duckdb"))
            self.duckdb.execute("PRAGMA memory_limit='1GB'")
            self.duckdb.execute("PRAGMA threads=4")
            logger.info("✓ DuckDB initialized for analytics")
        except ImportError:
            logger.warning("DuckDB not installed - analytics disabled")
            self.duckdb = None
    
    def query(self, sql: str, params: List[Any] = None) -> List[Dict]:
        """Execute DuckDB query"""
        if not self.duckdb:
            logger.warning("DuckDB not available")
            return []
        
        try:
            result = self.duckdb.execute(sql, params or []).fetchall()
            descriptions = [desc[0] for desc in self.duckdb.description or []]
            return [dict(zip(descriptions, row)) for row in result]
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []
    
    def load_telemetry_file(self, file_path: str, format: str = "parquet") -> bool:
        """Load telemetry from Parquet/CSV/JSON"""
        if not self.duckdb:
            return False
        
        try:
            table_name = Path(file_path).stem
            
            if format.lower() == "parquet":
                self.duckdb.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_parquet('{file_path}')")
            elif format.lower() == "csv":
                self.duckdb.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{file_path}')")
            elif format.lower() == "json":
                self.duckdb.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_json_auto('{file_path}')")
            
            logger.info(f"✓ Loaded {format} file: {table_name}")
            return True
        except Exception as e:
            logger.error(f"Load failed: {e}")
            return False
    
    # ==================== TELEMETRY ANALYTICS ====================
    
    def get_sensor_stats(self, sensor_id: str) -> Dict[str, Any]:
        """Get statistics for a sensor"""
        if not self.duckdb:
            return {}
        
        try:
            # Assuming telemetry data structure with value, timestamp columns
            result = self.duckdb.execute(f"""
                SELECT 
                    COUNT(*) as count,
                    AVG(value) as avg_value,
                    MIN(value) as min_value,
                    MAX(value) as max_value,
                    STDDEV(value) as stddev_value,
                    MIN(timestamp) as first_reading,
                    MAX(timestamp) as last_reading
                FROM telemetry 
                WHERE sensor_id = ?
            """, [sensor_id]).fetchone()
            
            if result:
                cols = [desc[0] for desc in self.duckdb.description]
                return dict(zip(cols, result))
            return {}
        except Exception as e:
            logger.error(f"Sensor stats failed: {e}")
            return {}
    
    def get_time_series(self, sensor_id: str, interval: str = "5m") -> List[Dict]:
        """Get time-series data aggregated by interval"""
        if not self.duckdb:
            return []
        
        try:
            result = self.duckdb.execute(f"""
                SELECT 
                    time_bucket('{interval}', timestamp) as bucket,
                    AVG(value) as avg_value,
                    MIN(value) as min_value,
                    MAX(value) as max_value,
                    COUNT(*) as count
                FROM telemetry
                WHERE sensor_id = ?
                GROUP BY bucket
                ORDER BY bucket
            """, [sensor_id]).fetchall()
            
            cols = [desc[0] for desc in self.duckdb.description]
            return [dict(zip(cols, row)) for row in result]
        except Exception as e:
            logger.error(f"Time series failed: {e}")
            return []
    
    def get_anomalies(self, sensor_id: str, threshold: float = 2.0) -> List[Dict]:
        """Detect anomalies using statistical analysis"""
        if not self.duckdb:
            return []
        
        try:
            result = self.duckdb.execute(f"""
                WITH stats AS (
                    SELECT 
                        AVG(value) as avg_value,
                        STDDEV(value) as stddev_value
                    FROM telemetry
                    WHERE sensor_id = ?
                )
                SELECT 
                    timestamp,
                    value,
                    (value - stats.avg_value) / stats.stddev_value as z_score
                FROM telemetry, stats
                WHERE sensor_id = ?
                AND ABS((value - stats.avg_value) / stats.stddev_value) > ?
                ORDER BY timestamp DESC
                LIMIT 100
            """, [sensor_id, sensor_id, threshold]).fetchall()
            
            cols = [desc[0] for desc in self.duckdb.description]
            return [dict(zip(cols, row)) for row in result]
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []
    
    def compare_sensors(self, sensor_ids: List[str], start_time: str = None, end_time: str = None) -> Dict[str, Any]:
        """Compare statistics across multiple sensors"""
        if not self.duckdb:
            return {}
        
        try:
            where_clause = "WHERE sensor_id IN ({})".format(','.join('?' * len(sensor_ids)))
            params = sensor_ids.copy()
            
            if start_time:
                where_clause += " AND timestamp >= ?"
                params.append(start_time)
            if end_time:
                where_clause += " AND timestamp <= ?"
                params.append(end_time)
            
            result = self.duckdb.execute(f"""
                SELECT 
                    sensor_id,
                    COUNT(*) as count,
                    AVG(value) as avg_value,
                    MIN(value) as min_value,
                    MAX(value) as max_value,
                    STDDEV(value) as stddev_value
                FROM telemetry 
                {where_clause}
                GROUP BY sensor_id
                ORDER BY avg_value DESC
            """, params).fetchall()
            
            cols = [desc[0] for desc in self.duckdb.description]
            return {row[0]: dict(zip(cols[1:], row[1:])) for row in result}
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            return {}
    
    # ==================== PROFILE ANALYSIS ====================
    
    def get_profile_summary(self, profile_id: str) -> Dict[str, Any]:
        """Get summary statistics for a decoded profile"""
        if not self.duckdb:
            return {}
        
        try:
            result = self.duckdb.execute(f"""
                SELECT 
                    COUNT(*) as total_chunks,
                    SUM(chunk_size) as total_size,
                    AVG(chunk_size) as avg_chunk_size,
                    MIN(timestamp) as first_chunk,
                    MAX(timestamp) as last_chunk
                FROM profiles
                WHERE profile_id = ?
            """, [profile_id]).fetchone()
            
            if result:
                cols = [desc[0] for desc in self.duckdb.description]
                return dict(zip(cols, result))
            return {}
        except Exception as e:
            logger.error(f"Profile summary failed: {e}")
            return {}
    
    # ==================== EXPORT ====================
    
    def export_to_parquet(self, query: str, output_path: str) -> bool:
        """Export query results to Parquet"""
        if not self.duckdb:
            return False
        
        try:
            self.duckdb.execute(f"COPY ({query}) TO '{output_path}' (FORMAT PARQUET)")
            logger.info(f"✓ Exported to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    def export_to_csv(self, query: str, output_path: str) -> bool:
        """Export query results to CSV"""
        if not self.duckdb:
            return False
        
        try:
            self.duckdb.execute(f"COPY ({query}) TO '{output_path}' (FORMAT CSV, HEADER TRUE)")
            logger.info(f"✓ Exported to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    def export_to_json(self, query: str, output_path: str) -> bool:
        """Export query results to JSON"""
        if not self.duckdb:
            return False
        
        try:
            self.duckdb.execute(f"COPY ({query}) TO '{output_path}' (FORMAT JSON)")
            logger.info(f"✓ Exported to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    # ==================== STATISTICS ====================
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get DuckDB engine statistics"""
        if not self.duckdb:
            return {}
        
        try:
            tables = self.duckdb.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'").fetchall()
            
            stats = {
                "tables": [t[0] for t in tables],
                "table_count": len(tables),
            }
            
            return stats
        except Exception as e:
            logger.error(f"Stats retrieval failed: {e}")
            return {}
    
    def close(self):
        """Close DuckDB connection"""
        if self.duckdb:
            self.duckdb.close()
            logger.info("✓ DuckDB closed")


# ==================== INITIALIZATION ====================

_analytics_instance: Optional[DuckDBAnalyticsEngine] = None


def initialize_analytics_engine(data_dir: str = "/data/kloud/analytics") -> DuckDBAnalyticsEngine:
    """Initialize DuckDB analytics engine (singleton)"""
    global _analytics_instance
    if not _analytics_instance:
        _analytics_instance = DuckDBAnalyticsEngine(data_dir)
    return _analytics_instance


def get_analytics_engine() -> DuckDBAnalyticsEngine:
    """Get analytics engine instance"""
    return initialize_analytics_engine()

