from sqlalchemy import text
from src.database import engine
from src.models.mcp_tool import McpTool
from sqlmodel import SQLModel

def cleanup_and_fix_mcp_table():
    """Drop and recreate the MCP tools table properly."""
    with engine.connect() as conn:
        # Drop the existing table
        print("Dropping existing mcp_tools table...")
        conn.execute(text("DROP TABLE IF EXISTS mcp_tools CASCADE;"))
        conn.commit()

        # Recreate the table with proper schema
        print("Recreating mcp_tools table with proper schema...")
        SQLModel.metadata.create_all(engine)
        print("Table recreated successfully!")

        # Verify the columns
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'mcp_tools'
            ORDER BY ordinal_position;
        """)).fetchall()

        print('\nColumns in recreated mcp_tools table:')
        for col in result:
            print(f'  {col[0]}: {col[1]} (nullable: {col[2]})')

if __name__ == "__main__":
    cleanup_and_fix_mcp_table()