import os
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# Define the path for the SQLite database file
DB_PATH = os.getenv("DB_PATH", "tutor_memory.db")

def get_checkpointer():
    """
    Initializes and returns the LangGraph SqliteSaver.
    In a production environment, this might be swapped for PostgresSaver.
    """
    # check_same_thread=False is required if FastAPI handles requests across multiple threads
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    
    # Initialize the LangGraph Checkpointer with the connection
    memory = SqliteSaver(conn)
    
    # LangGraph requires the tables to be set up. SqliteSaver handles this automatically 
    # upon first write, but it's good practice to ensure the connection is active.
    return memory, conn