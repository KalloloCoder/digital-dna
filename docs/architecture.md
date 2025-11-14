# Digital DNA MVP - Architecture

## High-Level System Design

### System Overview

Digital DNA adalah sistem keamanan berbasis behavioral biometrics yang menggunakan arsitektur berlapis untuk capture, generate, verify, dan enforce access control terhadap identitas digital.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Entity (User/Device/App)                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌──────────────────────┐        ┌──────────────────────┐
│   BEHAVIORAL         │        │   BEHAVIORAL         │
│   CAPTURE            │        │   CAPTURE            │
│   (Agent)            │        │   (Agent)            │
└──────────┬───────────┘        └──────────┬───────────┘
           │                               │
           └───────────────┬───────────────┘
                           │
                    ┌──────▼──────┐
                    │  Behavioral │
                    │  Vectors    │
                    │  (Set)      │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────────┐
                    │  DNA GENERATION │
                    │  (Generator)    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Digital DNA    │
                    │  (Hash+Entropy) │
                    └────────┬────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
        ▼                                         ▼
┌──────────────────────┐                ┌──────────────────────┐
│ LOCAL VERIFICATION  │                │  FEDERATED           │
│ - Format check      │                │  VERIFICATION        │
│ - Hash verify       │                │  - Multi-node        │
│ - Anomaly detect    │                │  - Consensus         │
│ - Threat detect     │                │  - ZK-Proof          │
└──────────┬──────────┘                └──────────┬───────────┘
           │                                      │
           │              Confidence + Threat     │
           └──────────────────┬──────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  POLICY ENGINE      │
                    │  - Rule evaluation  │
                    │  - Decision making  │
                    │  - Action execution │
                    └────────┬────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    ┌────────┐          ┌─────────┐          ┌──────────┐
    │ ALLOW  │          │CHALLENGE│          │ QUARANTINE
    │        │          │ (MFA)   │          │   /DENY
    └────────┘          └─────────┘          └──────────┘
```

---

## Layer Architecture

### 1. Behavioral Capture Layer (`agent/`)

**Purpose**: Collect behavioral data dari entitas digital untuk membuat unique behavioral profile.

**Components**:
- `BehavioralCapture` class
- Multiple capture methods:
  - Keystroke dynamics
  - CPU/Memory usage
  - API call patterns
  - Network patterns
  - Login patterns
  - File access patterns

**Key Features**:
- Real-time capture atau mock data generation
- Metadata enrichment (timestamp, source, context)
- Initial anomaly scoring
- Vector hashing untuk integrity

**Data Flow**:
```
Entity Activity → Capture Methods → BehavioralVector Objects
    ↓
  Mock Data / Real Sensors
    ↓
  [Vector_1, Vector_2, ... Vector_N]
    ↓
  JSON Export / Pickle Serialization
```

**Output**:
```json
{
  "vectors": [
    {
      "vector_id": "user_alice_keystroke_1234567890",
      "entity_id": "user_alice",
      "behavior_type": "keystroke",
      "value": 65.5,
      "timestamp": "2025-11-14T10:30:00",
      "anomaly_level": "NORMAL",
      "hash_value": "a1b2c3d4e5f6..."
    }
  ]
}
```

---

### 2. DNA Generation Layer (`generator/`)

**Purpose**: Convert behavioral vectors into unique, verifiable Digital DNA.

**Components**:
- `DNAGenerator` class
- `DigitalDNA` data class
- `DNAFactory` for multi-entity management

**Key Features**:
- Vector normalization (0-1 range)
- Shannon entropy calculation
- Composite hashing (SHA256/SHA512/BLAKE2)
- Mock cryptographic signing
- DNA versioning & TTL management
- DNA rotation mechanism

**Algorithms**:

#### Entropy Calculation
```
1. Normalize vectors to [0, 1]
2. For each vector value v:
   entropy -= v * (v^2)
3. Final entropy = entropy / (max_possible * vector_count)
Result: 0.0-1.0 score representing behavioral uniqueness
```

#### Composite Hash
```
1. Sort vectors by behavior type
2. For each vector:
   hash_input = "index:type:normalized_value:timestamp"
3. Combined = hash_input_1 | hash_input_2 | ... | hash_input_N
4. Final Hash = SHA256(Combined)
Result: 64-character hex string representing DNA fingerprint
```

**DNA Lifecycle**:
```
Generation → Validation → Active Use (30 days) → Expiration
    ↓            ↓              ↓                    ↓
  Hash       Verify Format   Cached             Retired
Signature   Check Entropy    in System           Archive
```

**Output**:
```json
{
  "dna_id": "DNA_user_alice_1234567890_abcd1234",
  "entity_id": "user_alice",
  "dna_hash": "a1b2c3d4e5f6g7h8...",
  "entropy_score": 0.756,
  "dna_signature": "signature_hash_xyz...",
  "is_valid": true,
  "expiration_timestamp": "2025-12-14T10:30:00"
}
```

---

### 3. Local Verification Layer (`verification/`)

**Purpose**: Verify DNA locally dan detect behavioral anomalies/threats.

**Components**:
- `LocalVerifier` class
- `BehavioralBaseline` class
- Multiple detection methods:
  - Format verification
  - Hash integrity check
  - Anomaly detection
  - Spoofing detection
  - Insider threat detection
  - Credential theft detection
  - Behavioral drift detection

**Verification Flow**:

```
Input: DNA Object + Current Behavioral Vectors
  ↓
1. Format Verification
   - Check required fields
   - Validate hash format
   - Check entropy score
  ↓
2. Baseline Comparison
   - Extract statistical profile dari baseline
   - Calculate Z-scores untuk current vectors
   - Identify statistical outliers (>3σ)
  ↓
3. Threat Detection Modules
   - Spoofing Risk: keystroke variance, device consistency
   - Insider Risk: file access, API calls, privilege escalation
   - Credential Theft: velocity checks, automation patterns
   - Behavioral Drift: deviation dari baseline mean
  ↓
4. Threat Scoring
   - Combine individual threat scores
   - Adjust confidence based on threats
   - Determine threat level (SAFE/LOW/MEDIUM/HIGH/CRITICAL)
  ↓
Output: VerificationResult with confidence_score + threat_level
```

**Anomaly Detection Algorithms**:

#### Z-Score Analysis
```
Z = (X - mean) / std_dev

If |Z| > 3: Critical anomaly
If 2 < |Z| ≤ 3: Significant anomaly
If |Z| ≤ 2: Normal behavior
```

#### Behavioral Drift
```
normalized_drift = |current_mean - baseline_mean| / baseline_std_dev
If normalized_drift > 2.5: Behavioral drift detected
```

**Output**:
```json
{
  "verification_id": "VER_user_alice_123456789",
  "is_valid": true,
  "confidence_score": 0.87,
  "threat_level": "LOW",
  "detected_threats": [],
  "anomaly_indicators": ["slight_keystroke_variance"],
  "recommendations": ["allow_access_with_monitoring"]
}
```

---

### 4. Federated Verification Layer (`federated/`)

**Purpose**: Enable cross-node DNA verification dan consensus.

**Components**:
- `FederatedNode` class
- `FederatedNetwork` class
- `ZKProofStub` class
- `ConsensusResult` class

**Network Topology**: Mesh network (all nodes connected)

**Communication Flow**:

```
Node A                        Node B
  │                             │
  ├──> Send Verification ───────┤
  │    Request                  ├──> Verify DNA Locally
  │                             ├──> Create ZK-Proof
  │    ◄────Response with ──────┤
  │         ZK-Proof            │
  │
Verify ZK-Proof
Combine Results
```

**Zero-Knowledge Proof (Stub)**:

```
Current: Simplified mock implementation
Future: Real ZK protocol (Schnorr, Fiat-Shamir, etc.)

Commitment = H(DNA_hash || random_nonce)
Challenge = Random challenge from verifier
Response = H(Commitment || Challenge || DNA_hash)

Verification = Recompute and compare
```

**Consensus Mechanisms**:

1. **MAJORITY**: > 50% nodes agree
2. **QUORUM**: ≥ 2/3 nodes agree
3. **UNANIMOUS**: 100% nodes agree

```
Votes from nodes:
[TRUE, TRUE, FALSE, TRUE]

Majority: 3/4 = 75% → TRUE ✓
Quorum: 3/4 ≥ 66.7% → TRUE ✓
Unanimous: 3/4 = 75% ≠ 100% → FALSE ✗
```

**Output**:
```json
{
  "consensus_id": "CONS_node_01_user_alice_123456789",
  "consensus_reached": true,
  "consensus_type": "majority",
  "participating_nodes": ["node_01", "node_02", "node_03"],
  "confidence_score": 0.82,
  "timestamp": "2025-11-14T10:30:00"
}
```

---

### 5. Policy Engine Layer (`policy/`)

**Purpose**: Make access control decisions berdasarkan verification results.

**Components**:
- `PolicyEngine` class
- `PolicyRule` class
- `AccessControlDecision` class

**Decision Types**:
1. **ALLOW** - Grant access immediately
2. **CHALLENGE** - Request additional verification (MFA, CAPTCHA, behavioral challenge)
3. **QUARANTINE** - Block access, log incident, alert security
4. **DENY** - Reject access explicitly

**Policy Rule Types**:

```
1. Confidence-Based Rules
   IF confidence_score > 0.9 THEN ALLOW

2. Threat-Based Rules
   IF threat_level == CRITICAL THEN DENY

3. Behavioral-Based Rules
   IF behavioral_drift > threshold THEN CHALLENGE

4. Time-Based Rules
   IF time_of_access == unusual_hour THEN CHALLENGE

5. Location-Based Rules
   IF location_distance_impossible THEN QUARANTINE

6. Custom Rules
   Complex combinations of conditions
```

**Decision Logic**:

```
Input: VerificationResult + ConsensusResult (optional)
  │
  ├─> Find matching policy rules
  ├─> Sort by priority
  ├─> Apply highest priority rule
  │
  ├─> IF high_confidence + no_threats
  │   └─> ALLOW
  │
  ├─> ELSE IF medium_confidence + low_threats
  │   └─> CHALLENGE (MFA or behavioral)
  │
  ├─> ELSE IF low_confidence + medium_threats
  │   └─> QUARANTINE
  │
  └─> ELSE IF multiple_threats + critical_level
      └─> DENY + ALERT

Output: AccessControlDecision
  - decision (ALLOW/CHALLENGE/QUARANTINE/DENY)
  - confidence_score
  - applied_rules
  - recommendations
```

**Output**:
```json
{
  "decision_id": "DEC_user_alice_123456789",
  "decision": "challenge",
  "confidence_score": 0.75,
  "threat_level": "MEDIUM",
  "challenge_method": "mfa_totp",
  "recommendations": [
    "trigger_mfa_verification",
    "log_anomaly",
    "notify_user"
  ]
}
```

---

## Data Models

### BehavioralVector
```python
@dataclass
class BehavioralVector:
    vector_id: str
    entity_id: str
    behavior_type: str  # keystroke, cpu_usage, api_call, etc.
    timestamp: str
    value: float  # 0-100 normalized
    metadata: Dict  # behavior-specific data
    hash_value: str
    anomaly_level: str  # NORMAL, SUSPICIOUS, CRITICAL
```

### DigitalDNA
```python
@dataclass
class DigitalDNA:
    dna_id: str
    entity_id: str
    generation_timestamp: str
    expiration_timestamp: str
    dna_hash: str  # Composite hash
    dna_signature: str  # Cryptographic signature
    entropy_score: float  # 0.0-1.0
    vector_count: int
    version: str
    algorithm: str
    behavioral_profile_hash: str
    metadata: Dict
    is_valid: bool
```

### VerificationResult
```python
@dataclass
class VerificationResult:
    verification_id: str
    entity_id: str
    dna_hash: str
    is_valid: bool
    confidence_score: float  # 0.0-1.0
    threat_level: str  # SAFE, LOW, MEDIUM, HIGH, CRITICAL
    detected_threats: List[str]
    anomaly_indicators: List[str]
    recommendations: List[str]
```

### AccessControlDecision
```python
@dataclass
class AccessControlDecision:
    decision_id: str
    entity_id: str
    decision: str  # allow, challenge, quarantine, deny
    confidence_score: float  # 0.0-1.0
    threat_level: str
    applied_rules: List[str]
    recommendations: List[str]
    challenge_method: Optional[str]
    quarantine_reason: Optional[str]
```

---

## Scalability Considerations

### Horizontal Scaling
- Federated nodes dapat di-scale independently
- Each node dapat verify multiple entities
- Consensus dari n nodes

### Performance
- Vector capture: < 100ms per dimension
- DNA generation: < 500ms per entity
- Local verification: < 200ms
- Federated consensus: < 2s (3 nodes)
- Policy decision: < 100ms

### Storage
- Per entity per day: ~1KB (compressed vectors)
- DNA history (30 days): ~50KB per entity
- Total for 10K entities: ~500MB

---

## Security Considerations

### Threat Model
1. **DNA Forgery** - Attacker membuat fake DNA
   - Mitigation: Cryptographic signing, entropy validation

2. **Vector Spoofing** - Attacker meniru behavioral vectors
   - Mitigation: Multiple dimensions, statistical analysis, ZK-proof

3. **Replay Attacks** - Attacker merepeat old DNA/vectors
   - Mitigation: Timestamps, TTL, nonce validation

4. **Man-in-the-Middle** - Attacker intercept communication
   - Mitigation: Message signing, federated consensus

### Privacy
- Behavioral data disimpan locally pada device
- Cross-node sharing via ZK-proof (no actual DNA)
- Optional: Federated learning untuk policy updates

---

## Future Enhancements

1. **Machine Learning**
   - Anomaly detection dengan neural networks
   - Adaptive policy learning
   - Behavior prediction models

2. **Real Cryptography**
   - Full zero-knowledge proof implementation
   - RSA/ECDSA signing
   - TLS untuk node communication

3. **Advanced Threat Detection**
   - Graph analysis untuk insider threats
   - Temporal pattern analysis
   - Multi-entity correlation

4. **Blockchain Integration**
   - Immutable DNA audit trail
   - Decentralized consensus
   - Smart contract policies

5. **Real-Time Streaming**
   - Kafka/Pulsar untuk vector streaming
   - Online anomaly detection
   - Real-time policy updates

---

**Last Updated**: November 14, 2025
**Version**: MVP 0.1.0
