"""
Main runner for Digital DNA MVP demo workflow

This script wires together agent -> generator -> verification -> federated -> policy
and runs a mock workflow to demonstrate the prototype.
"""

import logging
from agent.agent import BehavioralCapture, generate_mock_entities
from generator.dna_generator import DNAGenerator, DNAFactory
from verification.local_verifier import LocalVerifier
from federated.node import FederatedNetwork, FederatedNode, ConsensusType
from policy.access_control import PolicyEngine
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting Digital DNA MVP demo workflow")

    # 1. Create mock entities
    entities = generate_mock_entities()

    # 2. Initialize factories and services
    dna_factory = DNAFactory()
    policy_engine = PolicyEngine()

    # 3. Create federated network with 2 nodes
    network = FederatedNetwork()
    node_a = FederatedNode("node_alpha", node_type="verifier")
    node_b = FederatedNode("node_beta", node_type="verifier")

    network.add_node(node_a)
    network.add_node(node_b)
    network.connect_all_nodes()

    # 4. Simulate capture, DNA generation, local verification, federated consensus, and policy decision
    for entity_id, agent in entities.items():
        logger.info(f"\n--- Processing entity: {entity_id} ---")

        # Generate behavioral profile
        profile = agent.generate_mock_profile()
        vectors = profile["vectors"]

        # Generate DNA
        generator = dna_factory.create_generator(entity_id, agent.entity_type)
        dna = generator.generate_dna(vectors)

        # Local verification
        verifier = LocalVerifier(entity_id, agent.entity_type)
        verifier.establish_baseline(vectors)
        verification_result = verifier.verify_dna(dna.__dict__, vectors)

        # Federated consensus
        consensus = node_a.initiate_consensus(entity_id, dna.dna_hash, ConsensusType.MAJORITY)

        # Policy decision
        consensus_payload = {
            "confidence_score": consensus.confidence_score,
            "consensus_reached": consensus.consensus_reached
        }
        decision = policy_engine.evaluate_access(entity_id, verification_result.__dict__, consensus_payload)

        logger.info(f"Final Decision for {entity_id}: {decision.decision} (confidence={decision.confidence_score:.2f})")
        time.sleep(0.2)

    logger.info("Demo workflow complete")


if __name__ == "__main__":
    main()
