import time
import sys
import os
import uuid
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our A2A components
from agents.model_agents import GPT45Agent, GPTO3MiniAgent
from utils.conversation import ConversationManager
from schemas.base import ContentType, Content, Message


class CollaborativeTask:
    """Represents a task that requires collaboration between agents."""
    
    def __init__(self, task_id: str, description: str, subtasks: List[Dict[str, Any]]):
        self.id = task_id
        self.description = description
        self.subtasks = subtasks
        self.results = {}
        self.status = "pending"  # pending, in_progress, completed, failed


class MultiAgentCollaborationDemo:
    """Demo for multi-agent collaboration using A2A protocol."""
    
    def __init__(self):
        """Initialize the demo with agents and task definitions."""
        # Create agents with specific roles
        self.research_agent = GPT45Agent(name="Research Specialist")
        self.summarization_agent = GPTO3MiniAgent(name="Summarization Expert")
        
        # Create conversation manager
        self.conversation_manager = ConversationManager()
        
        # Define a collaborative task
        self.task = CollaborativeTask(
            task_id=str(uuid.uuid4()),
            description="Analyze and summarize information about the Google Agent-to-Agent Protocol",
            subtasks=[
                {
                    "id": "research",
                    "description": "Research key aspects of the Google A2A Protocol",
                    "assigned_to": self.research_agent.id,
                    "status": "pending",
                    "dependencies": []
                },
                {
                    "id": "summarize",
                    "description": "Create a concise summary of the findings",
                    "assigned_to": self.summarization_agent.id,
                    "status": "pending",
                    "dependencies": ["research"]
                }
            ]
        )
    
    def run(self):
        """Run the multi-agent collaboration demo."""
        print("=" * 80)
        print("Multi-Agent Collaboration Demo")
        print("Using the Google Agent-to-Agent Protocol")
        print("=" * 80)
        
        print(f"\nTask: {self.task.description}")
        print(f"Subtasks:")
        for subtask in self.task.subtasks:
            agent_name = self.research_agent.name if subtask["assigned_to"] == self.research_agent.id else self.summarization_agent.name
            print(f"  - {subtask['id']}: {subtask['description']} (Assigned to: {agent_name})")
        
        # Create a conversation for the collaboration
        conversation = self.conversation_manager.create_conversation(
            participant_ids=[self.research_agent.id, self.summarization_agent.id],
            metadata={"task_id": self.task.id, "type": "collaboration"}
        )
        
        print(f"\nStarting collaboration (Conversation ID: {conversation.id})")
        print("-" * 80)
        
        # Step 1: Start with research subtask
        research_subtask = next(st for st in self.task.subtasks if st["id"] == "research")
        research_subtask["status"] = "in_progress"
        
        # Create initial task message for research agent
        task_prompt = f"""
        I need you to research the Google Agent-to-Agent (A2A) Protocol and provide key information about:
        
        1. What is the A2A Protocol and its purpose?
        2. Key components and message formats of the protocol
        3. How it enables multi-agent collaboration
        4. Any specific features that make it unique
        
        Please provide comprehensive information that can be used for creating a summary later.
        """
        
        task_message = Message(
            id=str(uuid.uuid4()),
            sender_id="system",
            recipient_id=self.research_agent.id,
            content=[
                Content(type=ContentType.TEXT, value=task_prompt)
            ]
        )
        
        # Add the message to the conversation
        self.conversation_manager.add_message_to_conversation(conversation.id, task_message)
        
        print("Task assigned to Research Specialist:")
        # Format multiline responses properly
        formatted_task = '\n'.join([line.strip() for line in task_prompt.strip().split('\n')])
        print(formatted_task)
        print("-" * 80)
        
        # Have research agent process the task
        self.research_agent.receive_message(task_message)
        research_response = self.research_agent.generate_response(task_message)
        
        # Add response to conversation
        self.conversation_manager.add_message_to_conversation(conversation.id, research_response)
        
        print(f"\nResearch Specialist's findings:")
        # Format multiline responses properly
        research_text = research_response.content[0].value.strip()
        formatted_research = '\n'.join([line.strip() for line in research_text.split('\n')])
        print(formatted_research)
        print("-" * 80)
        
        # Update research subtask status
        research_subtask["status"] = "completed"
        self.task.results["research"] = research_response.content[0].value
        
        # Step 2: Now move to summarization subtask
        summarize_subtask = next(st for st in self.task.subtasks if st["id"] == "summarize")
        summarize_subtask["status"] = "in_progress"
        
        # Create task message for summarization agent
        summarize_prompt = f"""
        Please create a concise summary of the following research about the Google Agent-to-Agent Protocol:
        
        {research_response.content[0].value}
        
        Your summary should be clear, well-structured, and highlight the most important aspects of the A2A Protocol.
        Focus on making the information accessible to someone new to the concept.
        """
        
        summarize_message = Message(
            id=str(uuid.uuid4()),
            sender_id=self.research_agent.id,
            recipient_id=self.summarization_agent.id,
            content=[
                Content(type=ContentType.TEXT, value=summarize_prompt)
            ],
            in_reply_to=research_response.id
        )
        
        # Add the message to the conversation
        self.conversation_manager.add_message_to_conversation(conversation.id, summarize_message)
        
        print("Task forwarded to Summarization Expert...")
        print("-" * 80)
        
        # Have summarization agent process the task
        self.summarization_agent.receive_message(summarize_message)
        summary_response = self.summarization_agent.generate_response(summarize_message)
        
        # Add response to conversation
        self.conversation_manager.add_message_to_conversation(conversation.id, summary_response)
        
        print(f"\nSummarization Expert's summary:")
        # Format multiline responses properly
        summary_text = summary_response.content[0].value.strip()
        formatted_summary = '\n'.join([line.strip() for line in summary_text.split('\n')])
        print(formatted_summary)
        print("-" * 80)
        
        # Update summarize subtask status
        summarize_subtask["status"] = "completed"
        self.task.results["summarize"] = summary_response.content[0].value
        
        # Task completed
        self.task.status = "completed"
        
        print("\nTask completed successfully!")
        print(f"Total messages exchanged: {len(self.conversation_manager.get_conversation_history(conversation.id))}")
        
        # Optional: Research agent provides feedback on the summary
        feedback_prompt = f"""
        Please review the following summary of your research on the Google Agent-to-Agent Protocol:
        
        {summary_response.content[0].value}
        
        Provide brief feedback on the accuracy and completeness of this summary.
        """
        
        feedback_message = Message(
            id=str(uuid.uuid4()),
            sender_id="system",
            recipient_id=self.research_agent.id,
            content=[
                Content(type=ContentType.TEXT, value=feedback_prompt)
            ],
            in_reply_to=summary_response.id
        )
        
        # Add the message to the conversation
        self.conversation_manager.add_message_to_conversation(conversation.id, feedback_message)
        
        # Have research agent provide feedback
        self.research_agent.receive_message(feedback_message)
        feedback_response = self.research_agent.generate_response(feedback_message)
        
        # Add feedback to conversation
        self.conversation_manager.add_message_to_conversation(conversation.id, feedback_response)
        
        print("\nResearch Specialist's feedback on summary:")
        # Format multiline responses properly
        feedback_text = feedback_response.content[0].value.strip()
        formatted_feedback = '\n'.join([line.strip() for line in feedback_text.split('\n')])
        print(formatted_feedback)
        print("=" * 80)


if __name__ == "__main__":
    demo = MultiAgentCollaborationDemo()
    demo.run()