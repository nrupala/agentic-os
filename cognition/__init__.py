"""
Paradise Stack v2.0 - High-Fidelity Development Organization
Cognitive AI Agent System with Multi-Layer Engineering Teams
Inspired by marimo's reactive programming model

Key Features:
- Reactive Execution (DAG-based)
- No Hidden State
- Lazy/Stale Mode
- Interactive UI Elements
- Agent Pairing
- PDCA Loops
- Meta-Cognition
- Knowledge Retention
"""

from .knowledge_graph import (
    KnowledgeGraph,
    Entity,
    Blob,
    Carrier,
    Placeholder,
    get_graph,
)

from .meta_cognition import (
    MetaCognition,
    RAGEngine,
    GANGenerator,
    RNNProcessor,
    LoopDetector,
    get_meta_cognition,
    get_rag,
    get_gan,
    get_rnn,
)

from .self_improvement import (
    Memory,
    SelfImprover,
    StrategyOptimizer,
    ImprovementLoop,
    get_memory,
    get_self_improver,
    get_optimizer,
    get_loop,
)

from .entities import (
    EntityRegistry,
    CognitiveCarrier,
    Container,
    DataBlob,
    TaskPlaceholder,
    get_registry,
    create_default_carriers,
)

from .verification import (
    VerificationEngine,
    VerificationResult,
    PDCAVerifier,
    LoopDetector as VerifLoopDetector,
)

from .engineering_teams import (
    EngineeringOrganization,
    FeatureEngineer,
    FunctionEngineer,
    GuardianAgent,
    ExecutorAgent,
    ImproverAgent,
    PerformanceEngineer,
    SecurityEngineer,
    TeamHandoffManager,
    Handoff,
    ReviewCycle,
    TeamLevel,
    HandoffStatus,
    get_organization,
)

from .pdc_orchestrator import (
    PDCAOrchestrator,
    PDCALoop,
    LoopState,
    get_orchestrator,
    initialize,
    run_development,
)

from .master_orchestrator import (
    MasterOrchestrator,
    OrganizationalMetrics,
    StrategicDecision,
    SelfHealingManager,
    KnowledgeRetentionManager,
    ContinuousImprovementEngine,
    get_master_orchestrator,
    run_organization,
)

# NEW: Reactive Engine (from marimo-inspired)
from .reactive_engine import (
    ReactiveEngine,
    Cell,
    CellState,
    DAG,
    ReactiveOrchestrator,
    get_reactive_engine,
)

# NEW: Notebook System (marimo-inspired)
from .notebook import (
    ParadiseNotebook,
    ParadiseUI,
    UIElement,
    ElementType,
    NotebookCell,
    DevelopmentSession,
    get_notebook,
    create_session,
)

# NEW: Agent Pairing System (marimo pair-inspired)
from .agent_pairing import (
    AgentPairingSystem,
    Agent,
    AgentPair,
    AgentRole,
    Message,
    Tool,
    SharedContext,
    get_pairing_system,
)

__version__ = "2.0.0"
__all__ = [
    # Knowledge Graph
    "KnowledgeGraph",
    "Entity",
    "Blob",
    "Carrier",
    "Placeholder",
    "get_graph",
    
    # Meta-Cognition
    "MetaCognition",
    "RAGEngine",
    "GANGenerator",
    "RNNProcessor",
    "LoopDetector",
    "get_meta_cognition",
    "get_rag",
    "get_gan",
    "get_rnn",
    
    # Self-Improvement
    "Memory",
    "SelfImprover",
    "StrategyOptimizer",
    "ImprovementLoop",
    "get_memory",
    "get_self_improver",
    "get_optimizer",
    "get_loop",
    
    # Entities
    "EntityRegistry",
    "CognitiveCarrier",
    "Container",
    "DataBlob",
    "TaskPlaceholder",
    "get_registry",
    "create_default_carriers",
    
    # Verification
    "VerificationEngine",
    "VerificationResult",
    "PDCAVerifier",
    "get_orchestrator",
    
    # Engineering Teams
    "EngineeringOrganization",
    "FeatureEngineer",
    "FunctionEngineer",
    "GuardianAgent",
    "ExecutorAgent",
    "ImproverAgent",
    "PerformanceEngineer",
    "SecurityEngineer",
    "TeamHandoffManager",
    "Handoff",
    "ReviewCycle",
    "TeamLevel",
    "HandoffStatus",
    "get_organization",
    
    # Orchestrators
    "PDCAOrchestrator",
    "PDCALoop",
    "LoopState",
    "MasterOrchestrator",
    "OrganizationalMetrics",
    "StrategicDecision",
    "SelfHealingManager",
    "KnowledgeRetentionManager",
    "ContinuousImprovementEngine",
    "get_master_orchestrator",
    "run_organization",
    
    # Reactive Engine (NEW - marimo-inspired)
    "ReactiveEngine",
    "Cell",
    "CellState",
    "DAG",
    "ReactiveOrchestrator",
    "get_reactive_engine",
    
    # Notebook System (NEW - marimo-inspired)
    "ParadiseNotebook",
    "ParadiseUI",
    "UIElement",
    "ElementType",
    "NotebookCell",
    "DevelopmentSession",
    "get_notebook",
    "create_session",
    
    # Agent Pairing (NEW - marimo pair-inspired)
    "AgentPairingSystem",
    "Agent",
    "AgentPair",
    "AgentRole",
    "Message",
    "Tool",
    "SharedContext",
    "get_pairing_system",
]

__org_structure__ = {
    "CEO": "MasterOrchestrator",
    "CLO": "MetaCognition",
    "CISO": "SecurityEngineer",
    "CTO": "PDCAOrchestrator",
    "Intelligence_Division": {
        "Knowledge_Graph": "KnowledgeGraph",
        "RAG_Engine": "RAGEngine",
        "RNN_Processor": "RNNProcessor",
        "GAN_Generator": "GANGenerator",
        "Memory": "Memory",
    },
    "Reactive_Division": {
        "Reactive_Engine": "ReactiveEngine",
        "Notebook_System": "ParadiseNotebook",
        "Agent_Pairing": "AgentPairingSystem",
    },
    "Engineering_Teams": {
        "Junior": ["FeatureEngineer", "FunctionEngineer"],
        "Mid": ["GuardianAgent", "ExecutorAgent"],
        "Senior": ["ImproverAgent", "PerformanceEngineer", "SecurityEngineer"],
    },
    "Quality_Division": ["VerificationEngine", "PDCAVerifier"],
    "Delivery_Gates": ["CodeComplete", "QualityGate", "AcceptanceGate"],
}
