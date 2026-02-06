#!/usr/bin/env python
"""
Database initialization script for Phase 3 Chatbot
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database import create_db_and_tables, engine
from src.main import register_todo_tools
from src.models.mcp_tool import McpTool
from sqlmodel import SQLModel
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize database with all required tables."""
    logger.info("Initializing database tables...")
    try:
        create_db_and_tables()

        # Ensure McpTool table structure is up to date
        # This will create the table if it doesn't exist, or validate it exists with proper schema
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created/updated successfully!")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def register_tools():
    """Register MCP tools."""
    logger.info("Registering MCP tools...")
    try:
        register_todo_tools()
        logger.info("MCP tools registered successfully!")
    except Exception as e:
        logger.error(f"Error registering tools: {e}")
        # Don't raise here as this shouldn't block startup

if __name__ == "__main__":
    logger.info("Starting Phase 3 Chatbot database initialization...")
    initialize_database()
    register_tools()
    logger.info("Phase 3 Chatbot initialization complete!")