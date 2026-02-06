from sqlalchemy import text
from src.database import engine

def check_mcp_tools_schema():
    """Check the actual columns in the mcp_tools table."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'mcp_tools'
            ORDER BY ordinal_position;
        """)).fetchall()

        print('Columns in mcp_tools table:')
        for col in result:
            print(f'  {col[0]}: {col[1]} (nullable: {col[2]})')

if __name__ == "__main__":
    check_mcp_tools_schema()