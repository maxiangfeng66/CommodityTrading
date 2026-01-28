"""
Visualizer Bridge - State management for real-time visualization

Singleton class that manages the visualizer state and provides methods
for agents to update their status. State is persisted to JSON for
HTTP polling by the frontend.
"""

import json
import os
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class VisualizerBridge:
    """
    Bridge between agents and the visualizer frontend.

    Maintains state in a JSON file that the frontend polls.
    Thread-safe singleton pattern.
    """

    _instance: Optional['VisualizerBridge'] = None
    _lock = threading.Lock()

    def __new__(cls, context_dir: str = "context"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, context_dir: str = "context"):
        if self._initialized:
            return

        self.context_dir = Path(context_dir)
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.context_dir / "visualizer_state.json"
        self._write_lock = threading.Lock()
        self._server_started = False

        # Initialize state
        self._state = self._get_initial_state()
        self._save_state()
        self._initialized = True

    @classmethod
    def get_instance(cls, context_dir: str = "context") -> 'VisualizerBridge':
        """Get singleton instance."""
        return cls(context_dir)

    def _get_initial_state(self) -> Dict[str, Any]:
        """Get initial empty state."""
        return {
            "status": "idle",  # idle, running, complete, error
            "commodity": "",
            "commodity_name": "",
            "start_time": None,
            "last_updated": datetime.now().isoformat(),
            "agents": {},
            "connections": [],
            "chat_log": [],
            "progress": 0,
            "modules_done": 0,
            "total_modules": 6,
            "debate_rounds": 0,
            "total_chars": 0,
            "current_phase": "",
            "error_message": ""
        }

    def _save_state(self):
        """Save state to JSON file (thread-safe)."""
        with self._write_lock:
            self._state["last_updated"] = datetime.now().isoformat()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self._state, f, indent=2, ensure_ascii=False)

    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to max length."""
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    # ==================== Workflow Lifecycle ====================

    def start_analysis(self, commodity: str, commodity_name: str = ""):
        """Start a new commodity analysis."""
        self._state = self._get_initial_state()
        self._state["status"] = "running"
        self._state["commodity"] = commodity
        self._state["commodity_name"] = commodity_name or commodity
        self._state["start_time"] = datetime.now().isoformat()
        self._state["current_phase"] = "Initializing"

        self._add_chat_log("System", f"Starting analysis for {commodity_name or commodity}")
        self._save_state()

        # Auto-open browser if server is running
        if self._server_started:
            self._open_browser()

    def complete_analysis(self, commodity: str = ""):
        """Mark analysis as complete."""
        self._state["status"] = "complete"
        self._state["progress"] = 100
        self._state["current_phase"] = "Complete"

        self._add_chat_log("System", f"Analysis complete for {commodity or self._state['commodity']}")
        self._save_state()

    def error_analysis(self, commodity: str, error_msg: str):
        """Mark analysis as failed."""
        self._state["status"] = "error"
        self._state["error_message"] = error_msg
        self._state["current_phase"] = "Error"

        self._add_chat_log("System", f"Error: {self._truncate(error_msg, 200)}", level="error")
        self._save_state()

    def update_phase(self, phase: str, progress: int = None):
        """Update current phase and optionally progress."""
        self._state["current_phase"] = phase
        if progress is not None:
            self._state["progress"] = min(100, max(0, progress))
        self._save_state()

    def update_progress(self, progress: int, message: str = ""):
        """Update progress percentage."""
        self._state["progress"] = min(100, max(0, progress))
        if message:
            self._add_chat_log("System", message)
        self._save_state()

    # ==================== Agent Management ====================

    def agent_start(self, agent_id: str, task: str = "", tier: int = 2, provider: str = ""):
        """Mark agent as started/thinking."""
        self._state["agents"][agent_id] = {
            "status": "thinking",
            "task": self._truncate(task, 500),
            "tier": tier,
            "provider": provider,
            "message": "Starting...",
            "output": "",
            "output_length": 0,
            "start_time": datetime.now().isoformat(),
            "progress": 0
        }

        self._add_chat_log(agent_id, f"Starting: {self._truncate(task, 100)}")
        self._save_state()

    def agent_progress(self, agent_id: str, message: str, chars_count: int = 0):
        """Update agent progress."""
        if agent_id in self._state["agents"]:
            self._state["agents"][agent_id]["message"] = self._truncate(message, 200)
            if chars_count > 0:
                self._state["agents"][agent_id]["output_length"] = chars_count
                self._state["total_chars"] += chars_count
            self._save_state()

    def agent_output(self, agent_id: str, output: str):
        """Update agent output preview."""
        if agent_id in self._state["agents"]:
            self._state["agents"][agent_id]["output"] = self._truncate(output, 5000)
            self._state["agents"][agent_id]["output_length"] = len(output)
            self._save_state()

    def agent_stream(self, agent_id: str, partial_output: str, is_final: bool = False):
        """Stream partial output from agent."""
        if agent_id in self._state["agents"]:
            # Keep last 2000 chars for preview
            if len(partial_output) > 2000:
                preview = "..." + partial_output[-2000:]
            else:
                preview = partial_output

            self._state["agents"][agent_id]["output"] = preview
            self._state["agents"][agent_id]["output_length"] = len(partial_output)

            if is_final:
                self._state["agents"][agent_id]["status"] = "complete"

            self._save_state()

    def agent_complete(self, agent_id: str, output_length: int = 0, output: str = ""):
        """Mark agent as complete."""
        if agent_id in self._state["agents"]:
            self._state["agents"][agent_id]["status"] = "complete"
            self._state["agents"][agent_id]["message"] = "Complete"
            if output_length > 0:
                self._state["agents"][agent_id]["output_length"] = output_length
            if output:
                self._state["agents"][agent_id]["output"] = self._truncate(output, 5000)

            self._add_chat_log(agent_id, "Complete")
            self._save_state()

    def agent_error(self, agent_id: str, error: str):
        """Mark agent as errored."""
        if agent_id not in self._state["agents"]:
            self._state["agents"][agent_id] = {
                "status": "error",
                "task": "",
                "tier": 2,
                "provider": "",
                "message": "",
                "output": "",
                "output_length": 0,
                "start_time": datetime.now().isoformat(),
                "progress": 0
            }

        self._state["agents"][agent_id]["status"] = "error"
        self._state["agents"][agent_id]["message"] = self._truncate(error, 200)

        self._add_chat_log(agent_id, f"Error: {self._truncate(error, 100)}", level="error")
        self._save_state()

    def agent_idle(self, agent_id: str):
        """Mark agent as idle."""
        if agent_id in self._state["agents"]:
            self._state["agents"][agent_id]["status"] = "idle"
            self._state["agents"][agent_id]["message"] = "Idle"
            self._save_state()

    # ==================== Dynamic Agent Spawning ====================

    def spawn_agent(self, agent_id: str, parent_id: str = "", role: str = "",
                    tier: int = 3, task: str = "", provider: str = ""):
        """
        Spawn a new dynamically created agent.

        This agent will appear in the "Spawned Agents" section of the visualizer.
        Unlike predefined agents (PM, SUP, TMs), spawned agents are created at runtime
        and removed when terminated.

        Args:
            agent_id: Unique identifier for the spawned agent
            parent_id: ID of the parent agent that spawned this one
            role: Role description (e.g., "Research", "Validator")
            tier: Agent tier (default 3 for sub-agents)
            task: Initial task description
            provider: AI provider being used
        """
        self._state["agents"][agent_id] = {
            "status": "thinking",
            "task": self._truncate(task, 500),
            "tier": tier,
            "provider": provider,
            "message": "Spawning...",
            "output": "",
            "output_length": 0,
            "start_time": datetime.now().isoformat(),
            "progress": 0,
            "parent": parent_id,
            "role": role,
            "spawned": True  # Flag to identify dynamically spawned agents
        }

        parent_info = f" (by {parent_id})" if parent_id else ""
        self._add_chat_log(agent_id, f"Spawned{parent_info}: {self._truncate(task or role, 100)}")
        self._save_state()

    def terminate_agent(self, agent_id: str, reason: str = ""):
        """
        Terminate a dynamically spawned agent.

        Removes the agent from the state, which will cause the frontend
        to remove its visual representation.

        Args:
            agent_id: ID of the agent to terminate
            reason: Optional reason for termination
        """
        if agent_id in self._state["agents"]:
            agent_data = self._state["agents"][agent_id]

            # Only remove if it was a spawned agent
            if agent_data.get("spawned", False):
                reason_msg = f": {reason}" if reason else ""
                self._add_chat_log(agent_id, f"Terminated{reason_msg}")
                del self._state["agents"][agent_id]
            else:
                # For predefined agents, just mark as idle
                self._state["agents"][agent_id]["status"] = "idle"
                self._state["agents"][agent_id]["message"] = "Terminated"

            self._save_state()

    def get_spawned_agents(self) -> Dict[str, Any]:
        """Get all currently spawned agents."""
        return {
            agent_id: agent_data
            for agent_id, agent_data in self._state["agents"].items()
            if agent_data.get("spawned", False)
        }

    def get_agent_children(self, parent_id: str) -> Dict[str, Any]:
        """Get all agents spawned by a specific parent."""
        return {
            agent_id: agent_data
            for agent_id, agent_data in self._state["agents"].items()
            if agent_data.get("parent") == parent_id
        }

    # ==================== Module Tracking ====================

    def module_start(self, module_name: str, task: str = ""):
        """Start a module (TM-FUND, TM-NEWS, etc.)."""
        self.agent_start(module_name, task, tier=2)

    def module_complete(self, module_name: str, score: float = None):
        """Complete a module."""
        self.agent_complete(module_name)
        self._state["modules_done"] = min(
            self._state["modules_done"] + 1,
            self._state["total_modules"]
        )

        # Update progress based on modules done
        module_progress = (self._state["modules_done"] / self._state["total_modules"]) * 70
        self._state["progress"] = int(10 + module_progress)  # 10% for init, 70% for modules

        if score is not None:
            self._add_chat_log(module_name, f"Score: {score:+.1f}")

        self._save_state()

    def module_error(self, module_name: str, error: str):
        """Mark module as errored."""
        self.agent_error(module_name, error)

    # ==================== Debate Tracking ====================

    def debate_start(self, module_name: str, round_num: int):
        """Start a debate round."""
        self._state["debate_rounds"] = round_num
        self.agent_progress(module_name, f"Debate round {round_num}")
        self._add_chat_log(module_name, f"Debate round {round_num} started")
        self._save_state()

    def debate_challenge(self, module_name: str, challenger: str, challenge: str):
        """Log a debate challenge."""
        self._add_chat_log(f"{module_name}/{challenger}", self._truncate(challenge, 150))
        self._save_state()

    def debate_response(self, module_name: str, response: str):
        """Log a debate response."""
        self._add_chat_log(module_name, self._truncate(response, 150))
        self._save_state()

    def debate_complete(self, module_name: str, outcome: str, rounds: int):
        """Complete debate for a module."""
        self._state["debate_rounds"] = max(self._state["debate_rounds"], rounds)
        self._add_chat_log(module_name, f"Debate complete: {outcome} ({rounds} rounds)")
        self._save_state()

    # ==================== Connection Management ====================

    def activate_connection(self, from_agent: str, to_agent: str):
        """Activate a connection between agents."""
        conn = {"from": from_agent, "to": to_agent, "status": "active"}

        # Remove existing connection if present
        self._state["connections"] = [
            c for c in self._state["connections"]
            if not (c["from"] == from_agent and c["to"] == to_agent)
        ]
        self._state["connections"].append(conn)
        self._save_state()

    def complete_connection(self, from_agent: str, to_agent: str):
        """Mark a connection as complete."""
        for conn in self._state["connections"]:
            if conn["from"] == from_agent and conn["to"] == to_agent:
                conn["status"] = "complete"
                break
        self._save_state()

    # ==================== Chat Log ====================

    def _add_chat_log(self, agent: str, message: str, level: str = "info"):
        """Add entry to chat log."""
        entry = {
            "agent": agent,
            "message": message,
            "level": level,
            "time": datetime.now().strftime("%H:%M:%S")
        }
        self._state["chat_log"].append(entry)

        # Keep only last 100 entries
        if len(self._state["chat_log"]) > 100:
            self._state["chat_log"] = self._state["chat_log"][-100:]

    def add_log(self, agent: str, message: str):
        """Public method to add log entry."""
        self._add_chat_log(agent, message)
        self._save_state()

    # ==================== Server Management ====================

    def start_server(self, port: int = 8765, open_browser: bool = True):
        """Start the HTTP server in background thread."""
        if self._server_started:
            return

        import threading
        from visualizer.serve_visualizer import start_server_thread

        self._server_started = True
        start_server_thread(port)

        if open_browser:
            self._open_browser(port)

    def _open_browser(self, port: int = 8765):
        """Open browser to visualizer."""
        url = f"http://localhost:{port}"
        try:
            webbrowser.open(url)
        except Exception:
            pass

    # ==================== State Access ====================

    def get_state(self) -> Dict[str, Any]:
        """Get current state (read-only copy)."""
        return self._state.copy()

    def reset(self):
        """Reset to initial state."""
        self._state = self._get_initial_state()
        self._save_state()


# Global instance getter
def get_visualizer(context_dir: str = "context") -> VisualizerBridge:
    """Get the global visualizer instance."""
    return VisualizerBridge.get_instance(context_dir)
