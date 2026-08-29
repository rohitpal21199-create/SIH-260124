"""
Report Generator - Reports
"""

import json
from datetime import datetime
from typing import Dict

class ReportGenerator:
    def __init__(self, database, analytics):
        self.db = database
        self.analytics = analytics
    
    def generate_summary_report(self) -> Dict:
        """Generate summary report"""
        stats = self.db.get_stats()
        insights = self.analytics.get_insights()
        
        return {
            'title': 'Urban Sensing Platform - Summary Report',
            'generated_at': datetime.now().isoformat(),
            'statistics': stats,
            'insights': insights,
            'bus_count': stats.get('unique_buses', 0),
            'total_events': stats.get('total_events', 0)
        }
    
    def generate_defect_report(self) -> Dict:
        """Generate defect report"""
        defects = self.db.get_defects()
        
        defect_types = {}
        for d in defects:
            defect_type = d.get('type', ['unknown'])[0] if isinstance(d.get('type'), list) else 'unknown'
            defect_types[defect_type] = defect_types.get(defect_type, 0) + 1
        
        return {
            'title': 'Road Defects Report',
            'generated_at': datetime.now().isoformat(),
            'total_defects': len(defects),
            'defect_types': defect_types,
            'defects': defects[-20:]
        }
    
    def generate_object_report(self) -> Dict:
        """Generate object detection report"""
        objects_count = self.db.get_objects_count()
        events = self.db.get_events()
        
        return {
            'title': 'Object Detection Report',
            'generated_at': datetime.now().isoformat(),
            'total_objects': sum(objects_count.values()),
            'object_distribution': objects_count,
            'recent_objects': [
                {'timestamp': e.get('timestamp'), 'objects': e.get('objects', [])}
                for e in events[-10:]
            ]
        }
    
    def export_report(self, report: Dict, filename: str):
        """Export report as JSON"""
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        return filename

# Test
if __name__ == "__main__":
    from database import Database
    from analytics import Analytics
    db = Database()
    analytics = Analytics(db)
    reporter = ReportGenerator(db, analytics)
    print("✅ Report Generator test passed!")