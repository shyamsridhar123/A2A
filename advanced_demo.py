import time
import sys
import os
import json
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our A2A components
from agents.model_agents import GPT45Agent, GPTO3MiniAgent
from utils.conversation import ConversationManager
from schemas.base import ContentType, Content, Message, FunctionCall, FunctionResult


# Define some sample functions that agents can call
def search_knowledge_base(query: str) -> dict:
    """
    Simulate searching a knowledge base for information.
    
    Args:
        query: The search query
        
    Returns:
        Search results
    """
    # Simulate different responses based on query
    if "a2a protocol" in query.lower():
        return {
            "results": [
                {
                    "title": "Agent-to-Agent Protocol Specification",
                    "summary": "The A2A protocol defines standards for autonomous agent communication.",
                    "url": "https://example.com/a2a-spec"
                },
                {
                    "title": "Google's Agent-to-Agent Communication Framework",
                    "summary": "Technical details of Google's implementation of A2A protocols.",
                    "url": "https://example.com/google-a2a"
                }
            ],
            "total_results": 2
        }
    elif "openai" in query.lower() or "gpt" in query.lower():
        return {
            "results": [
                {
                    "title": "OpenAI Models Overview",
                    "summary": "Comprehensive information about GPT-4.5 and GPT-O3 Mini.",
                    "url": "https://example.com/openai-models"
                }
            ],
            "total_results": 1
        }
    else:
        return {
            "results": [],
            "total_results": 0,
            "message": "No results found for your query."
        }


def analyze_sentiment(text: str) -> dict:
    """
    Simulate sentiment analysis on a text.
    
    Args:
        text: The text to analyze
        
    Returns:
        Sentiment analysis results
    """
    # Very simplified sentiment analysis
    positive_words = ["good", "great", "excellent", "amazing", "helpful", "useful"]
    negative_words = ["bad", "poor", "terrible", "useless", "difficult", "confusing"]
    
    positive_count = sum(word in text.lower() for word in positive_words)
    negative_count = sum(word in text.lower() for word in negative_words)
    
    if positive_count > negative_count:
        sentiment = "positive"
        score = 0.5 + (positive_count - negative_count) * 0.1
    elif negative_count > positive_count:
        sentiment = "negative"
        score = 0.5 - (negative_count - positive_count) * 0.1
    else:
        sentiment = "neutral"
        score = 0.5
        
    # Ensure score is between 0 and 1
    score = max(0, min(score, 1))
        
    return {
        "sentiment": sentiment,
        "score": score,
        "positive_aspects": positive_count,
        "negative_aspects": negative_count
    }


# Define the available functions as specifications
AVAILABLE_FUNCTIONS = {
    "search_knowledge_base": {
        "name": "search_knowledge_base",
        "description": "Search a knowledge base for information on a topic",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        },
        "function": search_knowledge_base
    },
    "analyze_sentiment": {
        "name": "analyze_sentiment",
        "description": "Analyze the sentiment of a text",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to analyze"
                }
            },
            "required": ["text"]
        },
        "function": analyze_sentiment
    }
}


class FunctionCallingDemo:
    def __init__(self):
        self.gpt45_agent = GPT45Agent(name="Research Assistant")
        self.gpt_o3_mini_agent = GPTO3MiniAgent(name="Knowledge Navigator")
        self.conversation_manager = ConversationManager()
        
    def handle_function_call(self, function_call: FunctionCall) -> FunctionResult:
        """
        Handle a function call from an agent.
        
        Args:
            function_call: The function call to handle
            
        Returns:
            The result of the function call
        """
        function_name = function_call.function_name
        arguments = function_call.arguments
        
        if function_name not in AVAILABLE_FUNCTIONS:
            return FunctionResult(
                function_name=function_name,
                error=f"Function {function_name} not found"
            )
            
        try:
            func = AVAILABLE_FUNCTIONS[function_name]["function"]
            result = func(**arguments)
            return FunctionResult(
                function_name=function_name,
                result=result
            )
        except Exception as e:
            return FunctionResult(
                function_name=function_name,
                error=str(e)
            )
    
    def create_function_call_message(self, sender_id: str, recipient_id: str, function_name: str, arguments: dict) -> Message:
        """Create a message containing a function call."""
        function_call = FunctionCall(
            function_name=function_name,
            arguments=arguments
        )
        
        message = Message(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=[
                Content(type=ContentType.JSON, value=function_call.model_dump())
            ],
            in_reply_to=None
        )
        
        return message
    
    def create_function_result_message(self, sender_id: str, recipient_id: str, in_reply_to: str, result: FunctionResult) -> Message:
        """Create a message containing a function result."""
        message = Message(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=[
                Content(type=ContentType.JSON, value=result.model_dump())
            ],
            in_reply_to=in_reply_to
        )
        
        return message
        
    def run(self):
        print("=" * 80)
        print("Advanced A2A Protocol Demo - Function Calling")
        print("Using OpenAI GPT-4.5 and GPT-O3 Mini Models")
        print("=" * 80)
        
        # Create a conversation
        conversation = self.conversation_manager.create_conversation(
            participant_ids=[self.gpt45_agent.id, self.gpt_o3_mini_agent.id],
            metadata={"topic": "A2A Protocol Function Calling Demo"}
        )
        
        print(f"\nStarted conversation: {conversation.id}")
        print(f"Topic: {conversation.metadata.get('topic')}")
        print("-" * 80)
        
        # Initial query from the Research Assistant
        initial_query = """
        I need to gather information about the A2A protocol and analyze how developers feel about it.
        Can you help me search for relevant information and analyze sentiments from developer feedback?
        """
        
        initial_message = self.gpt45_agent.create_message(
            recipient_id=self.gpt_o3_mini_agent.id,
            content_value=initial_query,
            content_type=ContentType.TEXT
        )
        
        self.conversation_manager.add_message_to_conversation(conversation.id, initial_message)
        print(f"\nMessage from {self.gpt45_agent.name}:")
        # Format multiline responses properly
        formatted_query = '\n'.join([line.strip() for line in initial_message.content[0].value.strip().split('\n')])
        print(f"{formatted_query}")
        print("-" * 80)
        
        # Knowledge Navigator decides to call the search function
        print("\nKnowledge Navigator is calling the search_knowledge_base function...")
        
        search_call_message = self.create_function_call_message(
            sender_id=self.gpt_o3_mini_agent.id,
            recipient_id="system",  # Function calls are directed to the system
            function_name="search_knowledge_base",
            arguments={"query": "a2a protocol"}
        )
        
        # Add function call to conversation
        self.conversation_manager.add_message_to_conversation(conversation.id, search_call_message)
        
        # System processes the function call
        function_call = FunctionCall(
            function_name=search_call_message.content[0].value["function_name"],
            arguments=search_call_message.content[0].value["arguments"]
        )
        
        function_result = self.handle_function_call(function_call)
        
        # Create function result message
        result_message = self.create_function_result_message(
            sender_id="system",
            recipient_id=self.gpt_o3_mini_agent.id,
            in_reply_to=search_call_message.id,
            result=function_result
        )
        
        # Add result to conversation
        self.conversation_manager.add_message_to_conversation(conversation.id, result_message)
        
        print("\nSearch Knowledge Base Result:")
        # Pretty print the JSON result
        print(json.dumps(function_result.result, indent=2))
        print("-" * 80)
        
        # Knowledge Navigator responds with the information
        knowledge_response = """
        I've found some information about the A2A protocol for you:
        
        1. The Agent-to-Agent Protocol (A2A) is a specification that defines standards for autonomous agent communication.
        2. Google has its own implementation of the A2A protocol framework.
        
        To analyze developer sentiment about A2A, I'll need to process some sample feedback. Let me do that for you.
        """
        
        response_message = self.gpt_o3_mini_agent.create_message(
            recipient_id=self.gpt45_agent.id,
            content_value=knowledge_response,
            content_type=ContentType.TEXT,
            in_reply_to=initial_message.id
        )
        
        self.conversation_manager.add_message_to_conversation(conversation.id, response_message)
        print(f"\nResponse from {self.gpt_o3_mini_agent.name}:")
        # Format multiline responses properly
        formatted_response = '\n'.join([line.strip() for line in response_message.content[0].value.strip().split('\n')])
        print(f"{formatted_response}")
        print("-" * 80)
        
        # Knowledge Navigator calls sentiment analysis function
        print("\nKnowledge Navigator is calling the analyze_sentiment function...")
        
        # Sample developer feedback
        sample_feedback = """
        The A2A protocol is really helpful for standardizing agent communication. 
        It makes development much easier and provides a great framework for building multi-agent systems.
        However, the documentation could be improved, as some parts are a bit confusing.
        Overall, it's an excellent initiative that will be useful for many developers.
        """
        
        sentiment_call_message = self.create_function_call_message(
            sender_id=self.gpt_o3_mini_agent.id,
            recipient_id="system",
            function_name="analyze_sentiment",
            arguments={"text": sample_feedback}
        )
        
        # Add sentiment function call to conversation
        self.conversation_manager.add_message_to_conversation(conversation.id, sentiment_call_message)
        
        # System processes the sentiment function call
        sentiment_function_call = FunctionCall(
            function_name=sentiment_call_message.content[0].value["function_name"],
            arguments=sentiment_call_message.content[0].value["arguments"]
        )
        
        sentiment_result = self.handle_function_call(sentiment_function_call)
        
        # Create sentiment result message
        sentiment_result_message = self.create_function_result_message(
            sender_id="system",
            recipient_id=self.gpt_o3_mini_agent.id,
            in_reply_to=sentiment_call_message.id,
            result=sentiment_result
        )
        
        # Add result to conversation
        self.conversation_manager.add_message_to_conversation(conversation.id, sentiment_result_message)
        
        print("\nSentiment Analysis Result:")
        # Pretty print the JSON result
        print(json.dumps(sentiment_result.result, indent=2))
        print("-" * 80)
        
        # Knowledge Navigator sends the final analysis
        final_analysis = f"""
        Based on the sentiment analysis of developer feedback about the A2A protocol:
        
        1. Overall sentiment: {sentiment_result.result['sentiment']}
        2. Sentiment score: {sentiment_result.result['score']:.2f} (on a scale from 0 to 1)
        3. Key positive aspects: 
           - Standardization of agent communication
           - Easier development of multi-agent systems
           - Excellent framework for developers
        
        4. Areas for improvement:
           - Documentation clarity
        
        The A2A protocol is generally well-received by developers, with most feedback being positive.
        Would you like me to gather more specific information about any aspect of the protocol?
        """
        
        final_message = self.gpt_o3_mini_agent.create_message(
            recipient_id=self.gpt45_agent.id,
            content_value=final_analysis,
            content_type=ContentType.TEXT
        )
        
        self.conversation_manager.add_message_to_conversation(conversation.id, final_message)
        print(f"\nFinal analysis from {self.gpt_o3_mini_agent.name}:")
        # Format multiline responses properly
        formatted_final = '\n'.join([line.strip() for line in final_message.content[0].value.strip().split('\n')])
        print(f"{formatted_final}")
        print("-" * 80)
        
        # Print conversation summary
        print(f"\nConversation Summary:")
        print(f"  - Total messages: {len(conversation.messages)}")
        print(f"  - Function calls: 2")
        print(f"  - Participants: {self.gpt45_agent.name}, {self.gpt_o3_mini_agent.name}, System")
        print("=" * 80)


if __name__ == "__main__":
    demo = FunctionCallingDemo()
    demo.run()