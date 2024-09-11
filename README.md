# START Matchmaking

## Overview
This project is a Slack-based matchmaking bot for START Munich. The bot allows users to upload their CVs and find matches based on skills and experiences.

## Key Components

### 1. main.py
The entry point of the application. It initializes the database and starts the Slack service.

### 2. slack_service.py
Handles interactions with the Slack API, including:
- Receiving messages and file uploads
- Routing messages to the appropriate handlers
- Initializing the Slack bot

### 3. db_service.py
Manages all database operations using SurrealDB. Key functions include:
- Initializing the database connection
- Saving and updating user profiles
- Performing similarity searches on CV contents

#### Vector Search Explained
The bot uses vector search to find matches. Here's how it works:
1. CVs are converted into numerical representations (embeddings)
2. These embeddings are stored in the database
3. When searching, the query is converted to an embedding
4. The database finds CVs with similar embeddings to the query

This allows for "fuzzy" matching, finding relevant skills even if the exact words don't match.

### 4. chains.py
Contains the core logic for processing messages and performing searches using LangChain. It defines several "chains" (sequences of operations) for different bot functionalities.

### 5. prompts.py
Stores the prompts used by the language model to generate responses. These prompts define the bot's personality and guide its responses.

### 6. model/
Contains data models used throughout the application:
- `startie.py`: Defines the Startie class, representing a user profile
- `chunk.py`: Defines the Chunk class, representing a piece of CV content

### 7. cli_service.py
A command-line interface for testing the bot's functionality without Slack integration.

## Setup and Running

1. Install dependencies:
`pip install -r requirements.txt`
