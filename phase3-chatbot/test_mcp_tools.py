"""Test script to verify MCP tools are properly implemented."""
import asyncio
from backend.mcp.tools import mcp_server


async def test_tool_registration():
    """Test that all 5 MCP tools are properly registered."""
    print("Testing MCP tool registration...")

    # Get the registered tools
    tools = mcp_server._tools
    tool_names = [tool.name for tool in tools.values()]

    print(f"Registered tools: {tool_names}")

    # Expected tools
    expected_tools = ["add_task", "list_tasks", "complete_task", "delete_task", "update_task"]

    # Check if all expected tools are present
    missing_tools = [tool for tool in expected_tools if tool not in tool_names]
    extra_tools = [tool for tool in tool_names if tool not in expected_tools]

    if missing_tools:
        print(f"❌ Missing tools: {missing_tools}")
        return False

    if extra_tools:
        print(f"⚠️  Extra tools (not expected): {extra_tools}")

    print("✅ All 5 MCP tools are properly registered!")

    # Display tool details
    for tool in tools.values():
        print(f"\nTool: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"Input schema: {tool.input_schema}")

    return True


if __name__ == "__main__":
    success = asyncio.run(test_tool_registration())
    if success:
        print("\n🎉 MCP tools verification completed successfully!")
    else:
        print("\n❌ MCP tools verification failed!")
        exit(1)