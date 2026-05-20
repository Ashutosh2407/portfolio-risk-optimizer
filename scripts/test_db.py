import asyncio
import ssl
import asyncpg
import os

async def test():
    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations('/app/global-bundle.pem')
    
    conn = await asyncpg.connect(
        host=os.getenv('DB_HOST'),
        port=5432,
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        ssl=ssl_context
    )
    print("SUCCESS - connected!")
    await conn.close()

asyncio.run(test())