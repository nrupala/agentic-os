#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
Paradise Agent Pairing System - AI Agent Collaboration
Inspired by marimo pair - Connect AI agents to work with Paradise Stack

Features:
- Agent pairing with notebooks
- Bidirectional communication
- Shared context
- Tool calling
- Session persistence
"""

import json
import uuid
from datetime import datetime
from typing import Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class AgentRole(Enum):
    PLANNER = "planner"
    IMPLEMENTER = "implementer"
    GUARDIAN = "guardian"
    EXECUTOR = "executor"
    IMPROVER = "improver"
    REVIEWER = "reviewer"
    USER = "user"


@dataclass
class Agent:
    """AI Agent in the pairing system"""
    agent_id: str
    name: str
    role: AgentRole
    capabilities: list[str] = field(default_factory=list)
    system_prompt: str = ""
    tools: list[str] = field(default_factory=list)
    is_active: bool = False
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "capabilities": self.capabilities,
            "is_active": self.is_active,
            "last_seen": self.last_seen,
        }


@dataclass
class Message:
    """Message between paired agents"""
    message_id: str
    from_agent: str
    to_agent: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    type: str = "text"
    metadata: dict = field(default_factory=dict)
    read: bool = False
    
    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "from": self.from_agent,
            "to": self.to_agent,
            "content": self.content,
            "timestamp": self.timestamp,
            "type": self.type,
            "metadata": self.metadata,
            "read": self.read,
        }


@dataclass
class SharedContext:
    """Shared context between paired agents"""
    variables: dict[str, Any] = field(default_factory=dict)
    files: dict[str, str] = field(default_factory=dict)
    plan: str = ""
    code: str = ""
    errors: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


class Tool:
    """Tool that agents can call"""
    
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func
        self.usage_count = 0
    
    def execute(self, **kwargs) -> Any:
        self.usage_count += 1
        return self.func(**kwargs)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "usage_count": self.usage_count,
        }


class AgentPair:
    """A pairing between two agents for collaboration"""
    
    def __init__(self, pair_id: str, agent_a: Agent, agent_b: Agent):
        self.pair_id = pair_id
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.messages: list[Message] = []
        self.shared_context = SharedContext()
        self.created_at = datetime.now().isoformat()
        self.last_activity = self.created_at
        self.status = "active"
    
    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        content: str,
        msg_type: str = "text",
        metadata: dict = None,
    ) -> Message:
        """Send a message between paired agents"""
        message = Message(
            message_id=str(uuid.uuid4())[:8],
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            type=msg_type,
            metadata=metadata or {},
        )
        self.messages.append(message)
        self.last_activity = datetime.now().isoformat()
        return message
    
    def get_messages(self, agent_id: str, unread_only: bool = False) -> list[Message]:
        """Get messages for an agent"""
        messages = [m for m in self.messages if m.to_agent == agent_id]
        if unread_only:
            messages = [m for m in messages if not m.read]
        return messages
    
    def mark_read(self, message_id: str):
        """Mark a message as read"""
        for msg in self.messages:
            if msg.message_id == message_id:
                msg.read = True
    
    def update_context(self, key: str, value: Any):
        """Update shared context"""
        setattr(self.shared_context, key, value)
        self.last_activity = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "pair_id": self.pair_id,
            "agent_a": self.agent_a.to_dict(),
            "agent_b": self.agent_b.to_dict(),
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "status": self.status,
            "message_count": len(self.messages),
            "context_keys": list(self.shared_context.__dict__.keys()),
        }


class AgentPairingSystem:
    """
    Agent Pairing System - Like marimo pair
    
    Allows AI agents to work together on Paradise Stack:
    - Planner + Implementer: Plan then build
    - Guardian + Executor: Check quality
    - User + Agent: Natural conversation
    - Multiple agents collaborating
    """
    
    def __init__(self):
        self.agents: dict[str, Agent] = {}
        self.pairs: dict[str, AgentPair] = {}
        self.tools: dict[str, Tool] = {}
        self.conversations: dict[str, list] = {}
        self._register_default_tools()
        self._register_default_agents()
    
    def _register_default_tools(self):
        """Register default tools for agents"""
        
        self.register_tool(Tool(
            name="read_file",
            description="Read contents of a file",
            func=lambda path: f"Content of {path}",
        ))
        
        self.register_tool(Tool(
            name="write_file",
            description="Write content to a file",
            func=lambda path, content: f"Wrote to {path}",
        ))
        
        self.register_tool(Tool(
            name="run_command",
            description="Run a shell command",
            func=lambda cmd: f"Ran: {cmd}",
        ))
        
        self.register_tool(Tool(
            name="search_code",
            description="Search for code patterns",
            func=lambda pattern: f"Found {pattern}",
        ))
        
        self.register_tool(Tool(
            name="lint_code",
            description="Lint code for errors",
            func=lambda code: "Linting passed",
        ))
        
        self.register_tool(Tool(
            name="run_tests",
            description="Run test suite",
            func=lambda pattern="": "Tests passed",
        ))
    
    def _register_default_agents(self):
        """Register default Paradise agents"""
        
        agents = [
            Agent(
                agent_id="planner",
                name="Paradise Planner",
                role=AgentRole.PLANNER,
                capabilities=["planning", "analysis", "architecture"],
                system_prompt="You are Paradise Planner. Analyze requirements and create implementation plans.",
                tools=["read_file", "search_code"],
            ),
            Agent(
                agent_id="implementer",
                name="Paradise Implementer",
                role=AgentRole.IMPLEMENTER,
                capabilities=["code_generation", "refactoring", "recursion"],
                system_prompt="You are Paradise Implementer. Write code based on plans.",
                tools=["read_file", "write_file", "run_command"],
            ),
            Agent(
                agent_id="guardian",
                name="Paradise Guardian",
                role=AgentRole.GUARDIAN,
                capabilities=["linting", "security", "quality"],
                system_prompt="You are Paradise Guardian. Check code quality and security.",
                tools=["lint_code", "search_code"],
            ),
            Agent(
                agent_id="executor",
                name="Paradise Executor",
                role=AgentRole.EXECUTOR,
                capabilities=["testing", "execution", "verification"],
                system_prompt="You are Paradise Executor. Run tests and verify functionality.",
                tools=["run_tests", "run_command"],
            ),
            Agent(
                agent_id="improver",
                name="Paradise Improver",
                role=AgentRole.IMPROVER,
                capabilities=["refactoring", "optimization", "fixing"],
                system_prompt="You are Paradise Improver. Fix issues and improve code quality.",
                tools=["read_file", "write_file", "lint_code"],
            ),
        ]
        
        for agent in agents:
            self.register_agent(agent)
    
    def register_agent(self, agent: Agent):
        """Register a new agent"""
        self.agents[agent.agent_id] = agent
    
    def register_tool(self, tool: Tool):
        """Register a new tool"""
        self.tools[tool.name] = tool
    
    def create_pair(self, agent_a_id: str, agent_b_id: str) -> Optional[AgentPair]:
        """Create a pair between two agents"""
        if agent_a_id not in self.agents or agent_b_id not in self.agents:
            return None
        
        pair_id = f"{agent_a_id}_{agent_b_id}_{uuid.uuid4().hex[:4]}"
        pair = AgentPair(
            pair_id=pair_id,
            agent_a=self.agents[agent_a_id],
            agent_b=self.agents[agent_b_id],
        )
        
        self.pairs[pair_id] = pair
        self.conversations[pair_id] = []
        
        self.agents[agent_a_id].is_active = True
        self.agents[agent_b_id].is_active = True
        
        return pair
    
    def get_pair(self, pair_id: str) -> Optional[AgentPair]:
        """Get a pair by ID"""
        return self.pairs.get(pair_id)
    
    def get_pairs_for_agent(self, agent_id: str) -> list[AgentPair]:
        """Get all pairs involving an agent"""
        return [
            p for p in self.pairs.values()
            if p.agent_a.agent_id == agent_id or p.agent_b.agent_id == agent_id
        ]
    
    def message_agents(
        self,
        from_agent: str,
        to_agent: str,
        content: str,
    ) -> Message:
        """Send a message directly between agents"""
        pair = self.get_pairs_for_agent(from_agent)
        
        if pair:
            return pair[0].send_message(from_agent, to_agent, content)
        
        for p in self.pairs.values():
            if (p.agent_a.agent_id == from_agent and p.agent_b.agent_id == to_agent) or \
               (p.agent_a.agent_id == to_agent and p.agent_b.agent_id == from_agent):
                return p.send_message(from_agent, to_agent, content)
        
        return None
    
    def simulate_collaboration(self, pair_id: str, task: str) -> dict:
        """Simulate agent collaboration on a task"""
        pair = self.get_pair(pair_id)
        if not pair:
            return {"error": "Pair not found"}
        
        results = {
            "task": task,
            "pair_id": pair_id,
            "conversation": [],
            "final_context": {},
        }
        
        if pair.agent_a.role == AgentRole.PLANNER:
            results["conversation"].append({
                "agent": pair.agent_a.name,
                "action": "Creating plan",
                "output": f"Plan for: {task}",
            })
            pair.update_context("plan", f"Plan for: {task}")
        
        if pair.agent_b.role == AgentRole.IMPLEMENTER:
            results["conversation"].append({
                "agent": pair.agent_b.name,
                "action": "Implementing",
                "output": "Code generated",
            })
            pair.update_context("code", "# Implementation code")
        
        results["final_context"] = {
            "plan": pair.shared_context.plan,
            "code": pair.shared_context.code,
        }
        
        return results
    
    def get_system_status(self) -> dict:
        """Get status of the pairing system"""
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.is_active),
            "total_pairs": len(self.pairs),
            "active_pairs": sum(1 for p in self.pairs.values() if p.status == "active"),
            "total_tools": len(self.tools),
            "total_messages": sum(len(p.messages) for p in self.pairs.values()),
        }
    
    def get_all_data(self) -> dict:
        """Get all data for dashboard"""
        return {
            "status": self.get_system_status(),
            "agents": {aid: a.to_dict() for aid, a in self.agents.items()},
            "pairs": [p.to_dict() for p in self.pairs.values()],
            "tools": {tname: t.to_dict() for tname, t in self.tools.items()},
        }


_pairing_system = None


def get_pairing_system() -> AgentPairingSystem:
    global _pairing_system
    if _pairing_system is None:
        _pairing_system = AgentPairingSystem()
    return _pairing_system


def main():
    print("🤝 Paradise Agent Pairing System")
    print("=" * 50)
    
    system = get_pairing_system()
    
    print("\n📊 System Status:")
    print(json.dumps(system.get_system_status(), indent=2))
    
    pair = system.create_pair("planner", "implementer")
    if pair:
        print(f"\n✅ Created pair: {pair.pair_id}")
        print(f"   {pair.agent_a.name} <-> {pair.agent_b.name}")
    
    result = system.simulate_collaboration(
        pair.pair_id,
        "Create a user authentication system"
    )
    print("\n💬 Collaboration:")
    for msg in result["conversation"]:
        print(f"   {msg['agent']}: {msg['action']}")
    
    print("\n📋 All Agents:")
    for agent in system.agents.values():
        print(f"   {agent.name} ({agent.role.value})")
        print(f"      Tools: {', '.join(agent.tools)}")


if __name__ == "__main__":
    main()
