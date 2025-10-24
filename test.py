from Caiosql import msql
import asyncio

async def test():
    k = await msql.connected('core')
    data = await k.fetchall('SELECT user_id, coin FROM banking')
    for i, s in data:
        print(f"[core] {i} - {s}")

async def test2():
    k = await msql.connected('guild')
    data = await k.fetchall('SELECT user_id, channel_name FROM voice_users')
    for i, s in data:
        print(f"[guild] {i} - {s}")

async def main():
    await asyncio.gather(test(), test2())

asyncio.run(main())
#Update Custom AioMysql
