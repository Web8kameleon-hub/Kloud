#!/bin/bash
# PostgreSQL Connection Pooling & Performance Tuning
# Configures PostgreSQL and PgBouncer for optimal connection handling

echo "============================================================"
echo "🔧 PostgreSQL Connection Pooling Optimization"
echo "============================================================"

# 1. Update PostgreSQL settings (container-based)
echo ""
echo "📋 Step 1: Optimizing PostgreSQL settings..."

docker exec kloud-postgres psql -U postgres -c "
-- Tuning for 4 CPU cores and 7.6GB RAM

-- Connection Limits
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET superuser_reserved_connections = 3;

-- Memory Settings
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '4GB';
ALTER SYSTEM SET work_mem = '256MB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';

-- Connection Pooling & Timeouts
ALTER SYSTEM SET idle_in_transaction_session_timeout = '30s';
ALTER SYSTEM SET statement_timeout = '30s';
ALTER SYSTEM SET lock_timeout = '10s';
ALTER SYSTEM SET idle_session_timeout = '60s';

-- Query Planning
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Parallel Query Execution
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 4;
ALTER SYSTEM SET max_parallel_maintenance_workers = 4;

-- Logging
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_connections = ON;

SELECT 'PostgreSQL settings updated' as status;
" 2>&1 | tail -5

# 2. Create PgBouncer configuration
echo ""
echo "🔌 Step 2: Setting up PgBouncer connection pooler..."

cat > /tmp/pgbouncer.ini << 'PGBOUNCER_EOF'
[databases]
readme_to_recover = host=postgres port=5432 dbname=readme_to_recover

[pgbouncer]
; Connection pooling mode (transaction = pool at transaction level)
pool_mode = transaction
listen_port = 6432
listen_addr = *
auth_type = plain
auth_file = /etc/pgbouncer/userlist.txt

; Connection pool settings
max_client_conn = 1000
default_pool_size = 25
min_pool_size = 10
reserve_pool_size = 5
reserve_pool_timeout = 3
max_pool_size = 50

; Timeout settings
server_lifetime = 3600
server_idle_in_transaction_timeout = 30
query_timeout = 0
query_wait_timeout = 120
client_idle_timeout = 900
client_login_timeout = 60

; Performance settings
tcp_keepalives = 1
tcp_keepalives_idle = 30
tcp_keepalives_interval = 10

; Statistics
stats_period = 60
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1

admin_users = postgres
PGBOUNCER_EOF

echo "✅ PgBouncer configuration created"

# 3. Create userlist for PgBouncer
cat > /tmp/userlist.txt << 'USERLIST_EOF'
"postgres" "postgres"
USERLIST_EOF

echo "✅ PgBouncer userlist created"

# 4. Analyze current slow queries
echo ""
echo "📊 Step 3: Analyzing slow queries..."

docker exec kloud-postgres psql -U postgres -d readme_to_recover -c "
-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Show top 5 slowest queries
SELECT 
    LEFT(query, 80) as query,
    calls,
    ROUND(mean_time::numeric, 2) as mean_ms,
    ROUND(max_time::numeric, 2) as max_ms
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_time DESC
LIMIT 5;
" 2>&1

# 5. Show table sizes for potential partitioning
echo ""
echo "📈 Step 4: Identifying large tables for partitioning..."

docker exec kloud-postgres psql -U postgres -d readme_to_recover -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    CASE 
        WHEN pg_total_relation_size(schemaname||'.'||tablename) > 104857600 THEN '⚠️ LARGE'
        ELSE '✅ OK'
    END as status
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
" 2>&1

# 6. Show current connection stats
echo ""
echo "🔌 Step 5: Current connection statistics..."

docker exec kloud-postgres psql -U postgres -c "
SELECT 
    datname as database,
    count(*) as connections,
    max(EXTRACT(EPOCH FROM (now() - query_start))) as oldest_query_seconds
FROM pg_stat_activity
WHERE datname IS NOT NULL
GROUP BY datname
ORDER BY connections DESC;
" 2>&1

# 7. Show connection pool recommendations
echo ""
echo "💡 Step 6: Connection Pool Recommendations..."

cat << 'RECOMMENDATIONS_EOF'

📋 Recommended Configuration:
   - Pool Mode: transaction (one connection per transaction)
   - Pool Size: 25 (default)
   - Min Size: 10
   - Max Size: 50
   - Client Connections: 1000

🎯 Tuning Tips:
   1. For 4 CPU cores: pool_size = (4 * 2) + reserve = 13-25
   2. For 7.6GB RAM: shared_buffers = 2GB (25% of RAM)
   3. work_mem per connection: 256MB / 25 = ~10MB per query
   4. max_connections should be < (pool_size * num_services)

⚠️ To apply PostgreSQL changes:
   docker restart kloud-postgres

🔍 To verify pooling:
   SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
   SELECT count(*) FROM pg_stat_activity WHERE state = 'idle in transaction';

RECOMMENDATIONS_EOF

echo ""
echo "============================================================"
echo "✅ OPTIMIZATION COMPLETE"
echo "============================================================"
echo ""
echo "📝 Files created:"
echo "   - /tmp/pgbouncer.ini (copy to container if using PgBouncer)"
echo "   - /tmp/userlist.txt (PgBouncer authentication)"
echo ""
echo "🚀 Next steps:"
echo "   1. Review recommendations above"
echo "   2. Restart PostgreSQL: docker restart kloud-postgres"
echo "   3. Monitor connections: watch -n 1 'docker exec kloud-postgres psql -U postgres -c \"SELECT count(*) FROM pg_stat_activity;\"'"
echo ""

