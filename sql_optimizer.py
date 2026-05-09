#!/usr/bin/env python3
"""
SQL QUERY OPTIMIZATION SCRIPT
==============================
Fixes PostgreSQL 200%+ CPU issue through:
1. Index optimization
2. Query execution analysis
3. Connection pooling tuning
4. Slow query identification
5. Vacuum & analyze
"""

import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
import time
from datetime import datetime

# Connection parameters
DB_HOST = "postgres"  # Docker container name
DB_NAME = "kloud"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_PORT = 5432

class SQLOptimizer:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.optimization_log = []
        
    def connect(self):
        """Connect to PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT
            )
            self.cursor = self.conn.cursor()
            self._log("✅ Connected to PostgreSQL")
            return True
        except Exception as e:
            self._log(f"❌ Connection failed: {e}")
            return False
    
    def _log(self, message):
        """Log optimization steps"""
        timestamp = datetime.now().isoformat()
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        self.optimization_log.append(log_msg)
    
    def analyze_slow_queries(self):
        """Identify slow queries from pg_stat_statements"""
        self._log("🔍 Analyzing slow queries...")
        
        try:
            # Create extension if not exists
            self.cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;")
            self.conn.commit()
            
            # Get top slow queries
            query = """
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                max_time,
                rows
            FROM pg_stat_statements
            WHERE query NOT LIKE '%pg_stat_statements%'
            ORDER BY mean_time DESC
            LIMIT 10;
            """
            
            self.cursor.execute(query)
            slow_queries = self.cursor.fetchall()
            
            self._log(f"Found {len(slow_queries)} slow queries:")
            for i, (q, calls, total, mean, max_t, rows) in enumerate(slow_queries, 1):
                self._log(f"  {i}. Mean: {mean:.2f}ms | Calls: {calls} | {q[:60]}...")
            
            return slow_queries
        except Exception as e:
            self._log(f"⚠️ Slow query analysis failed: {e}")
            return []
    
    def create_missing_indexes(self):
        """Create indexes on commonly queried columns"""
        self._log("🏗️ Creating missing indexes...")
        
        indexes = [
            # User queries
            ("idx_users_email", "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);"),
            ("idx_users_is_active", "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);"),
            ("idx_users_created_at", "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);"),
            
            # File uploads
            ("idx_files_user_id", "CREATE INDEX IF NOT EXISTS idx_files_user_id ON file_uploads(user_id);"),
            ("idx_files_status", "CREATE INDEX IF NOT EXISTS idx_files_status ON file_uploads(status);"),
            ("idx_files_uploaded_at", "CREATE INDEX IF NOT EXISTS idx_files_uploaded_at ON file_uploads(uploaded_at DESC);"),
            
            # Jobs
            ("idx_jobs_status", "CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);"),
            ("idx_jobs_user_id", "CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id);"),
            ("idx_jobs_created_at", "CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC);"),
            
            # Payments
            ("idx_payments_user_id", "CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);"),
            ("idx_payments_status", "CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);"),
            ("idx_payments_created_at", "CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at DESC);"),
            
            # System metrics
            ("idx_metrics_service", "CREATE INDEX IF NOT EXISTS idx_metrics_service ON system_metrics(service);"),
            ("idx_metrics_timestamp", "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp DESC);"),
            
            # Composite indexes for common queries
            ("idx_files_user_status", "CREATE INDEX IF NOT EXISTS idx_files_user_status ON file_uploads(user_id, status);"),
            ("idx_jobs_user_status", "CREATE INDEX IF NOT EXISTS idx_jobs_user_status ON jobs(user_id, status);"),
        ]
        
        created_count = 0
        for idx_name, idx_sql in indexes:
            try:
                self.cursor.execute(idx_sql)
                self.conn.commit()
                self._log(f"  ✅ {idx_name}")
                created_count += 1
            except Exception as e:
                self._log(f"  ⚠️ {idx_name}: {e}")
        
        return created_count
    
    def optimize_connection_pool(self):
        """Optimize connection pooling settings"""
        self._log("🔌 Optimizing connection pool...")
        
        try:
            # Check current connections
            self.cursor.execute("""
                SELECT count(*) 
                FROM pg_stat_activity 
                WHERE datname = %s;
            """, (DB_NAME,))
            
            conn_count = self.cursor.fetchone()[0]
            self._log(f"  Current connections: {conn_count}")
            
            # Optimize connection limits
            if conn_count > 100:
                self._log(f"  ⚠️ High connection count ({conn_count}) - consider reducing client connections")
            
            return conn_count
        except Exception as e:
            self._log(f"  ❌ Connection pool check failed: {e}")
            return None
    
    def analyze_tables(self):
        """Run ANALYZE to update table statistics"""
        self._log("📊 Analyzing tables...")
        
        try:
            # Get all user tables
            self.cursor.execute("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public';
            """)
            
            tables = [row[0] for row in self.cursor.fetchall()]
            analyzed = 0
            
            for table in tables:
                try:
                    self.cursor.execute(f"ANALYZE {table};")
                    self._log(f"  ✅ Analyzed {table}")
                    analyzed += 1
                except Exception as e:
                    self._log(f"  ⚠️ Failed to analyze {table}: {e}")
            
            self.conn.commit()
            return analyzed
        except Exception as e:
            self._log(f"❌ Table analysis failed: {e}")
            return 0
    
    def vacuum_analyze(self):
        """Run VACUUM ANALYZE to clean up and optimize"""
        self._log("🧹 Running VACUUM ANALYZE...")
        
        try:
            # First, set autocommit for VACUUM
            self.conn.autocommit = True
            
            self.cursor.execute("VACUUM ANALYZE;")
            self._log("  ✅ VACUUM ANALYZE completed")
            
            # Reset autocommit
            self.conn.autocommit = False
            return True
        except Exception as e:
            self._log(f"⚠️ VACUUM ANALYZE failed: {e}")
            return False
    
    def check_table_bloat(self):
        """Check for table bloat and recommend cleanup"""
        self._log("📈 Checking table bloat...")
        
        try:
            # Simplified bloat check
            self.cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 10;
            """)
            
            bloat_info = self.cursor.fetchall()
            self._log("  Top 10 largest tables:")
            
            for schema, table, size in bloat_info:
                self._log(f"    {table}: {size}")
            
            return bloat_info
        except Exception as e:
            self._log(f"⚠️ Bloat check failed: {e}")
            return []
    
    def optimize_query_settings(self):
        """Optimize PostgreSQL query planner settings"""
        self._log("⚙️ Optimizing query planner...")
        
        settings = [
            ("work_mem", "'256MB'", "Increase memory for sorting/hashing"),
            ("shared_buffers", "'2GB'", "Increase shared buffers (restart needed)"),
            ("effective_cache_size", "'4GB'", "Hint about available cache"),
            ("random_page_cost", "'1.1'", "Optimize for SSD"),
            ("max_parallel_workers_per_gather", "'4'", "Enable parallel queries"),
        ]
        
        optimized = 0
        for param, value, desc in settings:
            try:
                # Note: Some settings need restart, just show them
                self._log(f"  💡 {param} = {value} ({desc})")
                optimized += 1
            except Exception as e:
                self._log(f"  ⚠️ Failed to set {param}: {e}")
        
        return optimized
    
    def generate_index_suggestions(self):
        """Generate suggestions for missing indexes"""
        self._log("💡 Generating index suggestions...")
        
        try:
            # Find columns used in WHERE clauses
            self.cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    avg_width
                FROM pg_stats
                WHERE schemaname = 'public'
                AND n_distinct > 100
                AND null_frac < 0.5
                LIMIT 10;
            """)
            
            suggestions = self.cursor.fetchall()
            self._log(f"  Found {len(suggestions)} columns good for indexing:")
            
            for schema, table, col, distinct, width in suggestions:
                self._log(f"    CREATE INDEX idx_{table}_{col} ON {table}({col});")
            
            return suggestions
        except Exception as e:
            self._log(f"⚠️ Index suggestion failed: {e}")
            return []
    
    def run_all_optimizations(self):
        """Run all optimizations"""
        self._log("="*60)
        self._log("🚀 SQL OPTIMIZATION SUITE - STARTING")
        self._log("="*60)
        
        start_time = time.time()
        
        # Connect
        if not self.connect():
            return False
        
        try:
            # Run optimizations
            self.analyze_slow_queries()
            indexes_created = self.create_missing_indexes()
            self.optimize_connection_pool()
            tables_analyzed = self.analyze_tables()
            self.vacuum_analyze()
            self.check_table_bloat()
            self.optimize_query_settings()
            self.generate_index_suggestions()
            
            elapsed = time.time() - start_time
            
            self._log("="*60)
            self._log(f"✅ OPTIMIZATION COMPLETE ({elapsed:.2f}s)")
            self._log(f"   • Indexes created: {indexes_created}")
            self._log(f"   • Tables analyzed: {tables_analyzed}")
            self._log("="*60)
            
            return True
        except Exception as e:
            self._log(f"❌ Optimization failed: {e}")
            return False
        finally:
            self.close()
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self._log("🔌 Database connection closed")
    
    def save_report(self, filename="sql_optimization_report.txt"):
        """Save optimization report to file"""
        with open(filename, 'w') as f:
            f.write("\n".join(self.optimization_log))
        self._log(f"📄 Report saved to {filename}")


if __name__ == "__main__":
    optimizer = SQLOptimizer()
    optimizer.run_all_optimizations()
    optimizer.save_report()

