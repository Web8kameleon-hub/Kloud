# Kameleon Life API Root Endpoint
# Insert this block into apps/api/main.py near the API root section.
#
# @app.get("/api")
# async def api_root():
#     """
#     Kameleon Life API Root
#     Returns available endpoints and API information
#     """
#     return {
#         "name": "Kameleon Life API",
#         "version": "2.0.0",
#         "status": "operational",
#         "documentation": "https://kameleon.life",
#         "endpoints": {
#             "health": "/health",
#             "status": "/status",
#             "system_status": "/api/system-status",
#             "asi": {
#                 "status": "/api/asi/status",
#                 "health": "/api/asi/health",
#                 "alba_metrics": "/api/asi/alba/metrics",
#                 "albi_metrics": "/api/asi/albi/metrics"
#             },
#             "brain": "/brain",
#             "eeg": {
#                 "analysis": "/api/albi/eeg/analysis",
#                 "waves": "/api/albi/eeg/waves",
#                 "quality": "/api/albi/eeg/quality"
#             },
#             "spectrum": {
#                 "live": "/api/spectrum/live",
#                 "bands": "/api/spectrum/bands"
#             },
#             "monitoring": "/api/monitoring/dashboards"
#         },
#         "support": "support@kameleon.life"
#     }


