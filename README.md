# README for Tour Guide AI Project

## Project Overview
Tour Guide AI is a comprehensive web application designed to provide users with personalized travel planning assistance. It integrates a powerful Retrieval-Augmented Generation (RAG) system to offer real-time information, cultural insights, and customizable travel itineraries. The application leverages a FastAPI backend with MongoDB for authentication and data management, and a Streamlit-based frontend for an interactive user interface.

## Features
- **User Authentication**: Secure login and registration functionalities with MongoDB as the backend database.
- **Personalized Tour Guide Assistance**: Capabilities to answer travel-related questions, provide cultural insights, and suggest itineraries.
- **Real-Time Information Retrieval**: Web search integration to provide the most up-to-date information on travel destinations.
- **Customizable Itineraries**: Tailored travel plans considering user preferences, time constraints, and other requirements.
- **Team of Specialized Agents**: Distinct agents like the Cultural Expert and Itinerary Planner for in-depth and expert assistance.
- **Web Reading**: Ability to read and extract information from websites.
- **Session Management**: Persistent session states to maintain user interaction and chat history.

## Project Structure


```shell
project-root/
│
├── agents/
│   ├── agent.py              # Contains the agent creation logic
│   ├── app.py                # Main Streamlit app for frontend interaction
│   ├── requirements.txt      # Python dependencies for the agents module
│
├── backend/
│   ├── main.py               # Entry point for the FastAPI application
│   ├── models/               # Contains Pydantic models for request validation
│   ├── routes/               # API routes for user authentication and other features
│   ├── utils/                # Utility functions including password hashing and token management
│   ├── database/             # Database connection setup
├── README.md                 # Project documentation
```

## Backend Setup (FastAPI)

### Prerequisites
Ensure you have Python 3.10+, MongoDB, and PostgreSQL installed on your system.

### Installation
Clone the repository:
```bash
git clone https://github.com/username/repository-name.git
cd project-root/backend
```

## Create a virtual environment and activate it:

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Set up environment variables: Create a .env file and add your MongoDB and PostgreSQL connection details:

env
```shell
DATABASE_URL=mongodb://localhost:27017/your_db
```
## Run the FastAPI server:

```bash
uvicorn main:app --reload
```

## Frontend Setup (Streamlit)

## Prerequisites
Ensure Streamlit and Python 3.11+ are installed.

## Installation
Navigate to the agents folder:

```bash
cd project-root/agents
```

## Create a virtual environment and activate it:

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

## Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Streamlit application:

```bash
streamlit run app.py
```

## Authentication
Users can log in or register using the sidebar interface.

The application will display relevant travel assistant features after successful login.


## How to Use the Tour Guide App

1. Launch the FastAPI backend: Ensure the backend server is running at http://localhost:8000.

2. Launch the Streamlit frontend: Run streamlit run app.py in the agents folder.

3. Access the app: Open the Streamlit app in your web browser. You can log in or register using the sidebar and start interacting with the tour guide agent.

## Available Features : 
1. Get Travel Assistance: Ask questions about travel, culture, and receive curated answers.
2. Plan Itineraries: Create custom travel itineraries based on your input.
3. Real-Time Web Search: Use integrated search tools for current information on destinations.
   
## Dependencies

### Backend:

FastAPI
MongoDB Driver (e.g., motor)
PostgreSQL Driver (psycopg[binary])
Pydantic
passlib for password hashing


### Frontend:

Streamlit
requests for API calls
Additional libraries (see requirements.txt)

