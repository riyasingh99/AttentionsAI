from typing import List
import streamlit as st
from phi.assistant import Assistant
from phi.document import Document
from phi.document.reader.pdf import PDFReader
from phi.document.reader.website import WebsiteReader
from phi.utils.log import logger
from agent import get_tour_guide_agent

# Add custom CSS for background and heading color

import requests

# Backend URL (replace with your actual backend URL)
BACKEND_URL = "http://localhost:8000"

# Session state initialization for user authentication status
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# Function to handle login
def login_user(username, password):
    # Send username and password to the backend
    response = requests.post(f"{BACKEND_URL}/login", json={"username": username, "password": password})
    
    if response.status_code == 200:
        # Show success message from the backend
        st.success(f"{response.json().get('message')}")
        return True
    else:
        # Display the error message returned by the backend
        st.error(f"{response.json().get('detail')}")
        return False

# Function to handle registration
def register_user(username, password, email):
    # Send username, password, and email to the backend
    response = requests.post(f"{BACKEND_URL}/register", json={"username": username, "password": password, "email": email})
    
    if response.status_code == 201:
        # Show success message from the backend
        st.success(f"{response.json().get('message')}")
        return True
    else:
        # Display the error message returned by the backend
        st.error(f"{response.json().get('detail')}")
        return False

# Set up page configuration
st.set_page_config(
    page_title="Tour AssistAI",
    page_icon=":🔍",
)
st.title("Welcome to your Personalized Tour Guide and Itenary Planner 🧭")
# Add custom CSS for background and heading color
st.markdown(
    """
    <style>
    body {
        background-color: #FFFFE0; /* Light yellow background */
    }
    .stMarkdown h1 {
        color: #FFFFE0; /* Blue color for headings */
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <style>
        .css-1d391kg {  /* This class targets the sidebar title */
            padding-top: -50px !important;
        }
    </style>
    """, 
    unsafe_allow_html=True
)

# Sidebar for Authentication
st.sidebar.title("Authentication")
auth_choice = st.sidebar.radio("Choose an option", ["Login", "Register"])

if not st.session_state.get("authenticated", False):
    if auth_choice == "Login":
        st.sidebar.header("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if login_user(username, password):
                st.sidebar.success(f"Welcome back, {username}!")
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.experimental_rerun()

    elif auth_choice == "Register":
        st.sidebar.header("Register")
        username = st.sidebar.text_input("Create Username")
        password = st.sidebar.text_input("Create Password", type="password")
        email = st.sidebar.text_input("Enter Email")  # Added the email field
        
        if st.sidebar.button("Register"):
            if register_user(username, password, email):  # Send the email to the register_user function
                st.sidebar.info("You can now log in.")

# Show Welcome message if authenticated
if st.session_state.get("authenticated", False):
    st.sidebar.subheader(f"Welcome, {st.session_state['username']}! 👋")
    st.sidebar.write(f"Logged in as {st.session_state['username']}")
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.experimental_rerun()             

def restart_assistant():
    st.session_state["rag_assistant"] = None
    st.session_state["rag_assistant_run_id"] = None
    if "url_scrape_key" in st.session_state:
        st.session_state["url_scrape_key"] += 1
    if "file_uploader_key" in st.session_state:
        st.session_state["file_uploader_key"] += 1
    st.rerun()

def main() -> None:
    # Check if the user is authenticated before proceeding
    if not st.session_state["authenticated"]:
        st.warning("Please login to access the RAG application.")
        return

    # Get model
    llm_model = st.sidebar.selectbox("Select Model", options=["llama3", "phi3", "openhermes", "llama2"])
    # Set assistant_type in session state
    if "llm_model" not in st.session_state:
        st.session_state["llm_model"] = llm_model
    # Restart the assistant if assistant_type has changed
    elif st.session_state["llm_model"] != llm_model:
        st.session_state["llm_model"] = llm_model
        restart_assistant()

    # Get Embeddings model
    embeddings_model = st.sidebar.selectbox(
        "Select Embeddings",
        options=["nomic-embed-text", "llama3", "openhermes", "phi3"],
        help="When you change the embeddings model, the documents will need to be added again.",
    )
    # Set assistant_type in session state
    if "embeddings_model" not in st.session_state:
        st.session_state["embeddings_model"] = embeddings_model
    # Restart the assistant if assistant_type has changed
    elif st.session_state["embeddings_model"] != embeddings_model:
        st.session_state["embeddings_model"] = embeddings_model
        st.session_state["embeddings_model_updated"] = True
        restart_assistant()

    # Get the assistant
    rag_assistant: Assistant
    if "rag_assistant" not in st.session_state or st.session_state["rag_assistant"] is None:
        logger.info(f"---*--- Creating {llm_model} Assistant ---*---")
        rag_assistant = get_tour_guide_agent()
        st.session_state["rag_assistant"] = rag_assistant
    else:
        rag_assistant = st.session_state["rag_assistant"]

    # Create assistant run (i.e. log to database) and save run_id in session state
    try:
        st.session_state["rag_assistant_run_id"] = rag_assistant.create_run()
    except Exception:
        st.warning("Could not create assistant, is the database running?")
        return

    # Load existing messages
    assistant_chat_history = rag_assistant.memory.get_chat_history()
    if len(assistant_chat_history) > 0:
        logger.debug("Loading chat history")
        st.session_state["messages"] = assistant_chat_history
    else:
        logger.debug("No chat history found")
        st.session_state["messages"] = [{"role": "assistant", "content": "Upload a doc and ask me questions..."}]

    # Prompt for user input
    if prompt := st.chat_input():
        st.session_state["messages"].append({"role": "user", "content": prompt})

    # Display existing chat messages
    for message in st.session_state["messages"]:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is from a user, generate a new response
    last_message = st.session_state["messages"][-1]
    if last_message.get("role") == "user":
        question = last_message["content"]
        with st.chat_message("assistant"):
            response = ""
            resp_container = st.empty()
            with st.spinner("🗺️ Plotting your next adventure... Just a moment! ✈️"
):
                for delta in rag_assistant.run(question):
                    response += delta  # type: ignore
                    resp_container.markdown(response)
                st.session_state["messages"].append({"role": "assistant", "content": response})

# Sidebar with features of the tour guide app
st.sidebar.subheader("App Features")
st.sidebar.write("""
- 🧭 **Real-Time Navigation:** Step-by-step directions.
- 📍 **Nearby Attractions:** Discover places nearby.
- 🗺️ **Custom Itineraries:** Plan your perfect trip.
- ⭐ **Budget Planning:** Get trips planned under your budget.
- 🗺️ **Weather Reports:** Get realtime weather update.
""")


if __name__ == "__main__":
    main()
