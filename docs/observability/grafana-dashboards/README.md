# Grafana Dashboard Charts

This folder contains exported Grafana charts from Kloud Cloud's Prometheus monitoring.

## Chart Inventory

### Chart 1: Memory Usage by Label Name (Bytes)
**File:** `chart1.png`  
**Type:** Bar chart  
**Metrics:** Label memory consumption  
**Key Insight:** `__name__` label uses ~52KB (dominant)

### Chart 2: Top Label Value Pair Cardinality
**File:** `chart2.png`  
**Type:** Bar chart  
**Metrics:** Unique label combinations  
**Key Insight:** `instance=localhost:9090` has 1013 pairs

### Chart 3: TSDB Time Window Timeline
**File:** `chart3.png`  
**Type:** Line chart  
**Metrics:** Data window progression  
**Key Insight:** Linear growth (stable ingestion)

### Chart 4: Top Metric Families by Series Count
**File:** `chart4.png`  
**Type:** Bar chart  
**Metrics:** Series per metric family  
**Key Insight:** `http_req_dur_bucket` leads with 130 series

### Chart 5: Label Cardinality
**File:** `chart5.png`  
**Type:** Single bar  
**Metrics:** Total unique label pairs  
**Key Insight:** 515 pairs total (low cardinality)

### Chart 6: Total Active Time Series
**File:** `chart6.png`  
**Type:** Single bar  
**Metrics:** Active series count  
**Key Insight:** 1053 series (production-ready)

---

## How to Add Charts

Since I cannot save image attachments directly, please:

1. **Save the 6 attached charts** to this folder
2. **Rename them:**
   - Memory Usage → `chart1.png`
   - Label Pair Cardinality → `chart2.png`
   - TSDB Timeline → `chart3.png`
   - Metric Families → `chart4.png`
   - Label Cardinality → `chart5.png`
   - Active Series → `chart6.png`

3. **Verify links in README.md** will display correctly on GitHub

---

**Last Updated:** December 11, 2025

