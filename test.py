from Caiosql import msql
import asyncio
testdb1=msql()
testdb2=msql()
async def test():
    k = await testdb1.connected('core')
    data = await k.fetchall('SELECT user_id, coin FROM banking')
    for i, s in data:
        print(f"[core] {i} - {s}")

async def test2():
    k = await testdb2.connected('guild')
    data = await k.fetchall('SELECT user_id, channel_name FROM voice_users')
    for i, s in data:
        print(f"[guild] {i} - {s}")

async def main():
    await asyncio.gather(test(), test2())

asyncio.run(main())
#Update Custom AioMysql
