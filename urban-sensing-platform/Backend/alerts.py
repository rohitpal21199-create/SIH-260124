"""
Alert System - Real-time Alerts
"""

from datetime import datetime
from typing import List, Dict
import json

class AlertSystem:
    def __init__(self):
        self.alerts = []
        self.alert_thresholds = {
            'pothole': {'severity': 'medium', 'action': 'send_to_maintenance'},
            'crack': {'severity': 'low', 'action': 'report_to_authority'},
            'waterlogging': {'severity': 'medium', 'action': 'send_to_authority'},
            'missing_signage': {'severity': 'low', 'action': 'report_to_authority'},
            'accident': {'severity': 'high', 'action': 'emergency_alert'},
            'rash_driving': {'severity': 'high', 'action': 'police_alert'}
        }
        self.alert_id_counter = 0
    
    def check_alerts(self, events: List[Dict]) -> List[Dict]:
        """Check events for alerts"""
        new_alerts = []
        
        for event in events:
            # Check road defects
            if event.get('road_defects'):
                for defect in event.get('road_defects', []):
                    if defect in self.alert_thresholds:
                        self.alert_id_counter += 1
                        alert = {
                            'id': self.alert_id_counter,
                            'type': defect,
                            'severity': self.alert_thresholds[defect]['severity'],
                            'action': self.alert_thresholds[defect]['action'],
                            'location': event.get('location', ''),
                            'timestamp': event.get('timestamp', ''),
                            'bus_id': event.get('bus_id', ''),
                            'status': 'active',
                            'created_at': datetime.now().isoformat()
                        }
                        new_alerts.append(alert)
            
            # Check for potential accident
            if event.get('objects'):
                objects = event.get('objects', [])
                if 'car' in objects and 'person' in objects:
                    self.alert_id_counter += 1
                    alert = {
                        'id': self.alert_id_counter,
                        'type': 'potential_accident',
                        'severity': 'high',
                        'action': 'emergency_alert',
                        'location': event.get('location', ''),
                        'timestamp': event.get('timestamp', ''),
                        'bus_id': event.get('bus_id', ''),
                        'status': 'active',
                        'created_at': datetime.now().isoformat()
                    }
                    new_alerts.append(alert)
        
        self.alerts.extend(new_alerts)
        return new_alerts
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all active alerts"""
        return [a for a in self.alerts if a['status'] == 'active']
    
    def get_alerts_by_severity(self, severity: str) -> List[Dict]:
        """Get alerts by severity"""
        return [a for a in self.alerts if a.get('severity') == severity]
    
    def resolve_alert(self, alert_id: int):
        """Mark alert as resolved"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['status'] = 'resolved'
                alert['resolved_at'] = datetime.now().isoformat()
                return True
        return False
    
    def get_alert_summary(self) -> Dict:
        """Get alert summary"""
        active = self.get_active_alerts()
        
        return {
            'total_alerts': len(self.alerts),
            'active_alerts': len(active),
            'high_severity': len([a for a in active if a['severity'] == 'high']),
            'medium_severity': len([a for a in active if a['severity'] == 'medium']),
            'low_severity': len([a for a in active if a['severity'] == 'low'])
        }

# Test
if __name__ == "__main__":
    alert_system = AlertSystem()
    test_events = [{
        'bus_id': 'BUS-001',
        'timestamp': datetime.now().isoformat(),
        'location': '19.0760, 72.8777',
        'road_defects': ['pothole'],
        'objects': ['car', 'person']
    }]
    alerts = alert_system.check_alerts(test_events)
    print(f"✅ Generated {len(alerts)} alerts")
    print(f"📊 Alert Summary: {alert_system.get_alert_summary()}")