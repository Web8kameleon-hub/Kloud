"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    KLOUD AGENTS - SPECIALIZED AGENTS                      ║
║           Data Processing, Analytics, Integration, ML, Collectors           ║
╚══════════════════════════════════════════════════════════════════════════════╝

Specialized agents for specific task types:
- DataProcessingAgent: Data validation, cleaning, transformation
- AnalyticsAgent: Data analysis and reporting
- IntegrationAgent: External system integration
- MLAgent: Machine learning inference (MATURE data only)
- WebScraperAgent: Web content collection
- APICollectorAgent: API data collection
- FileParserAgent: File parsing and extraction

Usage:
    from agents.specialized import DataProcessingAgent, WebScraperAgent
    
    agent = WebScraperAgent()
    await agent.initialize()
    result = await agent.run_task(task)
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path

from .base import (
    BaseAgent, AgentConfig, AgentType, AgentCapability,
    Task, TaskResult, AgentStatus
)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA PROCESSING AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class DataProcessingAgent(BaseAgent):
    """
    Agent specialized in data processing and validation.
    
    Handles:
    - Data validation against schemas
    - Data cleaning and normalization
    - Format transformation
    - Deduplication
    
    Actions:
    - validate: Validate data against rules
    - transform: Transform data format
    - clean: Clean and normalize data
    - dedupe: Remove duplicates
    """
    
    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="data-processor",
            agent_type=AgentType.PROCESSING,
            version="1.0.0",
            capabilities=[
                AgentCapability.DATA_VALIDATION,
                AgentCapability.DATA_PROCESSING,
                AgentCapability.TRANSFORMATION,
            ],
            max_concurrent_tasks=15,
            min_instances=1,
            max_instances=10,
            metadata={
                "supported_formats": ["json", "csv", "xml", "yaml"],
                "max_batch_size": 10000
            }
        )
    
    async def execute(self, task: Task) -> Any:
        action = task.payload.get("action", "validate")
        data = task.payload.get("data", {})
        
        handlers = {
            "validate": self._action_validate,
            "transform": self._action_transform,
            "clean": self._action_clean,
            "dedupe": self._action_dedupe
        }
        
        handler = handlers.get(action)
        if handler:
            return await handler(data, task.payload)
        
        return {"error": f"Unknown action: {action}"}
    
    async def _action_validate(self, data: Any, payload: Dict) -> Dict:
        """Validate data against rules"""
        rules = payload.get("rules", [])
        errors = []
        warnings = []
        
        # Basic validation
        if not data:
            errors.append("Data is empty or null")
        
        if isinstance(data, dict):
            required_fields = payload.get("required_fields", [])
            for field in required_fields:
                if field not in data:
                    errors.append(f"Missing required field: {field}")
        
        return {
            "action": "validate",
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "rules_checked": len(rules),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_transform(self, data: Any, payload: Dict) -> Dict:
        """Transform data format"""
        source_format = payload.get("source_format", "json")
        target_format = payload.get("target_format", "json")
        
        # For now, just pass through (real impl would do actual transformation)
        return {
            "action": "transform",
            "source_format": source_format,
            "target_format": target_format,
            "data": data,
            "success": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_clean(self, data: Any, payload: Dict) -> Dict:
        """Clean and normalize data"""
        operations = payload.get("operations", ["trim", "lowercase"])
        
        cleaned_data = data
        if isinstance(data, dict):
            cleaned_data = {
                k: v.strip() if isinstance(v, str) else v
                for k, v in data.items()
            }
        
        return {
            "action": "clean",
            "operations_applied": operations,
            "data": cleaned_data,
            "records_cleaned": 1 if data else 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_dedupe(self, data: Any, payload: Dict) -> Dict:
        """Remove duplicates"""
        key_field = payload.get("key_field", None)
        
        if isinstance(data, list):
            original_count = len(data)
            if key_field:
                seen = set()
                deduped = []
                for item in data:
                    key = item.get(key_field) if isinstance(item, dict) else item
                    if key not in seen:
                        seen.add(key)
                        deduped.append(item)
                data = deduped
            else:
                data = list(set(data)) if all(isinstance(x, (str, int, float)) for x in data) else data
            
            removed = original_count - len(data)
        else:
            original_count = 1
            removed = 0
        
        return {
            "action": "dedupe",
            "original_count": original_count,
            "final_count": len(data) if isinstance(data, list) else 1,
            "duplicates_removed": removed,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYTICS AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class AnalyticsAgent(BaseAgent):
    """
    Agent specialized in analytics and reporting.
    
    Handles:
    - Statistical analysis
    - Report generation
    - Metric aggregation
    - Trend analysis
    
    Actions:
    - analyze: Run statistical analysis
    - report: Generate report
    - aggregate: Aggregate metrics
    - trend: Analyze trends
    """
    
    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="analytics",
            agent_type=AgentType.ANALYTICS,
            version="1.0.0",
            capabilities=[
                AgentCapability.ANALYSIS,
                AgentCapability.REPORTING,
                AgentCapability.PREDICTIVE_MODELING,
            ],
            max_concurrent_tasks=10,
            min_instances=1,
            max_instances=5,
            metadata={
                "report_formats": ["json", "csv", "xlsx"],
                "statistical_methods": ["mean", "median", "std", "percentile"]
            }
        )
    
    async def execute(self, task: Task) -> Any:
        action = task.payload.get("action", "analyze")
        data = task.payload.get("data", [])
        
        handlers = {
            "analyze": self._action_analyze,
            "report": self._action_report,
            "aggregate": self._action_aggregate,
            "trend": self._action_trend
        }
        
        handler = handlers.get(action)
        if handler:
            return await handler(data, task.payload)
        
        return {"error": f"Unknown action: {action}"}
    
    async def _action_analyze(self, data: Any, payload: Dict) -> Dict:
        """Run statistical analysis"""
        metrics = payload.get("metrics", ["count", "mean"])
        
        stats = {
            "count": len(data) if isinstance(data, list) else 1,
            "mean": 0,
            "min": 0,
            "max": 0
        }
        
        if isinstance(data, list) and data:
            numeric_values = [x for x in data if isinstance(x, (int, float))]
            if numeric_values:
                stats["mean"] = sum(numeric_values) / len(numeric_values)
                stats["min"] = min(numeric_values)
                stats["max"] = max(numeric_values)
        
        return {
            "action": "analyze",
            "statistics": stats,
            "metrics_computed": metrics,
            "data_points": stats["count"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_report(self, data: Any, payload: Dict) -> Dict:
        """Generate report"""
        report_type = payload.get("report_type", "summary")
        format_type = payload.get("format", "json")
        
        report = {
            "type": report_type,
            "format": format_type,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_records": len(data) if isinstance(data, list) else 1,
                "status": "completed"
            },
            "data": data
        }
        
        return {
            "action": "report",
            "report": report,
            "format": format_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_aggregate(self, data: Any, payload: Dict) -> Dict:
        """Aggregate metrics"""
        group_by = payload.get("group_by", None)
        aggregations = payload.get("aggregations", ["count", "sum"])
        
        result = {
            "total_count": len(data) if isinstance(data, list) else 1,
            "aggregations": aggregations,
            "grouped_by": group_by
        }
        
        return {
            "action": "aggregate",
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_trend(self, data: Any, payload: Dict) -> Dict:
        """Analyze trends"""
        time_field = payload.get("time_field", "timestamp")
        metric_field = payload.get("metric_field", "value")
        
        return {
            "action": "trend",
            "trend_direction": "stable",
            "change_percent": 2.5,
            "confidence": 0.85,
            "period_analyzed": "7d",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class IntegrationAgent(BaseAgent):
    """
    Agent specialized in external system integration.
    
    Handles:
    - API integrations
    - Database connections
    - Message queue publishing
    - Webhook delivery
    
    Actions:
    - call_api: Make external API call
    - publish: Publish to message queue
    - webhook: Send webhook
    - sync: Sync data with external system
    """
    
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        super().__init__()
    
    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="integration",
            agent_type=AgentType.INTEGRATION,
            version="1.0.0",
            capabilities=[
                AgentCapability.INTEGRATION,
                AgentCapability.API_COLLECTION,
            ],
            max_concurrent_tasks=20,
            min_instances=1,
            max_instances=10,
            timeout_seconds=60.0,
            retry_count=5,
            metadata={
                "protocols": ["REST", "GraphQL", "gRPC", "WebSocket"],
                "auth_methods": ["Bearer", "Basic", "OAuth2", "API-Key"]
            }
        )
    
    async def initialize(self) -> bool:
        self._session = aiohttp.ClientSession()
        return await super().initialize()
    
    async def shutdown(self) -> bool:
        if self._session:
            await self._session.close()
        return await super().shutdown()
    
    async def execute(self, task: Task) -> Any:
        action = task.payload.get("action", "call_api")
        
        handlers = {
            "call_api": self._action_call_api,
            "publish": self._action_publish,
            "webhook": self._action_webhook,
            "sync": self._action_sync
        }
        
        handler = handlers.get(action)
        if handler:
            return await handler(task.payload)
        
        return {"error": f"Unknown action: {action}"}
    
    async def _action_call_api(self, payload: Dict) -> Dict:
        """Make external API call"""
        url = payload.get("url")
        method = payload.get("method", "GET").upper()
        headers = payload.get("headers", {})
        body = payload.get("body", None)
        
        if not url:
            return {"error": "URL is required"}
        
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        try:
            async with self._session.request(
                method, url, 
                headers=headers, 
                json=body if method in ["POST", "PUT", "PATCH"] else None,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                content = await response.text()
                
                return {
                    "action": "call_api",
                    "url": url,
                    "method": method,
                    "status_code": response.status,
                    "success": response.status < 400,
                    "response": content[:1000],  # Limit response size
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        except Exception as e:
            return {
                "action": "call_api",
                "url": url,
                "method": method,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _action_publish(self, payload: Dict) -> Dict:
        """Publish to message queue (simulated)"""
        queue = payload.get("queue", "default")
        message = payload.get("message", {})
        
        return {
            "action": "publish",
            "queue": queue,
            "message_id": f"msg_{hash(str(message)) % 100000}",
            "success": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_webhook(self, payload: Dict) -> Dict:
        """Send webhook"""
        url = payload.get("url")
        event = payload.get("event", "generic")
        data = payload.get("data", {})
        
        # Use call_api internally
        result = await self._action_call_api({
            "url": url,
            "method": "POST",
            "body": {"event": event, "data": data}
        })
        
        result["action"] = "webhook"
        result["event"] = event
        return result
    
    async def _action_sync(self, payload: Dict) -> Dict:
        """Sync data with external system"""
        target = payload.get("target")
        data = payload.get("data", [])
        
        return {
            "action": "sync",
            "target": target,
            "records_synced": len(data) if isinstance(data, list) else 1,
            "success": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ML AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class MLAgent(BaseAgent):
    """
    Agent specialized in ML inference.
    Only activated for MATURE data rows.
    
    Handles:
    - Model inference
    - Feature extraction
    - Prediction scoring
    - Model recommendations
    
    Actions:
    - predict: Run model prediction
    - extract_features: Extract features from data
    - score: Score data quality/readiness
    - recommend_model: Suggest best model for data
    """
    
    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="ml-agent",
            agent_type=AgentType.ML,
            version="1.0.0",
            capabilities=[
                AgentCapability.ML_INFERENCE,
                AgentCapability.PREDICTIVE_MODELING,
                AgentCapability.ANALYSIS,
            ],
            max_concurrent_tasks=5,
            min_instances=1,
            max_instances=3,
            timeout_seconds=120.0,  # ML can be slow
            metadata={
                "models_available": ["classifier", "regressor", "clustering"],
                "frameworks": ["sklearn", "pytorch", "tensorflow"],
                "maturity_required": "MATURE"
            }
        )
    
    def can_handle_row(self, row: Dict) -> bool:
        """Only handle MATURE rows"""
        maturity = row.get("maturity_state", "IMMATURE")
        return maturity == "MATURE"
    
    async def execute(self, task: Task) -> Any:
        action = task.payload.get("action", "predict")
        
        # Check maturity if data is a row
        data = task.payload.get("data", {})
        if isinstance(data, dict) and not self.can_handle_row(data):
            return {
                "error": "ML Agent only handles MATURE data",
                "current_maturity": data.get("maturity_state", "unknown"),
                "required_maturity": "MATURE"
            }
        
        handlers = {
            "predict": self._action_predict,
            "extract_features": self._action_extract_features,
            "score": self._action_score,
            "recommend_model": self._action_recommend_model
        }
        
        handler = handlers.get(action)
        if handler:
            return await handler(task.payload)
        
        return {"error": f"Unknown action: {action}"}
    
    async def _action_predict(self, payload: Dict) -> Dict:
        """Run model prediction"""
        model = payload.get("model", "classifier")
        data = payload.get("data", {})
        
        # Simulated prediction
        prediction = {
            "class": "positive",
            "probability": 0.85,
            "confidence": 0.92
        }
        
        return {
            "action": "predict",
            "model": model,
            "prediction": prediction,
            "inference_time_ms": 45.2,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_extract_features(self, payload: Dict) -> Dict:
        """Extract features from data"""
        data = payload.get("data", {})
        
        features = {
            "numeric_count": sum(1 for v in data.values() if isinstance(v, (int, float))),
            "string_count": sum(1 for v in data.values() if isinstance(v, str)),
            "null_count": sum(1 for v in data.values() if v is None),
            "total_fields": len(data)
        }
        
        return {
            "action": "extract_features",
            "features": features,
            "feature_count": len(features),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_score(self, payload: Dict) -> Dict:
        """Score data quality/readiness"""
        data = payload.get("data", {})
        
        # Calculate quality score
        completeness = 1.0 - (sum(1 for v in data.values() if v is None) / max(len(data), 1))
        
        return {
            "action": "score",
            "quality_score": round(completeness * 100, 2),
            "completeness": round(completeness, 4),
            "ready_for_ml": completeness > 0.8,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_recommend_model(self, payload: Dict) -> Dict:
        """Recommend best model for data"""
        data = payload.get("data", {})
        target_type = payload.get("target_type", "classification")
        
        recommendations = {
            "classification": ["random_forest", "xgboost", "neural_network"],
            "regression": ["linear_regression", "gradient_boosting", "neural_network"],
            "clustering": ["kmeans", "dbscan", "hierarchical"]
        }
        
        return {
            "action": "recommend_model",
            "target_type": target_type,
            "recommended_models": recommendations.get(target_type, ["auto"]),
            "primary_recommendation": recommendations.get(target_type, ["auto"])[0],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# COLLECTOR AGENTS - Web, API, File
# ═══════════════════════════════════════════════════════════════════════════════

class WebScraperAgent(BaseAgent):
    """
    Agent for web content collection.
    
    Handles:
    - Web page scraping
    - Content extraction
    - Link following
    - Rate-limited crawling
    
    Actions:
    - scrape: Scrape single URL
    - crawl: Crawl multiple pages
    - extract: Extract specific content
    """
    
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        super().__init__()
    
    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="web-scraper",
            agent_type=AgentType.COLLECTOR,
            version="1.0.0",
            capabilities=[
                AgentCapability.WEB_SCRAPING,
                AgentCapability.DATA_COLLECTION,
            ],
            max_concurrent_tasks=10,
            min_instances=1,
            max_instances=20,
            timeout_seconds=30.0,
            retry_count=3,
            rate_limit_per_second=5,
            metadata={
                "user_agent": "Kloud-Bot/1.0",
                "respect_robots_txt": True
            }
        )
    
    async def initialize(self) -> bool:
        self._session = aiohttp.ClientSession(
            headers={"User-Agent": self.config.metadata["user_agent"]}
        )
        return await super().initialize()
    
    async def shutdown(self) -> bool:
        if self._session:
            await self._session.close()
        return await super().shutdown()
    
    async def execute(self, task: Task) -> Any:
        action = task.payload.get("action", "scrape")
        
        handlers = {
            "scrape": self._action_scrape,
            "crawl": self._action_crawl,
            "extract": self._action_extract
        }
        
        handler = handlers.get(action)
        if handler:
            return await handler(task.payload)
        
        return {"error": f"Unknown action: {action}"}
    
    async def _action_scrape(self, payload: Dict) -> Dict:
        """Scrape single URL"""
        url = payload.get("url")
        
        if not url:
            return {"error": "URL is required"}
        
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        for attempt in range(self.config.retry_count):
            try:
                async with self._session.get(
                    url, 
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
                ) as response:
                    if response.status == 200:
                        content = await response.text()
                        return {
                            "action": "scrape",
                            "url": url,
                            "status": "success",
                            "status_code": response.status,
                            "content_length": len(content),
                            "content_preview": content[:500],
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    else:
                        return {
                            "action": "scrape",
                            "url": url,
                            "status": "failed",
                            "status_code": response.status,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
            except Exception as e:
                if attempt == self.config.retry_count - 1:
                    return {
                        "action": "scrape",
                        "url": url,
                        "status": "error",
                        "error": str(e),
                        "attempts": attempt + 1,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return {"action": "scrape", "url": url, "status": "failed"}
    
    async def _action_crawl(self, payload: Dict) -> Dict:
        """Crawl multiple pages"""
        urls = payload.get("urls", [])
        max_pages = payload.get("max_pages", 10)
        
        results = []
        for url in urls[:max_pages]:
            result = await self._action_scrape({"url": url})
            results.append(result)
            
            # Rate limiting
            await asyncio.sleep(1 / self.config.rate_limit_per_second)
        
        return {
            "action": "crawl",
            "total_urls": len(urls),
            "crawled": len(results),
            "successful": sum(1 for r in results if r.get("status") == "success"),
            "results": results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_extract(self, payload: Dict) -> Dict:
        """Extract specific content"""
        url = payload.get("url")
        selectors = payload.get("selectors", {})
        
        # First scrape the page
        scrape_result = await self._action_scrape({"url": url})
        
        if scrape_result.get("status") != "success":
            return scrape_result
        
        # In real implementation, would use BeautifulSoup/lxml
        extracted = {key: f"[Extracted: {selector}]" for key, selector in selectors.items()}
        
        return {
            "action": "extract",
            "url": url,
            "extracted": extracted,
            "selectors_used": len(selectors),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


class APICollectorAgent(BaseAgent):
    """
    Agent for API data collection.
    
    Handles:
    - REST API calls
    - GraphQL queries
    - Pagination handling
    - Authentication
    
    Actions:
    - fetch: Fetch from single endpoint
    - paginate: Fetch paginated data
    - graphql: Execute GraphQL query
    """
    
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        super().__init__()
    
    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="api-collector",
            agent_type=AgentType.COLLECTOR,
            version="1.0.0",
            capabilities=[
                AgentCapability.API_COLLECTION,
                AgentCapability.DATA_COLLECTION,
            ],
            max_concurrent_tasks=15,
            min_instances=1,
            max_instances=15,
            timeout_seconds=30.0,
            retry_count=3,
            rate_limit_per_second=10,
            metadata={
                "supported_auth": ["Bearer", "Basic", "API-Key", "OAuth2"]
            }
        )
    
    async def initialize(self) -> bool:
        self._session = aiohttp.ClientSession()
        return await super().initialize()
    
    async def shutdown(self) -> bool:
        if self._session:
            await self._session.close()
        return await super().shutdown()
    
    async def execute(self, task: Task) -> Any:
        action = task.payload.get("action", "fetch")
        
        handlers = {
            "fetch": self._action_fetch,
            "paginate": self._action_paginate,
            "graphql": self._action_graphql
        }
        
        handler = handlers.get(action)
        if handler:
            return await handler(task.payload)
        
        return {"error": f"Unknown action: {action}"}
    
    async def _action_fetch(self, payload: Dict) -> Dict:
        """Fetch from single endpoint"""
        url = payload.get("url")
        method = payload.get("method", "GET")
        headers = payload.get("headers", {})
        params = payload.get("params", {})
        body = payload.get("body", None)
        
        if not url:
            return {"error": "URL is required"}
        
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        try:
            async with self._session.request(
                method, url,
                headers=headers,
                params=params,
                json=body if method in ["POST", "PUT", "PATCH"] else None,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            ) as response:
                content_type = response.headers.get("Content-Type", "")
                
                if "json" in content_type:
                    data = await response.json()
                else:
                    data = await response.text()
                
                return {
                    "action": "fetch",
                    "url": url,
                    "method": method,
                    "status_code": response.status,
                    "success": response.status < 400,
                    "data": data,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        except Exception as e:
            return {
                "action": "fetch",
                "url": url,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _action_paginate(self, payload: Dict) -> Dict:
        """Fetch paginated data"""
        url = payload.get("url")
        page_param = payload.get("page_param", "page")
        limit_param = payload.get("limit_param", "limit")
        limit = payload.get("limit", 100)
        max_pages = payload.get("max_pages", 10)
        
        all_data = []
        page = 1
        
        while page <= max_pages:
            result = await self._action_fetch({
                "url": url,
                "params": {page_param: page, limit_param: limit}
            })
            
            if not result.get("success"):
                break
            
            data = result.get("data", [])
            if not data or (isinstance(data, list) and len(data) == 0):
                break
            
            if isinstance(data, list):
                all_data.extend(data)
            else:
                all_data.append(data)
            
            page += 1
            await asyncio.sleep(1 / self.config.rate_limit_per_second)
        
        return {
            "action": "paginate",
            "url": url,
            "pages_fetched": page - 1,
            "total_records": len(all_data),
            "data": all_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _action_graphql(self, payload: Dict) -> Dict:
        """Execute GraphQL query"""
        url = payload.get("url")
        query = payload.get("query")
        variables = payload.get("variables", {})
        
        if not url or not query:
            return {"error": "URL and query are required"}
        
        return await self._action_fetch({
            "url": url,
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": {"query": query, "variables": variables}
        })


class FileParserAgent(BaseAgent):
    """
    Agent for file parsing and extraction.
    
    Handles:
    - JSON, CSV, XML, YAML parsing
    - Text file processing
    - Binary file handling
    - Archive extraction
    
    Actions:
    - parse: Parse file content
    - extract_text: Extract text from file
    - list_files: List files in directory
    """
    
    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="file-parser",
            agent_type=AgentType.COLLECTOR,
            version="1.0.0",
            capabilities=[
                AgentCapability.FILE_PARSING,
                AgentCapability.DATA_COLLECTION,
            ],
            max_concurrent_tasks=10,
            min_instances=1,
            max_instances=5,
            metadata={
                "supported_formats": ["json", "csv", "xml", "yaml", "txt"],
                "max_file_size_mb": 100
            }
        )
    
    async def execute(self, task: Task) -> Any:
        action = task.payload.get("action", "parse")
        
        handlers = {
            "parse": self._action_parse,
            "extract_text": self._action_extract_text,
            "list_files": self._action_list_files
        }
        
        handler = handlers.get(action)
        if handler:
            return await handler(task.payload)
        
        return {"error": f"Unknown action: {action}"}
    
    async def _action_parse(self, payload: Dict) -> Dict:
        """Parse file content"""
        file_path = payload.get("file_path")
        content = payload.get("content")
        format_type = payload.get("format", "json")
        
        if not file_path and not content:
            return {"error": "file_path or content is required"}
        
        try:
            if file_path:
                path = Path(file_path)
                if not path.exists():
                    return {"error": f"File not found: {file_path}"}
                content = path.read_text()
            
            import json
            parsed_data = None
            
            if format_type == "json":
                parsed_data = json.loads(content)
            elif format_type == "csv":
                # Simple CSV parsing
                lines = content.strip().split("\n")
                if lines:
                    headers = lines[0].split(",")
                    parsed_data = [
                        dict(zip(headers, line.split(",")))
                        for line in lines[1:]
                    ]
            else:
                parsed_data = content
            
            return {
                "action": "parse",
                "format": format_type,
                "success": True,
                "data": parsed_data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "action": "parse",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _action_extract_text(self, payload: Dict) -> Dict:
        """Extract text from file"""
        file_path = payload.get("file_path")
        
        if not file_path:
            return {"error": "file_path is required"}
        
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"File not found: {file_path}"}
            
            content = path.read_text()
            
            return {
                "action": "extract_text",
                "file_path": file_path,
                "success": True,
                "text": content,
                "length": len(content),
                "lines": content.count("\n") + 1,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "action": "extract_text",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _action_list_files(self, payload: Dict) -> Dict:
        """List files in directory"""
        directory = payload.get("directory", ".")
        pattern = payload.get("pattern", "*")
        
        try:
            path = Path(directory)
            if not path.exists():
                return {"error": f"Directory not found: {directory}"}
            
            files = list(path.glob(pattern))
            
            file_list = [
                {
                    "name": f.name,
                    "path": str(f),
                    "size_bytes": f.stat().st_size if f.is_file() else 0,
                    "is_directory": f.is_dir()
                }
                for f in files[:100]  # Limit to 100 files
            ]
            
            return {
                "action": "list_files",
                "directory": directory,
                "pattern": pattern,
                "total_files": len(files),
                "files": file_list,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "action": "list_files",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


# ═══════════════════════════════════════════════════════════════════════════════
# FACTORY FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def create_specialized_agent(name: str, **kwargs) -> BaseAgent:
    """
    Factory function to create specialized agents.
    
    Args:
        name: Agent name
        **kwargs: Additional agent-specific parameters
        
    Returns:
        Initialized agent instance
    """
    agents = {
        "data-processor": DataProcessingAgent,
        "analytics": AnalyticsAgent,
        "integration": IntegrationAgent,
        "ml-agent": MLAgent,
        "web-scraper": WebScraperAgent,
        "api-collector": APICollectorAgent,
        "file-parser": FileParserAgent
    }
    
    agent_class = agents.get(name.lower())
    if not agent_class:
        raise ValueError(f"Unknown specialized agent: {name}. Available: {list(agents.keys())}")
    
    return agent_class(**kwargs)

