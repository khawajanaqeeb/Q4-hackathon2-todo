"""MCP Server for Phase 3 Todo AI Chatbot.

This module sets up the MCP (Multi-Agent Communication Protocol) server
to serve the tools implemented in tools.py
"""
from .tools import mcp_server


def get_mcp_server():
    """Get the configured MCP server instance."""
    return mcp_server


# If running as main, start the server
if __name__ == "__main__":
    import asyncio

    async def main():
        # Start the server
        async with mcp_server:
            await mcp_server.run()

    asyncio.run(main())