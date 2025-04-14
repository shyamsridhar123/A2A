#!/usr/bin/env python3
"""
A2A Collaborative Agents Demo

This script demonstrates two agents collaborating using the A2A protocol to solve a problem.
The demo shows how agents can:
1. Exchange messages in a structured way
2. Process tasks in a collaborative workflow
3. Pass context between agents to build on each other's work

Usage:
    python a2a_collaborative_demo.py
"""

import os
import sys
import json
import uuid
import threading
import time
import requests
from typing import Dict, List, Any, Optional

# Add the current directory to the path to make imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.model_agents import GPT45Agent, GPTO3MiniAgent
from schemas.base import MessageRole, TextPart, DataPart, Task, TaskState
from server import register_agent, start_server


class CollaborativeWorkflow:
    """Manages a collaborative workflow between multiple agents."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.sessions = {}
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new collaborative session."""
        session_id = session_id or str(uuid.uuid4())
        self.sessions[session_id] = {
            "tasks": [],
            "artifacts": []
        }
        return session_id
    
    def submit_user_task(self, session_id: str, prompt: str) -> Dict[str, Any]:
        """Submit an initial task from a user to start the workflow."""
        # Create a unique task ID
        task_id = str(uuid.uuid4())
        
        # Create the JSON-RPC payload
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/send",
            "params": {
                "id": task_id,
                "sessionId": session_id,
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            }
        }
        
        # Send the request to the first agent
        response = requests.post(self.base_url, json=payload)
        if response.status_code == 200:
            result = response.json()
            # Store the task in the session
            if "result" in result:
                self.sessions[session_id]["tasks"].append(result["result"])
            return result
        else:
            print(f"Error submitting task: {response.status_code}")
            print(response.text)
            return {}
    
    def forward_to_second_agent(self, session_id: str, first_agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Forward the result from the first agent to the second agent."""
        if "result" not in first_agent_result:
            print("No result to forward")
            return {}
        
        # Extract the first agent's response
        first_task = first_agent_result["result"]
        message = first_task["status"]["message"]
        
        # Get text from the first agent's response
        text_content = ""
        for part in message.get("parts", []):
            if part.get("type") == "text":
                text_content += part.get("text", "") + "\n"
        
        # Create a new task for the second agent
        task_id = str(uuid.uuid4())
        
        # Create a message that includes the context from the first agent
        prompt = f"""
I need you to enhance and build upon the analysis provided by another agent.
Here is their response:

{text_content}

Please provide additional insights, corrections if needed, and expand on any important points.
"""
        
        # Create the JSON-RPC payload
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/send",
            "params": {
                "id": task_id,
                "sessionId": session_id,
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            }
        }
        
        # Send the request
        response = requests.post(self.base_url, json=payload)
        if response.status_code == 200:
            result = response.json()
            # Store the task in the session
            if "result" in result:
                self.sessions[session_id]["tasks"].append(result["result"])
            return result
        else:
            print(f"Error forwarding task: {response.status_code}")
            print(response.text)
            return {}
    
    def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """Get the result of a task."""
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/get",
            "params": {
                "id": task_id
            }
        }
        
        response = requests.post(self.base_url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting task: {response.status_code}")
            print(response.text)
            return {}


def print_section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_agent_response(agent_name: str, response: Dict[str, Any]) -> None:
    """Print an agent's response in a formatted way."""
    print(f"\n📝 {agent_name}'s Response:")
    print("-" * 40)
    
    if "result" not in response:
        print("No result available")
        return
    
    result = response["result"]
    if "status" not in result:
        print("No status available")
        return
    
    status = result["status"]
    if "message" not in status:
        print("No message available")
        return
    
    message = status["message"]
    if "parts" not in message:
        print("No message parts available")
        return
    
    for part in message["parts"]:
        if part.get("type") == "text":
            print(part.get("text", ""))
    
    print("-" * 40)


def run_server_thread():
    """Run the A2A server in a separate thread."""
    # Create and register two different agents
    research_agent = GPT45Agent(name="Research Assistant")
    enhancement_agent = GPTO3MiniAgent(name="Enhancement Specialist")
    
    register_agent(research_agent)
    register_agent(enhancement_agent)
    
    # Start the server
    start_server(port=8000)


def main():
    """Main function to demonstrate collaborative agents with A2A protocol."""
    # Start the server in a separate thread
    server_thread = threading.Thread(target=run_server_thread, daemon=True)
    server_thread.start()
    
    # Wait for the server to start
    time.sleep(2)
    
    print_section_header("🤝 A2A Collaborative Agents Demo")
    print("""
This demo shows how two agents can collaborate using the A2A protocol.
- Research Assistant: Provides initial analysis and information
- Enhancement Specialist: Enhances and expands on the first agent's work
    """)
    
    # Create a workflow manager
    workflow = CollaborativeWorkflow()
    
    # Create a new session
    session_id = workflow.create_session()
    print(f"Created new collaboration session: {session_id}\n")
    
    # Demo tasks with increasing complexity
    tasks = [
        {
            "name": "Basic Knowledge Query",
            "prompt": "What are the main principles of the Agent-to-Agent protocol?",
        },
        {
            "name": "Problem Analysis",
            "prompt": "Analyze the challenges in implementing secure agent-to-agent communication.",
        },
        {
            "name": "Creative Task",
            "prompt": "Suggest three innovative applications of the A2A protocol in healthcare.",
        }
    ]
    
    # Process each task with both agents collaboratively
    for i, task in enumerate(tasks):
        print_section_header(f"Task {i+1}: {task['name']}")
        print(f"User Query: {task['prompt']}")
        
        # Step 1: Submit the task to the first agent (Research Assistant)
        print("\n🔍 Submitting task to Research Assistant...")
        first_response = workflow.submit_user_task(session_id, task["prompt"])
        print_agent_response("Research Assistant", first_response)
        
        # Step 2: Forward to the second agent (Enhancement Specialist)
        print("\n🔄 Forwarding to Enhancement Specialist...")
        second_response = workflow.forward_to_second_agent(session_id, first_response)
        print_agent_response("Enhancement Specialist", second_response)
        
        # Pause between tasks
        if i < len(tasks) - 1:
            print("\nMoving to next task in 3 seconds...")
            time.sleep(3)
    
    print_section_header("✅ Collaborative Workflow Complete")
    print("""
The collaborative workflow has been completed successfully.
This demonstrates how multiple agents can collaborate in a workflow using the A2A protocol,
building on each other's outputs to provide enhanced results.
    """)
    print("\nPress Ctrl+C to exit the script.")
    
    # Keep the script running to maintain the server
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting the collaborative agents demo.")


if __name__ == "__main__":
    main()