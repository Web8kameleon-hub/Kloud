# 🚀 Research Data Ecosystem - Quick Start Guide

> **Get up and running in 5 minutes!**

## 📋 Prerequisites Checklist

- [ ] Python 3.10+
- [ ] Docker Desktop installed and running
- [ ] Git installed
- [ ] API keys ready (see below)

## 🔑 Required API Keys (Free Tiers)

1. **PubMed** (Optional but recommended): https://www.ncbi.nlm.nih.gov/account/settings/
2. **OpenWeatherMap**: https://openweathermap.org/api (Free tier: 60 calls/min)
3. **NewsAPI**: https://newsapi.org/register (Free tier: 100 calls/day)
4. **Guardian**: https://open-platform.theguardian.com/access/ (Free tier available)

## ⚡ 5-Minute Setup

### Step 1: Clone & Navigate (30 seconds)

```bash
cd c:\kloud-cloud
```

### Step 2: Install Python Dependencies (2 minutes)

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements-research.txt
```

### Step 3: Configure Environment (1 minute)

```powershell
# Copy environment template
copy .env.research.example .env

# Edit .env and add your API keys
notepad .env
```

**Minimum required in `.env`:**
```env
# You can use demo keys for testing, but get real keys for production
OPENWEATHER_API_KEY=demo
NEWSAPI_KEY=demo
GUARDIAN_API_KEY=test
PUBMED_API_KEY=  # Leave empty for testing (limited rate)
```

### Step 4: Start Infrastructure (2 minutes)

```powershell
# Start all services (PostgreSQL, MongoDB, Elasticsearch, etc.)
docker-compose -f docker-compose.research.yml up -d

# Wait for services to be healthy (30 seconds)
Start-Sleep -Seconds 30

# Verify services are running
docker-compose -f docker-compose.research.yml ps
```

Expected output:
```
NAME                STATUS              PORTS
postgres            Up (healthy)        5432
mongodb             Up (healthy)        27017
elasticsearch       Up (healthy)        9200
prometheus          Up (healthy)        9090
grafana             Up (healthy)        3000
```

### Step 5: Launch Jupyter Notebook (30 seconds)

```powershell
# Start Jupyter
jupyter notebook Research_Data_Ecosystem_Integration.ipynb
```

Your browser will open automatically at `http://localhost:8888`

## 🎯 First Run: Execute the Notebook

### Quick Execution (Run all cells)

1. In Jupyter, click **Cell** → **Run All**
2. Watch as the notebook:
   - ✅ Connects to databases
   - ✅ Fetches papers from PubMed (5 papers)
   - ✅ Fetches papers from ArXiv (5 papers)
   - ✅ Stores data in PostgreSQL, MongoDB, Elasticsearch
   - ✅ Fetches weather data for 3 cities
   - ✅ Fetches news articles
   - ✅ Creates 5 interactive visualizations
   - ✅ Generates Prometheus metrics
   - ✅ Runs test suite

**Expected Runtime**: 2-3 minutes (depending on internet speed)

### Step-by-Step Execution (Recommended for first time)

Execute cells in order:

1. **Cells 1-3**: Environment setup (imports)
2. **Cells 4-5**: Database connections (should see ✅ for each)
3. **Cells 6-7**: Fetch scientific papers (PubMed + ArXiv)
4. **Cells 8-9**: Store papers in databases
5. **Cells 10-11**: Fetch weather data
6. **Cells 12-13**: Fetch news articles
7. **Cells 14-15**: Create visualizations
8. **Cells 16-17**: Generate Prometheus metrics
9. **Cells 18-21**: View Docker & CI/CD configs
10. **Cell 23**: Run test suite
11. **Cell 24**: Read summary

## 📊 Verify Everything Works

### Check Databases

```powershell
# PostgreSQL
docker exec -it $(docker ps -qf "name=postgres") psql -U researcher -d research_db -c "SELECT COUNT(*) FROM research_papers;"

# MongoDB
docker exec -it $(docker ps -qf "name=mongodb") mongosh --eval "db.papers.count()"

# Elasticsearch
curl http://localhost:9200/research_papers/_count
```

Expected: ~10 papers (5 PubMed + 5 ArXiv)

### Check Monitoring

```powershell
# Prometheus metrics
curl http://localhost:9090/api/v1/query?query=research_papers_collected_total

# Grafana (open in browser)
start http://localhost:3000
# Login: admin / admin
```

### Check Trinity Services (if running)

```powershell
# Alba
curl http://localhost:5050/health

# Albi
curl http://localhost:6060/health

# Jona
curl http://localhost:7070/health

# ASI
curl http://localhost:8000/health
```

**Note**: If Trinity services aren't running, telemetry will gracefully fail (expected in development)

## 🐛 Common Issues & Quick Fixes

### Issue 1: "Port already in use"

```powershell
# Find what's using the port (e.g., 5432)
netstat -ano | findstr :5432

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or change ports in docker-compose.yml
```

### Issue 2: "Database connection failed"

```powershell
# Check if services are healthy
docker-compose -f docker-compose.research.yml ps

# View logs
docker-compose -f docker-compose.research.yml logs postgres
docker-compose -f docker-compose.research.yml logs mongodb
docker-compose -f docker-compose.research.yml logs elasticsearch

# Restart services
docker-compose -f docker-compose.research.yml restart
```

### Issue 3: "API rate limit exceeded"

**Solution**: Wait a few minutes or get real API keys. Free tiers have limits:
- PubMed: 3 requests/second (without key)
- ArXiv: 1 request/3 seconds
- OpenWeather: 60 requests/minute
- NewsAPI: 100 requests/day

### Issue 4: "ImportError: No module named 'agent_telemetry'"

```python
# Add to notebook cell before imports
import sys
sys.path.append('.')
```

### Issue 5: "Docker daemon not running"

```powershell
# Start Docker Desktop (Windows)
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Wait for Docker to start (30 seconds)
Start-Sleep -Seconds 30
```

## 📈 What to Expect

### On First Run (with demo/free API keys):

✅ **Will Work**:
- Database connections
- Data storage (PostgreSQL, MongoDB, Elasticsearch)
- Visualizations (charts, graphs)
- Prometheus metrics
- Testing suite

⚠️ **May Fail (Gracefully)**:
- API calls if rate limits exceeded
- Telemetry to Trinity services (if not running)
- Some news articles if quota exceeded

❌ **Won't Work Without Keys**:
- OpenWeatherMap (requires API key)
- NewsAPI (requires API key)
- Guardian (can use 'test' key for limited access)

### On Production Run (with real API keys + Trinity services):

✅ **Everything works**:
- All API calls
- Full telemetry to Alba/Albi/Jona
- Prometheus metrics scraped
- Grafana dashboards populated
- Complete end-to-end pipeline

## 🎓 Next Steps After First Run

### 1. Explore the Data

```powershell
# Open pgAdmin or DBeaver to explore PostgreSQL
# Connection: localhost:5432, user: researcher, db: research_db

# MongoDB Compass for MongoDB
# Connection: mongodb://localhost:27017

# Kibana for Elasticsearch (optional)
docker run -p 5601:5601 -e "ELASTICSEARCH_HOSTS=http://host.docker.internal:9200" kibana:8.11.0
```

### 2. Customize Queries

Edit notebook cells to search for different topics:

```python
# Cell 7: Change PubMed query
pubmed_papers = fetch_pubmed_papers("quantum computing", max_results=20)

# Cell 7: Change ArXiv query
arxiv_papers = fetch_arxiv_papers("deep learning", max_results=20)

# Cell 11: Change cities
cities = ["Tokyo", "Paris", "Sydney", "Toronto"]
```

### 3. Create Grafana Dashboards

1. Open Grafana: http://localhost:3000
2. Login: admin / admin
3. Add Prometheus data source: http://prometheus:9090
4. Import dashboard or create new
5. Add panels for:
   - Papers collected over time
   - Fetch duration histogram
   - Active collectors gauge
   - Telemetry success rate

### 4. Run in Production Mode

```powershell
# Set environment to production
$env:ENVIRONMENT="production"
$env:DEBUG="false"
$env:LOG_LEVEL="INFO"

# Use production compose file (if exists)
docker-compose -f docker-compose.prod.yml up -d

# Run notebook as Python script
jupyter nbconvert --to script Research_Data_Ecosystem_Integration.ipynb
python Research_Data_Ecosystem_Integration.py
```

### 5. Schedule Regular Data Collection

**Windows Task Scheduler**:
```powershell
# Create scheduled task to run daily at 2 AM
$action = New-ScheduledTaskAction -Execute "python" -Argument "c:\kloud-cloud\Research_Data_Ecosystem_Integration.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "ResearchDataCollection"
```

**Linux Cron**:
```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * cd /opt/kloud-cloud && /usr/bin/python3 Research_Data_Ecosystem_Integration.py
```

## 📚 Documentation Quick Links

- **Full Documentation**: [RESEARCH_ECOSYSTEM_README.md](RESEARCH_ECOSYSTEM_README.md)
- **Implementation Details**: [RESEARCH_ECOSYSTEM_IMPLEMENTATION_SUMMARY.md](RESEARCH_ECOSYSTEM_IMPLEMENTATION_SUMMARY.md)
- **Agent Telemetry**: [AGENT_TELEMETRY_DOCS.md](AGENT_TELEMETRY_DOCS.md)
- **Architecture**: [KLOUD_ARCHITECTURE_BASELINE_2025.md](KLOUD_ARCHITECTURE_BASELINE_2025.md)

## 🆘 Getting Help

### Documentation
```powershell
# View README
cat RESEARCH_ECOSYSTEM_README.md

# Search for specific topics
Select-String -Path RESEARCH_ECOSYSTEM_README.md -Pattern "prometheus"
```

### Logs
```powershell
# View all service logs
docker-compose -f docker-compose.research.yml logs

# View specific service
docker-compose -f docker-compose.research.yml logs postgres

# Follow logs (real-time)
docker-compose -f docker-compose.research.yml logs -f research_pipeline
```

### Health Checks
```powershell
# Check all services
docker-compose -f docker-compose.research.yml ps

# Check specific service
docker inspect $(docker ps -qf "name=postgres") | Select-String "Health"
```

### Reset Everything
```powershell
# Stop all services
docker-compose -f docker-compose.research.yml down

# Remove volumes (WARNING: deletes all data)
docker-compose -f docker-compose.research.yml down -v

# Start fresh
docker-compose -f docker-compose.research.yml up -d
```

## ✅ Success Checklist

After completing quick start, you should have:

- [ ] Python virtual environment activated
- [ ] All dependencies installed (`pip list` shows ~40 packages)
- [ ] Docker services running (6 containers)
- [ ] Jupyter notebook opened in browser
- [ ] Notebook executed successfully (all cells run without errors)
- [ ] Databases populated with papers (check with SQL/MongoDB queries)
- [ ] Visualizations displayed (5 charts visible)
- [ ] Prometheus metrics generated (check http://localhost:9090)
- [ ] Tests passed (6/6 tests green)
- [ ] Grafana accessible (http://localhost:3000)

**If all boxes checked: 🎉 You're ready for production!**

## 🚀 Production Deployment

Ready to deploy? Follow these guides:

1. **Docker Swarm**: See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
2. **Kubernetes**: See [K8S_DEPLOYMENT.md](K8S_DEPLOYMENT.md)
3. **Cloud (AWS/Azure/GCP)**: See [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)
4. **Hetzner**: See [DEPLOYMENT_GUIDE_HETZNER.md](DEPLOYMENT_GUIDE_HETZNER.md)

---

**Time to Complete**: ⏱️ 5-10 minutes  
**Difficulty**: 🟢 Beginner-friendly  
**Support**: See documentation or create issue on GitHub

Happy researching! 📚🔬

