"""
DNA Generator Module - Digital DNA MVP

Modul ini bertanggung jawab untuk menghasilkan Digital DNA unik dari behavioral vectors.
Digital DNA mencakup: hashing, entropy calculation, mock cryptographic signing, dan versioning.

Author: Digital DNA Team
Version: 0.1.0
"""

import logging
import json
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DNAAlgorithm(Enum):
    """Enum untuk algoritma DNA generation yang didukung."""
    SHA256_COMPOSITE = "sha256_composite"
    SHA512_COMPOSITE = "sha512_composite"
    BLAKE2_COMPOSITE = "blake2_composite"


@dataclass
class DigitalDNA:
    """Data class untuk menyimpan Digital DNA lengkap."""
    dna_id: str
    entity_id: str
    entity_type: str
    generation_timestamp: str
    expiration_timestamp: str
    dna_hash: str
    dna_signature: str  # Mock cryptographic signature
    entropy_score: float
    vector_count: int
    version: str
    algorithm: str
    behavioral_profile_hash: str
    metadata: Dict[str, Any]
    is_valid: bool = True


@dataclass
class DNAComponent:
    """Data class untuk komponen penyusun Digital DNA."""
    component_name: str
    component_value: str
    component_weight: float
    contribution_to_entropy: float


class DNAGenerator:
    """
    Kelas untuk menghasilkan Digital DNA dari behavioral vectors.
    
    Fitur:
    - Composite hashing dari multiple behavioral dimensions
    - Entropy calculation berdasarkan vector diversity
    - Mock cryptographic signing
    - DNA versioning dan expiration management
    - Support multiple hashing algorithms
    - Integration dengan behavioral vectors
    
    TODO: Integrasi dengan real cryptographic libraries (RSA, ECDSA)
    TODO: Implementasi hierarchical DNA composition
    """

    def __init__(self, entity_id: str, entity_type: str = "user"):
        """
        Inisialisasi DNAGenerator.
        
        Args:
            entity_id: ID unik untuk entitas
            entity_type: Tipe entitas ("user", "device", "application")
        """
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.dna_version = "1.0.0"
        self.dna_ttl_days = 30  # DNA valid untuk 30 hari
        self.dna_history: List[DigitalDNA] = []
        self.components: List[DNAComponent] = []
        
        logger.info(f"DNAGenerator initialized for entity: {entity_id} (type: {entity_type})")

    def generate_dna(
        self,
        behavioral_vectors: List[Dict[str, Any]],
        algorithm: DNAAlgorithm = DNAAlgorithm.SHA256_COMPOSITE
    ) -> DigitalDNA:
        """
        Generate Digital DNA dari behavioral vectors.
        
        Args:
            behavioral_vectors: List of behavioral vectors dari agent
            algorithm: Algoritma untuk DNA generation
            
        Returns:
            DigitalDNA object dengan DNA lengkap
        """
        logger.info(f"Generating Digital DNA for {self.entity_id} with {len(behavioral_vectors)} vectors")
        
        # Step 1: Extract dan normalize vectors
        normalized_vectors = self._normalize_vectors(behavioral_vectors)
        
        # Step 2: Calculate entropy
        entropy_score = self._calculate_entropy(normalized_vectors)
        
        # Step 3: Create composite hash
        composite_hash = self._create_composite_hash(normalized_vectors, algorithm)
        
        # Step 4: Generate behavioral profile hash
        profile_hash = self._hash_behavioral_profile(normalized_vectors)
        
        # Step 5: Create mock cryptographic signature
        signature = self._generate_mock_signature(composite_hash)
        
        # Step 6: Create DNA ID dan timestamps
        dna_id = self._generate_dna_id()
        generation_ts = datetime.utcnow().isoformat()
        expiration_ts = (datetime.utcnow() + timedelta(days=self.dna_ttl_days)).isoformat()
        
        # Step 7: Create metadata
        metadata = {
            "vector_count": len(behavioral_vectors),
            "components_count": len(self.components),
            "algorithm_version": algorithm.value,
            "generation_method": "behavioral_composite",
            "entropy_threshold_met": entropy_score >= 0.5
        }
        
        # Step 8: Create DigitalDNA object
        dna = DigitalDNA(
            dna_id=dna_id,
            entity_id=self.entity_id,
            entity_type=self.entity_type,
            generation_timestamp=generation_ts,
            expiration_timestamp=expiration_ts,
            dna_hash=composite_hash,
            dna_signature=signature,
            entropy_score=entropy_score,
            vector_count=len(behavioral_vectors),
            version=self.dna_version,
            algorithm=algorithm.value,
            behavioral_profile_hash=profile_hash,
            metadata=metadata,
            is_valid=True
        )
        
        self.dna_history.append(dna)
        
        logger.info(f"Digital DNA generated: {dna_id}, entropy={entropy_score:.3f}, signature={signature[:16]}...")
        return dna

    def _normalize_vectors(self, vectors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize behavioral vectors ke range [0, 1].
        
        Args:
            vectors: List of behavioral vectors
            
        Returns:
            Normalized vectors
        """
        if not vectors:
            return []
        
        # Use global normalization across all vectors so single-sample behavior types
        # still get meaningful normalized values (useful for small test fixtures)
        normalized = []
        all_values = [v.get("value", 0) for v in vectors]
        global_min = min(all_values) if all_values else 0
        global_max = max(all_values) if all_values else 1
        global_range = global_max - global_min if global_max != global_min else 1

        for vector in vectors:
            normalized_vector = vector.copy()
            original_value = vector.get("value", 0)
            normalized_vector["normalized_value"] = (original_value - global_min) / global_range
            normalized.append(normalized_vector)
        
        logger.info(f"Normalized {len(normalized)} vectors")
        return normalized

    def _calculate_entropy(self, vectors: List[Dict[str, Any]]) -> float:
        """
        Hitung entropy dari behavioral vectors.
        
        Entropy mengukur diversity dan randomness dari behavioral patterns.
        Semakin tinggi entropy, semakin unik perilaku.
        
        Args:
            vectors: List of normalized behavioral vectors
            
        Returns:
            Entropy score [0.0 - 1.0]
        """
        if not vectors:
            return 0.0
        
        # Collect normalized values
        values = [v.get("normalized_value", 0) for v in vectors]

        # Use variance as a proxy for entropy/diversity. For values in [0,1],
        # maximum variance is 0.25, so we normalize against that.
        mean = sum(values) / len(values) if values else 0
        variance = sum((x - mean) ** 2 for x in values) / len(values) if values else 0
        max_variance = 0.25
        entropy_score = min(variance / max_variance if max_variance > 0 else 0, 1.0)
        
        # Add component tracking
        self.components = [
            DNAComponent(
                component_name=f"vector_{i}",
                component_value=str(v.get("behavior_type", "unknown")),
                component_weight=v.get("normalized_value", 0),
                contribution_to_entropy=v.get("normalized_value", 0) * 0.1
            )
            for i, v in enumerate(vectors[:10])  # Limit to first 10 components
        ]
        
        logger.info(f"Entropy calculated: {entropy_score:.3f} from {len(values)} vectors")
        return entropy_score

    def _create_composite_hash(
        self,
        vectors: List[Dict[str, Any]],
        algorithm: DNAAlgorithm
    ) -> str:
        """
        Buat composite hash dari behavioral vectors.
        
        Composite hash menggabungkan hashes dari:
        1. Behavioral vectors (aggregated)
        2. Vector sequence dan timing
        3. Vector relationships
        
        Args:
            vectors: List of normalized vectors
            algorithm: Algorithm untuk hashing
            
        Returns:
            Composite hash string (hex)
        """
        if not vectors:
            return hashlib.sha256(b"empty").hexdigest()
        
        # Create hash inputs
        hash_inputs = []
        
        for i, vector in enumerate(vectors):
            behavior_type = vector.get("behavior_type", "unknown")
            value = vector.get("normalized_value", 0)
            timestamp = vector.get("timestamp", "")
            
            # Create vector hash
            vector_hash_input = f"{i}:{behavior_type}:{value:.6f}:{timestamp}"
            hash_inputs.append(vector_hash_input)
        
        # Combine all inputs
        combined_input = "|".join(hash_inputs)
        
        # Apply selected algorithm
        if algorithm == DNAAlgorithm.SHA256_COMPOSITE:
            composite_hash = hashlib.sha256(combined_input.encode()).hexdigest()
        elif algorithm == DNAAlgorithm.SHA512_COMPOSITE:
            composite_hash = hashlib.sha512(combined_input.encode()).hexdigest()
        else:  # BLAKE2_COMPOSITE
            # hashlib already imported at module level; use blake2b from it
            composite_hash = hashlib.blake2b(combined_input.encode()).hexdigest()
        
        logger.info(f"Composite hash created: {composite_hash[:16]}... using {algorithm.value}")
        return composite_hash

    def _hash_behavioral_profile(self, vectors: List[Dict[str, Any]]) -> str:
        """
        Hash dari behavioral profile (aggregation dari semua vectors).
        
        Args:
            vectors: List of vectors
            
        Returns:
            Profile hash string (hex)
        """
        profile_data = {
            "vector_count": len(vectors),
            "behavior_types": list(set(v.get("behavior_type", "unknown") for v in vectors)),
            "avg_value": sum(v.get("normalized_value", 0) for v in vectors) / len(vectors) if vectors else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        profile_json = json.dumps(profile_data, sort_keys=True)
        profile_hash = hashlib.sha256(profile_json.encode()).hexdigest()
        
        logger.info(f"Behavioral profile hash: {profile_hash[:16]}...")
        return profile_hash

    def _generate_mock_signature(self, data_to_sign: str) -> str:
        """
        Generate mock cryptographic signature.
        
        DALAM PRODUCTION: Use real RSA/ECDSA signing
        
        Args:
            data_to_sign: Data untuk di-sign
            
        Returns:
            Mock signature string (hex)
        """
        # Mock signing dengan HMAC-SHA256
        secret_key = secrets.token_bytes(32)
        mock_signature = hmac.new(
            secret_key,
            data_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()
        
        logger.info(f"Mock signature generated: {mock_signature[:16]}...")
        return mock_signature

    def _generate_dna_id(self) -> str:
        """Generate unique DNA ID."""
        timestamp = int(time.time() * 1000)
        random_suffix = secrets.token_hex(6)
        dna_id = f"DNA_{self.entity_id}_{timestamp}_{random_suffix}"
        return dna_id

    def verify_dna_validity(self, dna: DigitalDNA) -> Tuple[bool, str]:
        """
        Verifikasi validity dari Digital DNA.
        
        TODO: Implement real cryptographic verification
        
        Args:
            dna: DigitalDNA object untuk diverifikasi
            
        Returns:
            Tuple[is_valid, reason]
        """
        # Check expiration
        expiration_ts = datetime.fromisoformat(dna.expiration_timestamp)
        if datetime.utcnow() > expiration_ts:
            return False, "DNA has expired"
        
        # Check format
        if not dna.dna_hash or len(dna.dna_hash) < 16:
            return False, "Invalid DNA hash format"
        
        # Check signature
        if not dna.dna_signature or len(dna.dna_signature) < 16:
            return False, "Invalid DNA signature"
        
        # Check entropy
        if dna.entropy_score < 0.3:
            return False, "Entropy score too low"
        
        return True, "DNA is valid"

    def get_dna_history(self) -> List[DigitalDNA]:
        """Dapatkan history semua DNA yang telah generated."""
        return self.dna_history

    def get_latest_dna(self) -> Optional[DigitalDNA]:
        """Dapatkan DNA yang paling baru."""
        return self.dna_history[-1] if self.dna_history else None

    def rotate_dna(self, behavioral_vectors: List[Dict[str, Any]]) -> DigitalDNA:
        """
        Rotate ke DNA baru berdasarkan updated behavioral vectors.
        
        Args:
            behavioral_vectors: Updated behavioral vectors
            
        Returns:
            New DigitalDNA object
        """
        logger.info(f"Rotating DNA for {self.entity_id}")
        
        # Invalidate old DNA
        if self.dna_history:
            self.dna_history[-1].is_valid = False
        
        # Generate new DNA
        new_dna = self.generate_dna(behavioral_vectors)
        
        logger.info(f"DNA rotated. New DNA ID: {new_dna.dna_id}")
        return new_dna

    def compare_dna_similarity(self, dna1: DigitalDNA, dna2: DigitalDNA) -> float:
        """
        Hitung similarity score antara dua DNA.
        
        Returns:
            Similarity score [0.0 - 1.0]
        """
        if dna1.dna_hash == dna2.dna_hash:
            return 1.0
        
        # Hamming distance
        hash1 = dna1.dna_hash
        hash2 = dna2.dna_hash
        
        matching_chars = sum(1 for a, b in zip(hash1, hash2) if a == b)
        similarity = matching_chars / len(hash1) if hash1 else 0.0
        
        return similarity


class DNAFactory:
    """Factory untuk membuat dan manage DNA generators untuk multiple entities."""
    
    def __init__(self):
        """Inisialisasi DNAFactory."""
        self.generators: Dict[str, DNAGenerator] = {}
        logger.info("DNAFactory initialized")

    def create_generator(self, entity_id: str, entity_type: str = "user") -> DNAGenerator:
        """Buat atau dapatkan generator untuk entity."""
        if entity_id not in self.generators:
            self.generators[entity_id] = DNAGenerator(entity_id, entity_type)
        return self.generators[entity_id]

    def generate_dna_for_entity(
        self,
        entity_id: str,
        behavioral_vectors: List[Dict[str, Any]],
        entity_type: str = "user"
    ) -> DigitalDNA:
        """Generate DNA untuk entity dengan behavioral vectors."""
        generator = self.create_generator(entity_id, entity_type)
        return generator.generate_dna(behavioral_vectors)

    def get_generator(self, entity_id: str) -> Optional[DNAGenerator]:
        """Dapatkan generator untuk entity."""
        return self.generators.get(entity_id)

    def get_all_generators(self) -> Dict[str, DNAGenerator]:
        """Dapatkan semua generators."""
        return self.generators


if __name__ == "__main__":
    # Test code
    logger.info("=" * 80)
    logger.info("DNA GENERATOR MODULE TEST")
    logger.info("=" * 80)
    
    # Create mock behavioral vectors
    mock_vectors = [
        {
            "behavior_type": "keystroke",
            "value": 65.5,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {"ikt": 120}
        },
        {
            "behavior_type": "cpu_usage",
            "value": 45.3,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {"cpu": 45}
        },
        {
            "behavior_type": "api_call",
            "value": 32.1,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {"requests": 25}
        },
        {
            "behavior_type": "network_pattern",
            "value": 55.8,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {"data_mb": 50}
        },
        {
            "behavior_type": "login_pattern",
            "value": 40.2,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {"hour": 14}
        }
    ]
    
    # Create DNA generator
    generator = DNAGenerator("test_user_001", entity_type="user")
    
    # Generate DNA
    logger.info("\nGenerating Digital DNA...")
    dna = generator.generate_dna(mock_vectors)
    
    # Display DNA info
    logger.info(f"\nDigital DNA Generated:")
    logger.info(f"  DNA ID: {dna.dna_id}")
    logger.info(f"  Hash: {dna.dna_hash[:32]}...")
    logger.info(f"  Entropy: {dna.entropy_score:.3f}")
    logger.info(f"  Signature: {dna.dna_signature[:32]}...")
    logger.info(f"  Valid: {dna.is_valid}")
    logger.info(f"  Expires: {dna.expiration_timestamp}")
    
    # Verify DNA
    is_valid, reason = generator.verify_dna_validity(dna)
    logger.info(f"\nDNA Verification: {is_valid} ({reason})")
    
    # Test DNA rotation
    logger.info("\nRotating DNA...")
    new_dna = generator.rotate_dna(mock_vectors)
    logger.info(f"New DNA ID: {new_dna.dna_id}")
