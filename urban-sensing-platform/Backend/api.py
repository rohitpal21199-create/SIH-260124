"""
Main API Server - Urban Sensing Platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from database import Database
from analytics import Analytics
from alerts import AlertSystem
from reports import ReportGenerator

# ============================================
# Initialize
# ============================================
app = FastAPI(title="Urban Sensing Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()
analytics = Analytics(db)
alert_system = AlertSystem()
reporter = ReportGenerator(db, analytics)

# ============================================
# Models
# ============================================
class Event(BaseModel):
    timestamp: str
    bus_id: str
    event_type: str
    latitude: float
    longitude: float
    objects: Optional[List[str]] = []
    road_defects: Optional[List[str]] = []
    location: Optional[str] = None

# ============================================
# API Endpoints
# ============================================

@app.get("/")
def root():
    return {"message": "Urban Sensing Platform API", "status": "running"}

@app.post("/api/events")
async def add_event(event: Event):
    event_dict = event.dict()
    if not event.location:
        event_dict['location'] = f"{event.latitude}, {event.longitude}"
    
    db.add_event(event_dict)
    alerts = alert_system.check_alerts([event_dict])
    
    return {
        "status": "success",
        "event_id": len(db.read_events()) - 1,
        "alerts_generated": len(alerts)
    }

@app.get("/api/events")
def get_events(limit: int = 100, event_type: Optional[str] = None, bus_id: Optional[str] = None):
    return db.get_events(limit, event_type, bus_id)

@app.get("/api/events/latest")
def get_latest_events():
    return db.get_events(limit=10)

@app.get("/api/stats")
def get_stats():
    return db.get_stats()

@app.get("/api/analytics/daily")
def get_daily_analytics(days: int = 7):
    return analytics.get_daily_summary(days)

@app.get("/api/analytics/hourly")
def get_hourly_analytics():
    return analytics.get_hourly_pattern()

@app.get("/api/analytics/insights")
def get_insights():
    return analytics.get_insights()

@app.get("/api/alerts")
def get_alerts(severity: Optional[str] = None):
    if severity:
        return alert_system.get_alerts_by_severity(severity)
    return alert_system.get_active_alerts()

@app.get("/api/alerts/summary")
def get_alert_summary():
    return alert_system.get_alert_summary()

@app.post("/api/alerts/resolve/{alert_id}")
def resolve_alert(alert_id: int):
    result = alert_system.resolve_alert(alert_id)
    if result:
        return {"status": "success", "message": f"Alert {alert_id} resolved"}
    return {"status": "error", "message": "Alert not found"}

@app.get("/api/reports/summary")
def get_summary_report():
    return reporter.generate_summary_report()

@app.get("/api/reports/defects")
def get_defect_report():
    return reporter.generate_defect_report()

@app.get("/api/reports/objects")
def get_object_report():
    return reporter.generate_object_report()

@app.get("/api/export/json")
def export_json():
    return db.read_events()

@app.get("/api/export/csv")
def export_csv():
    filename = analytics.export_csv()
    return FileResponse(filename, media_type='text/csv', filename='data_export.csv')

@app.get("/api/heatmap")
def get_heatmap_data():
    return analytics.get_defect_heatmap()

@app.get("/api/buses")
def get_buses():
    return db.get_bus_routes()

# ============================================
# Run
# ============================================
if __name__ == "__main__":
    import uvicorn
    print("🚍 Starting Urban Sensing Platform API...")
    print("📡 API running at: http://localhost:8000")
    print("📋 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)