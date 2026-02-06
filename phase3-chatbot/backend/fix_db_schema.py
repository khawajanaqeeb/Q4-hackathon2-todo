from sqlalchemy import text
from src.database import engine

def fix_mcp_tools_schema():
    """Fix the MCP tools table schema by adding missing columns."""
    with engine.connect() as conn:
        # Check if the column exists
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'mcp_tools' AND column_name = 'tool_schema'
        """)).fetchone()

        if result:
            print('Column tool_schema already exists')
        else:
            print('Adding missing tool_schema column to mcp_tools table...')
            # Add the JSON column
            conn.execute(text("ALTER TABLE mcp_tools ADD COLUMN tool_schema JSON;"))
            conn.commit()
            print('Column tool_schema added successfully!')

        # Ensure the column is properly set up
        conn.execute(text("UPDATE mcp_tools SET tool_schema = '{}' WHERE tool_schema IS NULL;"))
        conn.execute(text("ALTER TABLE mcp_tools ALTER COLUMN tool_schema SET NOT NULL;"))
        conn.commit()
        print('Database schema fixed successfully!')

if __name__ == "__main__":
    fix_mcp_tools_schema()