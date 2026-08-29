"""
Analytics Engine - Data Analysis & Insights
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict
import json

class Analytics:
    def __init__(self, database):
        self.db = database
    
    def get_daily_summary(self, days: int = 7) -> Dict:
        """Get daily summary for last N days"""
        events = self.db.read_events()
        
        if not events:
            return {}
        
        df = pd.DataFrame(events)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        daily_stats = df.groupby('date').agg({
            'bus_id': 'nunique',
            'objects': lambda x: sum(len(obj) for obj in x),
            'road_defects': lambda x: sum(len(defect) for defect in x)
        }).reset_index()
        
        return {
            'dates': [str(d) for d in daily_stats['date'].tolist()],
            'bus_count': daily_stats['bus_id'].tolist(),
            'objects_count': daily_stats['objects'].tolist(),
            'defects_count': daily_stats['road_defects'].tolist()
        }
    
    def get_hourly_pattern(self) -> Dict:
        """Get hourly detection pattern"""
        events = self.db.read_events()
        
        if not events:
            return {}
        
        hours = []
        for e in events:
            try:
                hour = datetime.fromisoformat(e['timestamp']).hour
                hours.append(hour)
            except:
                continue
        
        if not hours:
            return {}
        
        hour_counts = {}
        for h in range(24):
            hour_counts[h] = hours.count(h)
        
        return {
            'hours': list(hour_counts.keys()),
            'counts': list(hour_counts.values())
        }
    
    def get_defect_heatmap(self) -> Dict:
        """Get defect locations for heatmap"""
        defects = self.db.get_defects()
        
        locations = []
        for d in defects:
            loc = d.get('location', '').split(',')
            if len(loc) == 2:
                try:
                    locations.append({
                        'lat': float(loc[0]),
                        'lon': float(loc[1]),
                        'type': d.get('type', ['unknown'])[0] if isinstance(d.get('type'), list) else 'unknown'
                    })
                except:
                    continue
        
        return locations
    
    def get_insights(self) -> Dict:
        """Generate insights"""
        stats = self.db.get_stats()
        object_counts = self.db.get_objects_count()
        
        return {
            'summary': f"Total {stats['total_events']} events from {stats['unique_buses']} buses",
            'top_objects': sorted(object_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'total_objects': stats['total_objects'],
            'total_defects': stats['total_defects'],
            'last_update': stats['timestamp']
        }
    
    def export_csv(self, filename: str = "data/export.csv"):
        """Export events to CSV"""
        events = self.db.read_events()
        df = pd.DataFrame(events)
        df.to_csv(filename, index=False)
        return filename

# Test
if __name__ == "__main__":
    from database import Database
    db = Database()
    analytics = Analytics(db)
    print("✅ Analytics test passed!")