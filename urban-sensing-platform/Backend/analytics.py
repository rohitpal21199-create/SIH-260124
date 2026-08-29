"""
Analytics Engine - Without Pandas
"""

import json
from datetime import datetime

class Analytics:
    def __init__(self, database):
        self.db = database
    
    def get_daily_summary(self, days: int = 7):
        events = self.db.read_events()
        if not events:
            return {}
        
        date_counts = {}
        for e in events[-100:]:
            date = e.get('timestamp', '')[:10]
            if date:
                date_counts[date] = date_counts.get(date, 0) + 1
        
        return {
            'dates': list(date_counts.keys()),
            'counts': list(date_counts.values())
        }
    
    def get_hourly_pattern(self):
        events = self.db.read_events()
        if not events:
            return {}
        
        hour_counts = {}
        for h in range(24):
            hour_counts[h] = 0
        
        for e in events:
            try:
                hour = datetime.fromisoformat(e.get('timestamp', '')).hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            except:
                continue
        
        return {
            'hours': list(hour_counts.keys()),
            'counts': list(hour_counts.values())
        }
    
    def get_defect_heatmap(self):
        return self.db.get_defects()
    
    def get_insights(self):
        stats = self.db.get_stats()
        object_counts = self.db.get_objects_count()
        
        return {
            'summary': f"Total {stats['total_events']} events from {stats['unique_buses']} buses",
            'top_objects': sorted(object_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'total_objects': stats['total_objects'],
            'total_defects': stats['total_defects'],
            'last_update': stats['timestamp']
        }
    
    def export_csv(self, filename="data/export.csv"):
        events = self.db.read_events()
        if not events:
            return filename
        
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=events[0].keys())
            writer.writeheader()
            writer.writerows(events)
        return filename

# Test
if __name__ == "__main__":
    from database import Database
    db = Database()
    analytics = Analytics(db)
    print("✅ Analytics test passed!")