"""
Policy Engine Module - Digital DNA MVP

Modul ini bertanggung jawab untuk policy enforcement dan access control decisions.
Termasuk: policy evaluation, decision making (allow/challenge/quarantine), dan adaptive policies.

Author: Digital DNA Team
Version: 0.1.0
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AccessDecision(Enum):
    """Enum untuk access control decision."""
    ALLOW = "allow"
    CHALLENGE = "challenge"
    QUARANTINE = "quarantine"
    DENY = "deny"


class PolicyRuleType(Enum):
    """Enum untuk tipe policy rule."""
    THREAT_BASED = "threat_based"
    CONFIDENCE_BASED = "confidence_based"
    BEHAVIORAL_BASED = "behavioral_based"
    TIME_BASED = "time_based"
    LOCATION_BASED = "location_based"
    CUSTOM = "custom"


@dataclass
class PolicyRule:
    """Data class untuk policy rule."""
    rule_id: str
    rule_name: str
    rule_type: str
    conditions: Dict[str, Any]
    actions: List[str]
    priority: int
    is_enabled: bool
    created_timestamp: str


@dataclass
class AccessControlDecision:
    """Data class untuk access control decision."""
    decision_id: str
    entity_id: str
    decision: str
    confidence_score: float
    threat_level: str
    applied_rules: List[str]
    decision_timestamp: str
    decision_details: Dict[str, Any]
    challenge_method: Optional[str] = None
    quarantine_reason: Optional[str] = None


class PolicyEngine:
    """
    Kelas untuk policy enforcement dan access control decisions.
    
    Fitur:
    - Policy rule evaluation
    - Multi-factor decision making
    - Adaptive policies berdasarkan threat level
    - Decision audit trail
    - Support multiple rule types
    - Contextual decision making
    
    Decision Logic:
    - ALLOW: DNA valid, confidence tinggi, no threats
    - CHALLENGE: DNA suspicious, perlu additional verification (MFA, behavioral challenges)
    - QUARANTINE: High risk atau multiple threats detected
    - DENY: Critical threats, format errors, atau policy violation
    
    TODO: Implement machine learning untuk adaptive policies
    TODO: Implement real-time policy updates
    TODO: Implement policy conflict resolution
    """

    def __init__(self):
        """Inisialisasi PolicyEngine."""
        self.rules: Dict[str, PolicyRule] = {}
        self.decisions_history: List[AccessControlDecision] = []
        self.rule_counter = 0
        
        # Initialize default policies
        self._initialize_default_policies()
        
        logger.info("PolicyEngine initialized with default policies")

    def _initialize_default_policies(self):
        """Initialize default policy rules."""
        
        # Rule 1: High Confidence Allow
        self.add_rule(
            rule_name="High Confidence Allow",
            rule_type=PolicyRuleType.CONFIDENCE_BASED,
            conditions={
                "confidence_score_min": 0.9,
                "threat_level_max": "LOW",
                "dna_valid": True
            },
            actions=["allow"],
            priority=10
        )
        
        # Rule 2: Moderate Confidence Challenge
        self.add_rule(
            rule_name="Moderate Confidence Challenge",
            rule_type=PolicyRuleType.CONFIDENCE_BASED,
            conditions={
                "confidence_score_min": 0.7,
                "confidence_score_max": 0.89,
                "threat_level_max": "MEDIUM"
            },
            actions=["challenge_mfa", "challenge_behavioral"],
            priority=8
        )
        
        # Rule 3: Low Confidence Quarantine
        self.add_rule(
            rule_name="Low Confidence Quarantine",
            rule_type=PolicyRuleType.CONFIDENCE_BASED,
            conditions={
                "confidence_score_max": 0.6,
                "threat_level_max": "HIGH"
            },
            actions=["quarantine"],
            priority=6
        )
        
        # Rule 4: Critical Threat Deny
        self.add_rule(
            rule_name="Critical Threat Deny",
            rule_type=PolicyRuleType.THREAT_BASED,
            conditions={
                "threat_level_exact": "CRITICAL"
            },
            actions=["deny", "alert_security"],
            priority=1
        )
        
        # Rule 5: High Threat Quarantine
        self.add_rule(
            rule_name="High Threat Quarantine",
            rule_type=PolicyRuleType.THREAT_BASED,
            conditions={
                "threat_level_exact": "HIGH"
            },
            actions=["quarantine", "notify_admin"],
            priority=2
        )
        
        # Rule 6: Spoofing Detected
        self.add_rule(
            rule_name="Spoofing Detected",
            rule_type=PolicyRuleType.THREAT_BASED,
            conditions={
                "threats_contain": "SPOOFING_DETECTED"
            },
            actions=["challenge_identity_verification", "log_incident"],
            priority=3
        )
        
        # Rule 7: Invalid DNA Format
        self.add_rule(
            rule_name="Invalid DNA Format",
            rule_type=PolicyRuleType.BEHAVIORAL_BASED,
            conditions={
                "dna_valid": False
            },
            actions=["deny", "alert_security"],
            priority=2
        )

    def add_rule(
        self,
        rule_name: str,
        rule_type: PolicyRuleType,
        conditions: Dict[str, Any],
        actions: List[str],
        priority: int
    ) -> PolicyRule:
        """
        Add new policy rule.
        
        Args:
            rule_name: Nama rule
            rule_type: Tipe rule
            conditions: Kondisi untuk rule activation
            actions: Actions untuk dijalankan jika rule matched
            priority: Priority level (1-10, lower = higher priority)
            
        Returns:
            PolicyRule yang dibuat
        """
        self.rule_counter += 1
        rule_id = f"RULE_{self.rule_counter:04d}"
        
        rule = PolicyRule(
            rule_id=rule_id,
            rule_name=rule_name,
            rule_type=rule_type.value,
            conditions=conditions,
            actions=actions,
            priority=priority,
            is_enabled=True,
            created_timestamp=datetime.utcnow().isoformat()
        )
        
        self.rules[rule_id] = rule
        logger.info(f"Policy rule added: {rule_id} - {rule_name}")
        return rule

    def evaluate_access(
        self,
        entity_id: str,
        verification_result: Dict[str, Any],
        consensus_result: Optional[Dict[str, Any]] = None
    ) -> AccessControlDecision:
        """
        Evaluate access berdasarkan verification result dan policies.
        
        Args:
            entity_id: ID entitas
            verification_result: Hasil verifikasi DNA lokal
            consensus_result: Hasil consensus federated (optional)
            
        Returns:
            AccessControlDecision dengan decision lengkap
        """
        logger.info(f"Evaluating access for {entity_id}")
        
        decision_id = f"DEC_{entity_id}_{int(datetime.utcnow().timestamp() * 1000)}"
        
        # Extract relevant information
        is_valid = verification_result.get("is_valid", False)
        confidence_score = verification_result.get("confidence_score", 0.0)
        threat_level = verification_result.get("threat_level", "UNKNOWN")
        detected_threats = verification_result.get("detected_threats", [])
        
        # Incorporate federated consensus if available
        if consensus_result:
            consensus_confidence = consensus_result.get("confidence_score", 0.5)
            confidence_score = (confidence_score + consensus_confidence) / 2
        
        # Find matching rules (sorted by priority)
        matching_rules = self._find_matching_rules(
            is_valid=is_valid,
            confidence_score=confidence_score,
            threat_level=threat_level,
            detected_threats=detected_threats
        )
        
        # Make decision based on highest priority matching rule
        decision = AccessDecision.ALLOW
        challenge_method = None
        quarantine_reason = None
        applied_rules = []
        
        if matching_rules:
            for rule in matching_rules:
                applied_rules.append(rule.rule_id)
                decision = self._get_decision_from_rule(rule)
                
                if any("challenge" in (a or "").lower() for a in rule.actions):
                    # prefer explicit challenge action if present
                    for a in rule.actions:
                        if a and "challenge" in a.lower():
                            challenge_method = a
                            break
                    else:
                        challenge_method = rule.actions[0] if rule.actions else None
                
                if decision == AccessDecision.QUARANTINE:
                    quarantine_reason = rule.rule_name
                
                # Use highest priority rule's decision
                break
        else:
            # Default: if no rules match and verification is valid, allow
            decision = AccessDecision.ALLOW if is_valid else AccessDecision.CHALLENGE
        
        decision_details = {
            "verification_result": verification_result,
            "consensus_result": consensus_result,
            "matching_rules": [asdict(r) for r in matching_rules[:3]],
            "confidence_breakdown": {
                "local_confidence": verification_result.get("confidence_score", 0),
                "federated_confidence": consensus_result.get("confidence_score", 0) if consensus_result else None,
                "final_confidence": confidence_score
            }
        }
        
        access_decision = AccessControlDecision(
            decision_id=decision_id,
            entity_id=entity_id,
            decision=decision.value,
            confidence_score=confidence_score,
            threat_level=threat_level,
            applied_rules=applied_rules,
            decision_timestamp=datetime.utcnow().isoformat(),
            decision_details=decision_details,
            challenge_method=challenge_method,
            quarantine_reason=quarantine_reason
        )
        
        self.decisions_history.append(access_decision)
        
        logger.info(f"Access decision: {decision.value} (confidence={confidence_score:.2f}, threat={threat_level})")
        return access_decision

    def _find_matching_rules(
        self,
        is_valid: bool,
        confidence_score: float,
        threat_level: str,
        detected_threats: List[str]
    ) -> List[PolicyRule]:
        """
        Find matching policy rules berdasarkan kondisi.
        
        Returns:
            List of matching rules sorted by priority
        """
        matching_rules = []
        
        for rule in self.rules.values():
            if not rule.is_enabled:
                continue
            
            if self._evaluate_rule_conditions(
                rule,
                is_valid,
                confidence_score,
                threat_level,
                detected_threats
            ):
                matching_rules.append(rule)
        
        # Sort by priority (lower number = higher priority)
        matching_rules.sort(key=lambda r: r.priority)
        return matching_rules

    def _evaluate_rule_conditions(
        self,
        rule: PolicyRule,
        is_valid: bool,
        confidence_score: float,
        threat_level: str,
        detected_threats: List[str]
    ) -> bool:
        """
        Evaluate jika rule conditions terpenuhi.
        
        Returns:
            True jika semua conditions terpenuhi
        """
        conditions = rule.conditions
        
        # Check confidence score conditions
        if "confidence_score_min" in conditions:
            if confidence_score < conditions["confidence_score_min"]:
                return False
        
        if "confidence_score_max" in conditions:
            if confidence_score > conditions["confidence_score_max"]:
                return False
        
        # Check threat level conditions
        if "threat_level_exact" in conditions:
            if threat_level != conditions["threat_level_exact"]:
                return False
        
        if "threat_level_max" in conditions:
            threat_levels = ["SAFE", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
            max_level = threat_levels.index(conditions["threat_level_max"])
            current_level = threat_levels.index(threat_level) if threat_level in threat_levels else -1
            
            if current_level > max_level:
                return False
        
        # Check DNA validity
        if "dna_valid" in conditions:
            if is_valid != conditions["dna_valid"]:
                return False
        
        # Check threat presence
        if "threats_contain" in conditions:
            threat_keyword = conditions["threats_contain"]
            if not any(threat_keyword in t for t in detected_threats):
                return False
        
        return True

    def _get_decision_from_rule(self, rule: PolicyRule) -> AccessDecision:
        """
        Determine access decision dari rule actions.
        
        Returns:
            AccessDecision
        """
        actions = rule.actions
        
        # Determine primary decision
        if "deny" in actions:
            return AccessDecision.DENY
        elif "quarantine" in actions:
            return AccessDecision.QUARANTINE
        elif any("challenge" in a for a in actions):
            return AccessDecision.CHALLENGE
        else:
            return AccessDecision.ALLOW

    def override_decision(
        self,
        decision_id: str,
        new_decision: AccessDecision,
        reason: str
    ):
        """
        Override previous decision (administrative override).
        
        Args:
            decision_id: ID dari decision yang akan di-override
            new_decision: Decision baru
            reason: Alasan override
        """
        for decision in self.decisions_history:
            if decision.decision_id == decision_id:
                old_decision = decision.decision
                decision.decision = new_decision.value
                decision.decision_details["override"] = {
                    "old_decision": old_decision,
                    "new_decision": new_decision.value,
                    "reason": reason,
                    "override_timestamp": datetime.utcnow().isoformat()
                }
                logger.info(f"Decision overridden: {decision_id} ({old_decision} -> {new_decision.value})")
                return
        
        logger.warning(f"Decision not found: {decision_id}")

    def enable_rule(self, rule_id: str):
        """Enable policy rule."""
        if rule_id in self.rules:
            self.rules[rule_id].is_enabled = True
            logger.info(f"Rule enabled: {rule_id}")

    def disable_rule(self, rule_id: str):
        """Disable policy rule."""
        if rule_id in self.rules:
            self.rules[rule_id].is_enabled = False
            logger.info(f"Rule disabled: {rule_id}")

    def get_all_rules(self) -> List[PolicyRule]:
        """Get semua policy rules."""
        return list(self.rules.values())

    def get_decisions_history(self) -> List[AccessControlDecision]:
        """Get semua decisions history."""
        return self.decisions_history

    def get_decision_statistics(self) -> Dict[str, Any]:
        """Get statistik decisions."""
        if not self.decisions_history:
            return {}
        
        total = len(self.decisions_history)
        decisions_count = {}
        threat_counts = {}
        
        for decision in self.decisions_history:
            # Count decisions
            decision_type = decision.decision
            decisions_count[decision_type] = decisions_count.get(decision_type, 0) + 1
            
            # Count threats
            for threat in decision.decision_details.get("verification_result", {}).get("detected_threats", []):
                threat_counts[threat] = threat_counts.get(threat, 0) + 1
        
        return {
            "total_decisions": total,
            "decisions_by_type": decisions_count,
            "top_threats": sorted(threat_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "avg_confidence": sum(d.confidence_score for d in self.decisions_history) / total
        }


if __name__ == "__main__":
    # Test code
    logger.info("=" * 80)
    logger.info("POLICY ENGINE MODULE TEST")
    logger.info("=" * 80)
    
    # Create policy engine
    engine = PolicyEngine()
    
    # Create mock verification result
    mock_verification = {
        "is_valid": True,
        "confidence_score": 0.85,
        "threat_level": "LOW",
        "detected_threats": [],
        "verification_id": "VER_test_001"
    }
    
    # Evaluate access
    logger.info("\nEvaluating access with high confidence and low threat...")
    decision_1 = engine.evaluate_access("test_user_001", mock_verification)
    
    logger.info(f"\nDecision Result:")
    logger.info(f"  Decision: {decision_1.decision}")
    logger.info(f"  Confidence: {decision_1.confidence_score:.2f}")
    logger.info(f"  Applied Rules: {decision_1.applied_rules}")
    
    # Test with high threat
    logger.info("\n" + "=" * 80)
    logger.info("Evaluating access with HIGH threat...")
    mock_verification_threat = {
        "is_valid": False,
        "confidence_score": 0.3,
        "threat_level": "CRITICAL",
        "detected_threats": ["SPOOFING_DETECTED", "INSIDER_THREAT_DETECTED"],
        "verification_id": "VER_test_002"
    }
    
    decision_2 = engine.evaluate_access("test_user_002", mock_verification_threat)
    
    logger.info(f"\nDecision Result:")
    logger.info(f"  Decision: {decision_2.decision}")
    logger.info(f"  Confidence: {decision_2.confidence_score:.2f}")
    logger.info(f"  Threat Level: {decision_2.threat_level}")
    logger.info(f"  Quarantine Reason: {decision_2.quarantine_reason}")
    
    # Display all rules
    logger.info("\n" + "=" * 80)
    logger.info("All Policy Rules:")
    for rule in engine.get_all_rules():
        logger.info(f"  {rule.rule_id}: {rule.rule_name} (priority={rule.priority})")
