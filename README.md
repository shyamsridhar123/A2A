# Agent-to-Agent (A2A) Protocol Demo

This project demonstrates a simple implementation of the Google Agent-to-Agent (A2A) protocol using OpenAI's GPT-4.5 and GPT-O3 Mini models.

## Overview

The Agent-to-Agent (A2A) protocol is a standardized communication protocol that enables autonomous AI agents to communicate, coordinate, and collaborate effectively. This demo showcases how different AI models can interact in a structured way using this protocol.

## Features

- Implementation of core A2A protocol components
- Demo of two agents (powered by GPT-4.5 and GPT-O3 Mini) communicating
- Advanced demo with function calling capabilities
- Structured message format following A2A standards
- Conversation management between multiple agents

## Project Structure

```
├── agents/                  # Agent implementations
│   ├── base_agent.py        # Base agent class
│   └── model_agents.py      # Model-specific agent implementations
├── models/                  # Model wrappers
│   ├── openai_model.py      # Base OpenAI model wrapper
│   └── model_implementations.py  # Specific model implementations
├── schemas/                 # A2A protocol schemas
│   └── base.py              # Core schema definitions
├── utils/                   # Utility functions
│   └── conversation.py      # Conversation management
├── main.py                  # Basic demo script
├── advanced_demo.py         # Advanced demo with function calling
├── collaboration_demo.py    # Multi-agent collaboration demo
├── cli.py                   # Command-line interface for all demos
├── requirements.txt         # Project dependencies
└── .env                     # Environment variables (API keys)
```

## Setup

1. Make sure you have Python 3.8+ installed
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your `.env` file with your OpenAI API keys:

```
# Azure OpenAI GPT 4.5 Configuration
AZURE_OPENAI_ENDPOINT_GPT45="your-endpoint-here"
AZURE_OPENAI_KEY_GPT45="your-api-key-here"
AZURE_OPENAI_MODEL_GPT45="gpt-4.5-preview"
AZURE_OPENAI_DEPLOYMENT_GPT45="gpt-4.5-preview"
AZURE_OPENAI_API_VERSION="2025-03-01-preview"

# Azure OpenAI GPT-O3 Mini Configuration
AZURE_OPENAI_ENDPOINT_O3_MINI="your-endpoint-here"
AZURE_OPENAI_KEY_O3_MINI="your-api-key-here"
AZURE_OPENAI_MODEL_O3_MINI="gpt-o3-mini"
AZURE_OPENAI_DEPLOYMENT_O3_MINI="gpt-o3-mini"
```

## Running the Demos

### Basic Demo

The basic demo shows a simple conversation between two agents:

```bash
python main.py
```

### Advanced Demo

The advanced demo showcases function calling capabilities:

```bash
python advanced_demo.py
```

### Collaboration Demo

The collaboration demo shows how multiple agents can work together on a task:

```bash
python collaboration_demo.py
```

### Interactive CLI

Use the command-line interface to choose which demo to run:

```bash
python cli.py [basic|advanced|interactive|collaboration]
```

## A2A Protocol Components

The implementation includes the following key A2A protocol components:

1. **Message Format**: Standardized message structure with IDs, sender/recipient information, and content
2. **Agent Specifications**: Clear definition of agent capabilities and supported protocols
3. **Content Types**: Support for different types of content (text, JSON, etc.)
4. **Conversation Sessions**: Manage and track conversations between agents
5. **Function Calling**: Ability for agents to invoke functions and process results

## Comparison with Official Google A2A Protocol

This implementation is a simplified, educational version of the official [Google A2A Protocol](https://github.com/google/A2A). Here's how our implementation compares:

### Similarities

- **Core Concept**: Both focus on enabling different AI agents to communicate and collaborate
- **Message Structure**: Both use standardized message formats with sender/recipient information
- **Conversation Management**: Our ConversationManager is similar to the Task concept in official A2A
- **Function Calling**: Both support capability sharing through function calls

### Key Differences

1. **HTTP Protocol**: The official A2A uses HTTP endpoints for communication, while our implementation works in-process
2. **Agent Cards**: Official A2A uses "Agent Cards" (JSON files at `/.well-known/agent.json`) for discovery, which our implementation doesn't include
3. **Task States**: Official A2A has formal task states (`submitted`, `working`, `input-required`, `completed`, `failed`, `canceled`), while we use a simpler message exchange model
4. **Enterprise Features**: The official protocol includes push notifications, streaming responses, and security considerations not implemented in our version
5. **Standard Specification**: Our implementation focuses on demonstrating concepts rather than adhering to the formal JSON specification

### Potential Enhancements

To align more closely with the official protocol, future enhancements could include:
- Adding Agent Cards for capability discovery
- Converting agents to expose HTTP endpoints
- Implementing formal task state management
- Adding streaming support and push notifications
- Conforming to the official A2A JSON schema

## Extending the Demo

You can extend this demo by:

- Adding more agent types with different capabilities
- Implementing more complex function calling scenarios
- Creating a web interface for visualization
- Adding support for more content types (images, audio, etc.)
- Implementing A2A protocol extensions

## Resources

- [Google Agent-to-Agent Protocol](https://github.com/google/A2A)
- [Google A2A Documentation](https://google.github.io/A2A/)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)

## License

MIT