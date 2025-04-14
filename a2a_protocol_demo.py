#!/usr/bin/env python3
"""
A2A Protocol Demo Script

This script demonstrates the Google A2A protocol implementation with the following features:
1. Setting up an A2A server with agent registration
2. Fetching and displaying the agent card
3. Sending tasks to agents and receiving responses
4. Demonstrating streaming responses
5. Showing task state transitions

Usage:
    python a2a_protocol_demo.py
"""

import os
import sys
import json
import uuid
import asyncio
import requests
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Add the current directory to the path to make imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.model_agents import GPT45Agent, GPTO3MiniAgent
from schemas.base import MessageRole, TextPart
from server import register_agent, start_server


class A2AClient:
    """Client for interacting with an A2A protocol server."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.task_ids = []

    def get_agent_card(self) -> Dict[str, Any]:
        """Fetch the agent card from the server."""
        response = requests.get(f"{self.base_url}/.well-known/agent.json")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching agent card: {response.status_code}")
            print(response.text)
            return {}

    def send_task(self, message_text: str) -> Dict[str, Any]:
        """Send a task to the server."""
        task_id = str(uuid.uuid4())
        self.task_ids.append(task_id)
        
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/send",
            "params": {
                "id": task_id,
                "sessionId": str(uuid.uuid4()),
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "type": "text",
                            "text": message_text
                        }
                    ]
                }
            }
        }
        
        response = requests.post(self.base_url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error sending task: {response.status_code}")
            print(response.text)
            return {}

    def send_task_with_streaming(self, message_text: str) -> None:
        """Send a task with streaming enabled."""
        task_id = str(uuid.uuid4())
        self.task_ids.append(task_id)
        
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/sendSubscribe",
            "params": {
                "id": task_id,
                "sessionId": str(uuid.uuid4()),
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "type": "text",
                            "text": message_text
                        }
                    ]
                }
            }
        }
        
        # Stream processing
        print("\n📨 Sending task with streaming...\n")
        response = requests.post(f"{self.base_url}/stream", json=payload, stream=True)
        
        for line in response.iter_lines():
            if line:
                # Parse SSE format (data: {...})
                if line.startswith(b'data: '):
                    try:
                        data = json.loads(line[6:])
                        
                        if data.get("result"):
                            result = data["result"]
                            if "status" in result:
                                state = result["status"].get("state", "unknown")
                                print(f"📝 Task state updated: {state}")
                                
                                message = result["status"].get("message")
                                if message and "parts" in message:
                                    for part in message["parts"]:
                                        if part.get("type") == "text":
                                            print(f"\n🤖 Agent response:\n{part.get('text')}\n")
                                
                                if result.get("final", False):
                                    print("✅ Task completed.")
                        
                        elif data.get("error"):
                            print(f"❌ Error: {data['error'].get('message', 'Unknown error')}")
                    
                    except json.JSONDecodeError:
                        print(f"Error parsing response: {line[6:]}")
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get a task from the server."""
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
    
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """Cancel a task."""
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/cancel",
            "params": {
                "id": task_id
            }
        }
        
        response = requests.post(self.base_url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error canceling task: {response.status_code}")
            print(response.text)
            return {}


def format_json(obj: Dict[str, Any]) -> str:
    """Format a JSON object for pretty printing."""
    return json.dumps(obj, indent=2)


def print_section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def run_server_thread():
    """Run the A2A server in a separate thread."""
    # Register the agents with updated names for Azure OpenAI
    agent1 = GPT45Agent(name="GPT-4 Turbo Assistant")
    agent2 = GPTO3MiniAgent(name="GPT-3.5 Turbo Helper")
    
    register_agent(agent1)
    register_agent(agent2)
    
    # Start the server
    start_server(port=8000)


def main():
    """Main function to demonstrate the A2A protocol."""
    # Start the server in a separate thread
    server_thread = threading.Thread(target=run_server_thread, daemon=True)
    server_thread.start()
    
    # Wait for the server to start
    time.sleep(2)
    
    # Create a client
    client = A2AClient()
    
    print_section_header("📋 A2A Protocol Demo")
    print("This script demonstrates the capabilities of the Google A2A protocol implementation.")
    
    # Demo 1: Get agent card
    print_section_header("1. Agent Card Demo")
    print("Fetching the agent card from the server...")
    agent_card = client.get_agent_card()
    print(f"\nAgent Card for {agent_card.get('name', 'Unknown Agent')}:")
    print(f"Description: {agent_card.get('description', 'No description')}")
    print(f"Version: {agent_card.get('version', 'Unknown')}")
    print("\nCapabilities:")
    capabilities = agent_card.get("capabilities", {})
    for key, value in capabilities.items():
        print(f"  - {key}: {value}")
    
    print("\nSkills:")
    for skill in agent_card.get("skills", []):
        print(f"  - {skill.get('name', 'Unknown Skill')}: {skill.get('description', 'No description')}")
    
    # Demo 2: Send a simple task
    print_section_header("2. Simple Task Demo")
    print("Sending a simple task to the agent...")
    response = client.send_task("What is the A2A protocol?")
    
    result = response.get("result", {})
    if result:
        print(f"\nTask ID: {result.get('id', 'Unknown')}")
        print(f"Task State: {result.get('status', {}).get('state', 'Unknown')}")
        
        # Print the response message if available
        message = result.get("status", {}).get("message", {})
        if message:
            for part in message.get("parts", []):
                if part.get("type") == "text":
                    print(f"\nResponse:\n{part.get('text', '')}")
    
    # Demo 3: Streaming response
    print_section_header("3. Streaming Response Demo")
    client.send_task_with_streaming("Please explain how message exchange works in the A2A protocol.")
    
    # Demo 4: Task state transitions
    print_section_header("4. Task State Transitions Demo")
    print("Sending a task and then checking its state...")
    response = client.send_task("What are the key components of the A2A protocol?")
    
    result = response.get("result", {})
    if result:
        task_id = result.get("id", "")
        if task_id:
            print(f"Task ID: {task_id}")
            print(f"Initial State: {result.get('status', {}).get('state', 'Unknown')}")
            
            print("\nFetching the task to check its current state...")
            task_response = client.get_task(task_id)
            task_result = task_response.get("result", {})
            if task_result:
                print(f"Current State: {task_result.get("status", {}).get("state", "Unknown")}")
                
                # Check for artifacts
                artifacts = task_result.get("artifacts", [])
                if artifacts:
                    print(f"\nTask produced {len(artifacts)} artifact(s):")
                    for i, artifact in enumerate(artifacts):
                        print(f"  Artifact {i+1}: {artifact.get('name', 'Unnamed')}")
                        for part in artifact.get("parts", []):
                            if part.get("type") == "text":
                                print(f"  Content: {part.get('text', '')[:150]}...")
    
    # Demo 5: Task cancellation
    print_section_header("5. Task Cancellation Demo")
    print("Sending a task and then canceling it...")
    response = client.send_task("This is a task that will be canceled.")
    
    result = response.get("result", {})
    if result:
        task_id = result.get("id", "")
        if task_id:
            print(f"Task ID: {task_id}")
            print(f"State before cancellation: {result.get('status', {}).get('state', 'Unknown')}")
            
            print("\nCanceling the task...")
            cancel_response = client.cancel_task(task_id)
            cancel_result = cancel_response.get("result", {})
            if cancel_result:
                print(f"State after cancellation: {cancel_result.get('status', {}).get('state', 'Unknown')}")
    
    print_section_header("✅ Demo Complete")
    print("The A2A protocol demonstration has completed successfully.")
    print("Press Ctrl+C to exit the script.")
    
    # Keep the script running to maintain the server
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting the A2A protocol demo.")


if __name__ == "__main__":
    main()