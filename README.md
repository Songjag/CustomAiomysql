#Customaiomysql

Async MySQL backend wrapper sử dụng aiomysql với connection pool và hỗ
trợ SSL.

============================================================

1.  Features

-   Async connection pooling
-   TLS/SSL secure connection (TLS >= 1.2)
-   Query timeout support
-   Retry mechanism
-   execute (DML)
-   fetchone
-   fetchall
-   fetchmany (chunk)
-   stream (memory-efficient)
-   pool_recycle tránh stale connection

============================================================

2.  Installation

Yêu cầu: - Python 3.13+ - MySQL 5.7+ / 8+

Cài đặt dependency:

pip install aiomysql,aiohttp

============================================================

3.  Usage

3.1 Connect

import asyncio from your_module import CAioMysql

async def main(): db = CAioMysql()

    await db.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="password",
        db="testdb",
        minsize=5,
        maxsize=20
    )

    await db.close()

asyncio.run(main())

------------------------------------------------------------------------

3.2 SELECT - fetchall

rows = await db.fetchall( “SELECT id, name FROM users WHERE active=%s”,
(1,) )

for row in rows: print(row[“id”], row[“name”])

------------------------------------------------------------------------

3.3 SELECT - fetchone

row = await db.fetchone( “SELECT id, name FROM users WHERE id=%s”, (10,)
)

if row: print(row[“name”])

------------------------------------------------------------------------

3.4 INSERT / UPDATE / DELETE

affected = await db.execute( “UPDATE users SET name=%s WHERE id=%s”,
(“Alice”, 10) )

print(“Rows affected:”, affected)

------------------------------------------------------------------------

3.5 Streaming Large Result

async for row in db.stream( “SELECT id, amount FROM transactions”,
chunk_size=1000 ): process(row)

Memory usage: - fetchall → O(n) - stream → O(chunk_size)

============================================================

License: MIT
hết