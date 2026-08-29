"""
Database Module - Data Storage & Retrieval
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, data_file="data/events.json"):
        self.data_file = data_file
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        """Create file if not exists"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f)
    
    def read_events(self) -> List[Dict]:
        """Read all events"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def write_events(self, events: List[Dict]):
        """Write events to file"""
        with open(self.data_file, 'w') as f:
            json.dump(events, f, indent=2)
    
    def add_event(self, event: Dict):
        """Add a single event"""
        events = self.read_events()
        events.append(event)
        self.write_events(events)
        return event
    
    def get_events(self, limit: int = 100, 
                   event_type: Optional[str] = None,
                   bus_id: Optional[str] = None) -> List[Dict]:
        """Get events with filters"""
        events = self.read_events()
        
        if event_type:
            events = [e for e in events if e.get('event_type') == event_type]
        if bus_id:
            events = [e for e in events if e.get('bus_id') == bus_id]
        
        return events[-limit:]
    
    def get_stats(self) -> Dict:
        """Get statistics"""
        events = self.read_events()
        
        stats = {
            'total_events': len(events),
            'total_objects': 0,
            'total_defects': 0,
            'unique_buses': len(set(e.get('bus_id', '') for e in events)),
            'timestamp': datetime.now().isoformat()
        }
        
        for e in events:
            stats['total_objects'] += len(e.get('objects', []))
            stats['total_defects'] += len(e.get('road_defects', []))
        
        return stats
    
    def get_defects(self) -> List[Dict]:
        """Get all road defects"""
        events = self.read_events()
        defects = []
        for e in events:
            if e.get('road_defects'):
                defects.append({
                    'type': e['road_defects'],
                    'location': e.get('location', ''),
                    'timestamp': e.get('timestamp', ''),
                    'bus_id': e.get('bus_id', '')
                })
        return defects
    
    def get_objects_count(self) -> Dict:
        """Count objects by type"""
        events = self.read_events()
        object_counts = {}
        
        for e in events:
            for obj in e.get('objects', []):
                object_counts[obj] = object_counts.get(obj, 0) + 1
        
        return object_counts
    
    def get_bus_routes(self) -> Dict:
        """Get bus routes"""
        events = self.read_events()
        bus_routes = {}
        
        for e in events:
            bus_id = e.get('bus_id')
            if bus_id:
                if bus_id not in bus_routes:
                    bus_routes[bus_id] = []
                bus_routes[bus_id].append({
                    'lat': e.get('latitude', 0),
                    'lon': e.get('longitude', 0),
                    'timestamp': e.get('timestamp', '')
                })
        
        return bus_routes

# Test
if __name__ == "__main__":
    db = Database()
    test_event = {
        'timestamp': datetime.now().isoformat(),
        'bus_id': 'BUS-TEST',
        'event_type': 'object_detection',
        'latitude': 19.0760,
        'longitude': 72.8777,
        'objects': ['car', 'person'],
        'road_defects': ['pothole'],
        'location': '19.0760, 72.8777'
    }
    db.add_event(test_event)
    print("✅ Database test passed!")
    print(f"📊 Stats: {db.get_stats()}")