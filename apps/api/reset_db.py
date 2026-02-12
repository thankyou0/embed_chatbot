import asyncio
from sqlalchemy import text
from app.core.database import engine

async def reset_db():
    print("Resetting database schema...")
    try:
        async with engine.begin() as conn:
            # Drop the entire public schema and recreate it
            # This wipes all tables and the alembic_version history
            await conn.execute(text("DROP SCHEMA public CASCADE"))
            await conn.execute(text("CREATE SCHEMA public"))
            await conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
            print("Schema reset successfully!")
    except Exception as e:
        print(f"Error resetting database: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(reset_db())