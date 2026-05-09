# 🎯 QUICK ACCESS GUIDE - KLOUD CLOUD DOCKER

**Status**: ✅ All services running and ready!

---

## 🖥️ WEB INTERFACES

| Interface | URL | Credentials | Purpose |
|-----------|-----|-------------|---------|
| **Web Dashboard** | http://localhost:3002 | Auto | Main UI |
| **Grafana** | http://localhost:3001 | admin / admin | Monitoring |
| **Prometheus** | http://localhost:9090 | - | Metrics |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin | File Storage |
| **API Docs** | http://localhost:8000/docs | - | Swagger UI |
| **API ReDoc** | http://localhost:8000/redoc | - | API Reference |

---

## 🔌 API ENDPOINTS

### Health Checks
```bash
curl http://localhost:8000/health          # API Server
curl http://localhost:5555/health          # ALBA
curl http://localhost:6666/health          # ALBI
curl http://localhost:7777/health          # JONA
curl http://localhost:9999/health          # Orchestrator
```

### Core API Operations
```bash
# Get all fitness users
curl http://localhost:8000/fitness/users

# Create new user
curl -X POST http://localhost:8000/fitness/users/profile \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","name":"User","age":30,"gender":"M","weight":75}'

# Start workout
curl -X POST http://localhost:8000/fitness/users/{user_id}/workouts

# Get API documentation
curl http://localhost:8000/docs
```

---

## 🐳 DOCKER COMMANDS

### View Running Services
```bash
cd c:\kloud-cloud
docker-compose -f docker-compose.prod.yml ps
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs --tail 100

# Specific service
docker-compose -f docker-compose.prod.yml logs -f kloud-api

# Real-time logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Restart Services
```bash
# Single service
docker-compose -f docker-compose.prod.yml restart kloud-api

# All services
docker-compose -f docker-compose.prod.yml restart

# Stop all
docker-compose -f docker-compose.prod.yml down

# Start all
docker-compose -f docker-compose.prod.yml up -d
```

### Execute Commands
```bash
# Run command in API
docker exec kloud-api python main.py

# Access PostgreSQL
docker exec -it kloud-postgres psql -U kloud -d klouddb

# Access Redis
docker exec -it kloud-redis redis-cli

# Check service logs
docker logs kloud-alba -f
```

---

## 📊 MONITORING & OBSERVABILITY

### Grafana Dashboards
1. Open: http://localhost:3001
2. Login: admin / admin
3. View pre-configured dashboards:
   - System metrics
   - Service performance
   - Database metrics

### Prometheus Queries
1. Open: http://localhost:9090
2. Query metrics:
   ```
   up{job="kloud"}
   container_memory_usage_bytes
   container_cpu_usage_seconds_total
   ```

### Service Metrics
- Request count
- Response time
- Error rate
- CPU usage
- Memory usage
- Database connections

---

## 💾 DATABASE ACCESS

### PostgreSQL
```bash
# Connect to database
docker exec -it kloud-postgres psql -U kloud -d klouddb

# Useful queries
\dt                                          # List tables
SELECT * FROM fitness_users;                 # View users
SELECT * FROM workouts;                      # View workouts
\q                                           # Exit
```

### Redis
```bash
# Connect to Redis
docker exec -it kloud-redis redis-cli

# Useful commands
PING                                         # Test connection
KEYS *                                       # List all keys
GET key_name                                 # Get value
SET key_name value                           # Set value
DEL key_name                                 # Delete key
FLUSHALL                                     # Clear all data
```

---

## 📁 STORAGE

### MinIO Access
```
Console: http://localhost:9001
Username: minioadmin
Password: minioadmin
```

### MinIO Commands
```bash
# List buckets
docker exec kloud-minio mc ls local/

# Create bucket
docker exec kloud-minio mc mb local/bucket-name

# Upload file
docker exec kloud-minio mc cp file.txt local/bucket-name/
```

---

## 🎯 QUICK SCENARIOS

### Scenario 1: Check if Everything is Running
```bash
cd c:\kloud-cloud
docker-compose -f docker-compose.prod.yml ps
```
✅ Expected: All 11 services showing "Up"

### Scenario 2: View Real-time Logs
```bash
docker-compose -f docker-compose.prod.yml logs -f
```
✅ Expected: Stream of logs from all services

### Scenario 3: Test API Connectivity
```bash
curl http://localhost:8000/docs
```
✅ Expected: Swagger UI documentation loads

### Scenario 4: Create Test User
```bash
curl -X POST http://localhost:8000/fitness/users/profile \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@kloud.com",
    "name": "Test User",
    "age": 30,
    "gender": "M",
    "weight": 75,
    "fitness_level": "beginner",
    "fitness_goal": "general_health"
  }'
```
✅ Expected: User created with ID returned

### Scenario 5: Monitor System Health
```bash
# Open Grafana
http://localhost:3001

# Login with: admin / admin

# View dashboards showing:
# - CPU usage across containers
# - Memory consumption
# - Network traffic
# - Service uptime
```

---

## ⚠️ TROUBLESHOOTING

### Service Not Starting
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs kloud-api

# Restart service
docker-compose -f docker-compose.prod.yml restart kloud-api

# Rebuild service
docker-compose -f docker-compose.prod.yml up -d --no-deps --build kloud-api
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker exec kloud-postgres pg_isready -U kloud

# Check Redis is running
docker exec kloud-redis redis-cli ping

# Reset database (careful!)
docker exec kloud-postgres psql -U kloud -d klouddb -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

### Memory Issues
```bash
# Check container memory usage
docker stats

# Prune unused volumes
docker volume prune

# Prune unused images
docker image prune -a
```

### Port Already in Use
```bash
# Find what's using the port
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

---

## 🔧 MAINTENANCE

### Regular Cleanup
```bash
# Remove stopped containers
docker container prune -f

# Remove unused images
docker image prune -a -f

# Remove unused volumes
docker volume prune -f
```

### Backup Database
```bash
# Backup PostgreSQL
docker exec kloud-postgres pg_dump -U kloud klouddb > backup.sql

# Restore from backup
docker exec -i kloud-postgres psql -U kloud klouddb < backup.sql
```

### View System Resources
```bash
# Real-time stats
docker stats

# Container info
docker inspect kloud-api | findstr -i "memory\|cpu"

# Volume info
docker volume ls
```

---

## 📞 GETTING HELP

### Check Documentation
- Fitness Module: `FITNESS_MODULE_INDEX.md`
- API Docs: `http://localhost:8000/docs`
- Integration Guide: `INTEGRATION_COMPLETE_REPORT.md`

### Check Logs
```bash
# Last 50 lines
docker-compose -f docker-compose.prod.yml logs --tail 50

# Follow logs live
docker-compose -f docker-compose.prod.yml logs -f
```

### Test Connectivity
```bash
# Test all services
docker ps -a
docker network ls
docker volume ls
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] All 11 services showing "Up" in `docker ps`
- [ ] Can access http://localhost:3002 (Web UI)
- [ ] Can access http://localhost:3001 (Grafana)
- [ ] Can access http://localhost:8000/docs (API Docs)
- [ ] API responds to `curl http://localhost:8000/health`
- [ ] PostgreSQL responds: `docker exec kloud-postgres pg_isready`
- [ ] Redis responds: `docker exec kloud-redis redis-cli ping`
- [ ] MinIO console accessible at http://localhost:9001
- [ ] Prometheus accessible at http://localhost:9090
- [ ] No critical errors in logs

---

## 🎉 SUCCESS!

All systems are running and ready to use!

**Next Steps**:
1. Open http://localhost:3002 to see the web dashboard
2. Open http://localhost:8000/docs to see the API documentation
3. Open http://localhost:3001 to see monitoring dashboards
4. Start creating fitness users and workouts!

---

**Last Updated**: December 3, 2025  
**Docker Compose File**: docker-compose.prod.yml  
**Status**: ✅ ALL SYSTEMS OPERATIONAL

