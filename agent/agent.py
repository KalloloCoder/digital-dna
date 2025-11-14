"""
Behavioral Agent Module - Digital DNA MVP

Modul ini bertanggung jawab untuk menangkap behavioral vectors dari entitas digital.
Termasuk: keystroke dynamics, CPU usage, API calls, network patterns, dan anomali perilaku.

Author: Digital DNA Team
Version: 0.1.0
"""

import logging
import json
import random
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BehaviorType(Enum):
    """Enum untuk tipe perilaku yang dapat ditangkap."""
    KEYSTROKE = "keystroke"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    API_CALL = "api_call"
    NETWORK_PATTERN = "network_pattern"
    LOGIN_PATTERN = "login_pattern"
    FILE_ACCESS = "file_access"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class AnomalyLevel(Enum):
    """Enum untuk level anomali deteksi awal."""
    NORMAL = 0
    SUSPICIOUS = 1
    CRITICAL = 2


@dataclass
class BehavioralVector:
    """Data class untuk menyimpan satu vektor perilaku."""
    vector_id: str
    entity_id: str
    behavior_type: str
    timestamp: str
    value: float
    metadata: Dict[str, Any]
    hash_value: str
    anomaly_level: str = "NORMAL"


class BehavioralCapture:
    """
    Kelas utama untuk menangkap behavioral vectors dari entitas digital.
    
    Fitur:
    - Capture keystroke dynamics (inter-keystroke time, pressure)
    - Capture CPU/memory usage patterns
    - Capture API call patterns
    - Capture network patterns
    - Initial anomaly detection
    - Mock data generation untuk simulasi
    
    TODO: Integrasi dengan sistem monitoring real yang aktual
    """

    def __init__(self, entity_id: str, entity_type: str = "user"):
        """
        Inisialisasi BehavioralCapture.
        
        Args:
            entity_id: ID unik untuk entitas (user/device/application)
            entity_type: Tipe entitas ("user", "device", "application")
        """
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.vectors: List[BehavioralVector] = []
        self.baseline: Dict[str, float] = {}
        self.anomaly_threshold = 0.7
        
        logger.info(f"BehavioralCapture initialized for entity: {entity_id} (type: {entity_type})")

    def capture_keystroke_dynamics(self) -> BehavioralVector:
        """
        Tangkap keystroke dynamics (inter-keystroke time, pressure, dwell time).
        
        Mock data untuk simulasi:
        - Inter-keystroke time: 50-150ms
        - Dwell time: 80-200ms
        - Pressure: 40-100 (normalized)
        
        Returns:
            BehavioralVector dengan keystroke dynamics data
        """
        # Mock keystroke data
        ikt = random.uniform(50, 150)  # inter-keystroke time
        dwell_time = random.uniform(80, 200)
        pressure = random.uniform(40, 100)
        
        value = (ikt + dwell_time + pressure) / 3  # normalized
        
        metadata = {
            "inter_keystroke_time_ms": ikt,
            "dwell_time_ms": dwell_time,
            "pressure_normalized": pressure,
            "key_sequence": "mock_pattern_123"
        }
        
        vector = self._create_vector(
            behavior_type=BehaviorType.KEYSTROKE,
            value=value,
            metadata=metadata
        )
        
        logger.info(f"Keystroke dynamics captured for {self.entity_id}: IKT={ikt:.2f}ms")
        return vector

    def capture_cpu_memory_usage(self) -> BehavioralVector:
        """
        Tangkap CPU dan memory usage patterns.
        
        Mock data untuk simulasi:
        - CPU usage: 10-90%
        - Memory usage: 20-80%
        - Process count: 20-100
        
        Returns:
            BehavioralVector dengan resource usage data
        """
        cpu_usage = random.uniform(10, 90)
        memory_usage = random.uniform(20, 80)
        process_count = random.randint(20, 100)
        
        value = (cpu_usage + memory_usage) / 2
        
        metadata = {
            "cpu_percent": cpu_usage,
            "memory_percent": memory_usage,
            "process_count": process_count,
            "top_process": "chrome.exe"
        }
        
        vector = self._create_vector(
            behavior_type=BehaviorType.CPU_USAGE,
            value=value,
            metadata=metadata
        )
        
        logger.info(f"Resource usage captured for {self.entity_id}: CPU={cpu_usage:.1f}%, MEM={memory_usage:.1f}%")
        return vector

    def capture_api_calls(self) -> BehavioralVector:
        """
        Tangkap API call patterns (endpoints, frequency, latency, status codes).
        
        Mock data untuk simulasi:
        - Request count: 1-50
        - Average latency: 50-500ms
        - Error rate: 0-10%
        
        Returns:
            BehavioralVector dengan API call pattern
        """
        request_count = random.randint(1, 50)
        avg_latency = random.uniform(50, 500)
        error_rate = random.uniform(0, 10)
        
        value = (request_count + avg_latency + error_rate) / 3
        
        metadata = {
            "request_count": request_count,
            "avg_latency_ms": avg_latency,
            "error_rate_percent": error_rate,
            "endpoints": ["/api/user/profile", "/api/data/query", "/api/auth/validate"],
            "http_methods": ["GET", "POST", "PUT"]
        }
        
        vector = self._create_vector(
            behavior_type=BehaviorType.API_CALL,
            value=value,
            metadata=metadata
        )
        
        logger.info(f"API calls captured for {self.entity_id}: {request_count} requests, {avg_latency:.1f}ms avg latency")
        return vector

    def capture_network_patterns(self) -> BehavioralVector:
        """
        Tangkap network pattern (IP geolocation, port usage, data transfer rate).
        
        Mock data untuk simulasi:
        - Source IP: mock
        - Destination IPs: multiple
        - Data transfer: 1MB-100MB
        - Open ports: 3-20
        
        Returns:
            BehavioralVector dengan network pattern
        """
        data_transfer_mb = random.uniform(1, 100)
        open_ports = random.randint(3, 20)
        packet_loss = random.uniform(0, 5)
        
        value = (data_transfer_mb + open_ports * 5 + packet_loss) / 3
        
        metadata = {
            "source_ip": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "destination_ips": [f"10.0.{i}.1" for i in range(1, 4)],
            "data_transfer_mb": data_transfer_mb,
            "open_ports": open_ports,
            "packet_loss_percent": packet_loss
        }
        
        vector = self._create_vector(
            behavior_type=BehaviorType.NETWORK_PATTERN,
            value=value,
            metadata=metadata
        )
        
        logger.info(f"Network patterns captured for {self.entity_id}: {data_transfer_mb:.1f}MB transferred, {open_ports} open ports")
        return vector

    def capture_login_patterns(self) -> BehavioralVector:
        """
        Tangkap login pattern (time of day, location, device, frequency).
        
        Mock data untuk simulasi:
        - Login hour: 0-23
        - Login location: mock
        - Device fingerprint: mock
        - Frequency: daily/weekly
        
        Returns:
            BehavioralVector dengan login pattern
        """
        login_hour = random.randint(0, 23)
        frequency_per_week = random.randint(1, 30)
        failed_attempts = random.randint(0, 3)
        
        value = (login_hour + frequency_per_week + failed_attempts * 2) / 3
        
        metadata = {
            "login_hour": login_hour,
            "login_location": "Jakarta, Indonesia",
            "device_fingerprint": "DEVICE_" + hashlib.md5(str(random.random()).encode()).hexdigest()[:12],
            "frequency_per_week": frequency_per_week,
            "failed_login_attempts": failed_attempts
        }
        
        vector = self._create_vector(
            behavior_type=BehaviorType.LOGIN_PATTERN,
            value=value,
            metadata=metadata
        )
        
        logger.info(f"Login patterns captured for {self.entity_id}: hour={login_hour}, freq={frequency_per_week}/week")
        return vector

    def capture_file_access_patterns(self) -> BehavioralVector:
        """
        Tangkap file access pattern (files accessed, frequency, permissions).
        
        Mock data untuk simulasi:
        - Files accessed: 10-100
        - Read/Write ratio
        - Sensitive files accessed: yes/no
        
        Returns:
            BehavioralVector dengan file access pattern
        """
        files_accessed = random.randint(10, 100)
        read_ops = random.randint(50, 200)
        write_ops = random.randint(10, 100)
        sensitive_access = random.choice([True, False])
        
        value = (files_accessed + read_ops + write_ops) / 3
        
        metadata = {
            "files_accessed_count": files_accessed,
            "read_operations": read_ops,
            "write_operations": write_ops,
            "sensitive_files_accessed": sensitive_access,
            "file_types": ["docx", "xlsx", "pdf", "exe", "dll"]
        }
        
        vector = self._create_vector(
            behavior_type=BehaviorType.FILE_ACCESS,
            value=value,
            metadata=metadata
        )
        
        logger.info(f"File access patterns captured for {self.entity_id}: {files_accessed} files, sensitive={sensitive_access}")
        return vector

    def _create_vector(self, behavior_type: BehaviorType, value: float, metadata: Dict[str, Any]) -> BehavioralVector:
        """
        Internal helper untuk membuat dan menyimpan behavioral vector.
        
        Args:
            behavior_type: Tipe perilaku
            value: Nilai numerik perilaku
            metadata: Metadata tambahan
            
        Returns:
            BehavioralVector yang telah dibuat
        """
        vector_id = f"{self.entity_id}_{behavior_type.value}_{int(time.time() * 1000)}"
        hash_value = self._compute_vector_hash(vector_id, value, metadata)
        
        # Simple anomaly detection
        anomaly_level = self._detect_anomaly(behavior_type, value, metadata)
        
        vector = BehavioralVector(
            vector_id=vector_id,
            entity_id=self.entity_id,
            behavior_type=behavior_type.value,
            timestamp=datetime.utcnow().isoformat(),
            value=value,
            metadata=metadata,
            hash_value=hash_value,
            anomaly_level=anomaly_level.name
        )
        
        self.vectors.append(vector)
        return vector

    def _compute_vector_hash(self, vector_id: str, value: float, metadata: Dict[str, Any]) -> str:
        """
        Hitung hash untuk behavioral vector.
        
        Args:
            vector_id: ID vektor
            value: Nilai numerik
            metadata: Metadata
            
        Returns:
            Hash string (SHA256)
        """
        combined = f"{vector_id}_{value}_{json.dumps(metadata, sort_keys=True)}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def _detect_anomaly(self, behavior_type: BehaviorType, value: float, metadata: Dict[str, Any]) -> AnomalyLevel:
        """
        Deteksi awal anomali pada vektor perilaku.
        
        Logika sederhana berdasarkan threshold:
        - NORMAL: value < threshold
        - SUSPICIOUS: threshold <= value < 2*threshold
        - CRITICAL: value >= 2*threshold
        
        TODO: Implementasi machine learning untuk anomaly detection
        
        Args:
            behavior_type: Tipe perilaku
            value: Nilai numerik
            metadata: Metadata
            
        Returns:
            AnomalyLevel
        """
        threshold = 60.0
        
        if value < threshold:
            return AnomalyLevel.NORMAL
        elif value < 2 * threshold:
            return AnomalyLevel.SUSPICIOUS
        else:
            return AnomalyLevel.CRITICAL

    def get_vectors(self) -> List[BehavioralVector]:
        """Dapatkan semua vectors yang telah ditangkap."""
        return self.vectors

    def get_vectors_as_dict(self) -> List[Dict[str, Any]]:
        """Dapatkan semua vectors sebagai dictionary list."""
        return [asdict(v) for v in self.vectors]

    def clear_vectors(self):
        """Hapus semua vectors dari buffer."""
        self.vectors.clear()
        logger.info(f"All vectors cleared for {self.entity_id}")

    def generate_mock_profile(self) -> Dict[str, Any]:
        """
        Generate mock behavioral profile dengan menangkap semua tipe perilaku.
        
        Returns:
            Dictionary dengan behavioral profile lengkap
        """
        logger.info(f"Generating mock behavioral profile for {self.entity_id}")
        
        profile = {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "profile_timestamp": datetime.utcnow().isoformat(),
            "vectors": []
        }
        
        # Capture all behavior types
        capture_methods = [
            self.capture_keystroke_dynamics,
            self.capture_cpu_memory_usage,
            self.capture_api_calls,
            self.capture_network_patterns,
            self.capture_login_patterns,
            self.capture_file_access_patterns
        ]
        
        for method in capture_methods:
            vector = method()
            profile["vectors"].append(asdict(vector))
        
        logger.info(f"Mock profile generated with {len(profile['vectors'])} vectors")
        return profile


# Example mock data generator
def generate_mock_entities() -> Dict[str, BehavioralCapture]:
    """
    Generate mock entities dengan behavioral capture.
    
    Returns:
        Dictionary of BehavioralCapture instances untuk berbagai entity
    """
    entities = {}
    
    # Mock users
    users = ["user_alice", "user_bob", "user_charlie"]
    for user_id in users:
        entities[user_id] = BehavioralCapture(user_id, entity_type="user")
    
    # Mock devices
    devices = ["device_laptop_001", "device_phone_001"]
    for device_id in devices:
        entities[device_id] = BehavioralCapture(device_id, entity_type="device")
    
    # Mock applications
    apps = ["app_chrome", "app_slack"]
    for app_id in apps:
        entities[app_id] = BehavioralCapture(app_id, entity_type="application")
    
    return entities


if __name__ == "__main__":
    # Test code
    logger.info("=" * 80)
    logger.info("BEHAVIORAL AGENT MODULE TEST")
    logger.info("=" * 80)
    
    # Create mock entity
    agent = BehavioralCapture("test_user_001", entity_type="user")
    
    # Capture various behavioral vectors
    logger.info("\nCapturing behavioral vectors...")
    agent.capture_keystroke_dynamics()
    agent.capture_cpu_memory_usage()
    agent.capture_api_calls()
    agent.capture_network_patterns()
    agent.capture_login_patterns()
    agent.capture_file_access_patterns()
    
    # Generate and display profile
    profile = agent.generate_mock_profile()
    logger.info(f"\nBehavioral profile created with {len(profile['vectors'])} vectors")
    logger.info(f"Profile timestamp: {profile['profile_timestamp']}")
    
    # Display summary
    for vector in profile['vectors']:
        logger.info(f"  - {vector['behavior_type']}: {vector['value']:.2f} (anomaly: {vector['anomaly_level']})")
