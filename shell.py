from configparser import ConfigParser
from tkinter import filedialog
import aiomysql,asyncio
import logging,os,importlib,sys,subprocess,socket
from typing import Optional
logger = logging.getLogger("msql_logger")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    os.makedirs("logs", exist_ok=True)
    file_handler = logging.FileHandler("logs/msql.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

# Required packages
REQUIRED_PACKAGES = {
    "aiohttp": "aiohttp",
    "customtkinter": "customtkinter",
    "aiomysql": "aiomysql"
}

def install_missing_pack():
    for module_name, pip_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            logger.info(f'Missing Package: {pip_name}. Starting download...')
            subprocess.run([sys.executable, "-m", "pip", "install", pip_name], check=True)

async def save_config(host, port, user, password):
    __path__ = "Config/configdb.cfg"
    try:
        os.makedirs(os.path.dirname(__path__), exist_ok=True)
        config = ConfigParser()
        if not config.has_section("database"):
            config.add_section("database")

        config.set("database", "host", host)
        config.set("database", "port", str(port))
        config.set("database", "user", user)
        config.set("database", "password", password)

        with open(__path__, "w") as configfile:
            config.write(configfile)

        logger.info("Saved database config successfully.")
    except Exception as e:
        logger.exception(f"[SAVE CONFIG ERROR] {e}")

class CAioMysql:
    def __init__(self, pool: Optional[aiomysql.Pool] = None) -> None:
        self.pool: aiomysql.Pool = pool
        #logger.info('Initialized Custom Aiomysql Wrapper.')

    @staticmethod
    async def check_connect() -> Optional[str]:
        try:
            with socket.create_connection(('youtube.com', 80), timeout=5):
                logger.info('Internet connection verified.')
                return None
        except Exception:
            logger.warning('No internet connection or very low connection.')
            return "Connection Error"

    @classmethod
    async def connectdb(
        cls,
        host: str,
        port: int,
        user: str,
        password: str,
        db: str,
        minsize: int = 1,
        maxsize: int = 10,
        autocommit: bool = True,
    ):
        if host != "localhost":
            connection_error = await cls.check_connect()
            if connection_error:
                logger.error("Connection error before attempting to connect to database.")
                raise ConnectionError(connection_error)

        try:
            pool = await aiomysql.create_pool(
                host=host,
                port=port,
                user=user,
                password=password,
                db=db,
                minsize=minsize,
                maxsize=maxsize,
                autocommit=autocommit,
            )
            logger.info(f"Connected to {host}:{port} - Database: {db}")
            return cls(pool=pool)
        except aiomysql.Error as ae:
            logger.exception(f"[AIOMYSQL ERROR] {ae}")
            raise ae
        except Exception as e:
            logger.exception(f"[CONNECTDB EXCEPTION] {e}")
            raise e

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("Database connection pool closed.")

    async def connect(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        db: str,
        minsize: int = 1,
        maxsize: int = 10,
        autocommit: bool = True,
    ):
        try:
            logger.info(f"Connecting to DB {db} at {host}:{port} as {user}")
            new_pool = await self.__class__.connectdb(
                host, port, user, password, db, minsize, maxsize, autocommit
            )
            self.pool = new_pool.pool
            await save_config(host, port, user, password)
            logger.info("Connection established and config saved.")
            return self
        except Exception as e:
            logger.exception("Exception while connecting:")
            raise e

    

    async def execute(
        self, query: str, params: Tuple[Any] = None
    ) -> List[Tuple[Any]]:
        if not self.pool:
            raise Exception("Database chưa kết nối.")
        try:
            logger.info(f"[EXECUTE] Query: {query} | Params: {params}")
            async with self.pool.acquire() as con:
                connection: aiomysql.Connection = con
                async with connection.cursor() as cur:
                    cursor: aiomysql.Cursor = cur
                    await cursor.execute(query, params)
                    if query.strip().upper().startswith("SELECT"):
                        result = await cursor.fetchall()
                        logger.info(f"[EXECUTE] Rows returned: {len(result)}")
                        return result
                    else:
                        await connection.commit()
                        logger.info(f"[EXECUTE] Rows affected: {cursor.rowcount}")
                        return cursor.rowcount
        except Exception as e:
            logger.exception(f"[EXECUTE ERROR] {e}")
            raise e

    async def fetchall(
        self, query: str, params: Optional[Tuple] = None
    ) -> List:
        if not self.pool:
            raise Exception("Database chưa kết nối.")
        try:
            logger.info(f"[FETCHALL] Query: {query} | Params: {params}")
            async with self.pool.acquire() as con:
                connection: aiomysql.Connection = con
                async with connection.cursor() as cur:
                    cursor: aiomysql.Cursor = cur
                    await cursor.execute(query, params)
                    results = await cursor.fetchall()
                    logger.info(f"[FETCHALL] Rows: {len(results)}")
                    return results
        except Exception as e:
            logger.exception(f"[FETCHALL ERROR] {e}")
            raise e

    async def fetchone(
        self, query: str, params: Optional[Tuple] = None
    ) -> List:
        if not self.pool:
            raise Exception("Database chưa kết nối.")
        try:
            logger.info(f"[FETCHONE] Query: {query} | Params: {params}")
            async with self.pool.acquire() as con:
                connection: aiomysql.Connection = con
                async with connection.cursor() as cur:
                    cursor: aiomysql.Cursor = cur
                    await cursor.execute(query, params)
                    result = await cursor.fetchone()
                    logger.info(f"[FETCHONE] Result: {result}")
                    return result
        except Exception as e:
            logger.exception(f"[FETCHONE ERROR] {e}")
            raise e

    async def connected(self, db: str, __path__: str = None):
        async def load_config(file_name: str) -> List[Tuple]:
            config = ConfigParser()
            config.read(file_name)
            host = config.get("database", "host")
            port = config.getint("database", "port", fallback=3306)
            user = config.get("database", "user")
            password = config.get("database", "password")
            if not host or not user or not password:
                raise ValueError("Thiếu host/user/password trong config.")
            return [host, port, user, password]
        
        if __path__ is None:
            return "No config file found."
        
        data = await load_config(__path__)
        await self.connect(*data, db=db)

async def mysql_shell():
    print("=== Python MySQL Guild CMD ===")

    # Bước 1: Yêu cầu chọn file config
    #config_path = input("Nhập đường dẫn tới file config (vd: Config/configdb.cfg): ").strip()
    config_path=filedialog.askopenfilename(title="Chọn file config",filetypes=[("Config files", "*.cfg")])
    if not config_path:
        print("❌ File config không tồn tại.")
        return
    db = CAioMysql()
    try:
        await db.connected("mysql",config_path) 
    except Exception as e:
        print(f"❌ Lỗi kết nối: {e}")
        return
    print("✅ Kết nối tới host thành công.")
    while True:
        dbname = input("Nhập tên database để USE (hoặc gõ 'exit' để thoát): ").strip()
        if dbname.lower() == "exit":
            break
        try:
            await db.connected(dbname)
            print(f"✅ Đã chọn database {dbname}")
            break
        except Exception as e:
            print(f"❌ Lỗi: {e}")
    print("Nhập SQL command để thực thi (gõ 'exit' để thoát)")
    while True:
        query = input("SQL> ").strip()
        if query.lower() == "exit":
            break
        try:
            if query.lower().startswith("select"):
                result = await db.execute(query)
                if result:
                    for row in result:
                        print(row)
                else:
                    print("⚠️ Không có kết quả.")
            else:
                rowcount = await db.execute(query)
                print(f"✅ Query OK, {rowcount} rows affected.")
        except Exception as e:
            print(f"❌ Lỗi khi thực thi: {e}")

    await db.close()
    print("🔒 Đã đóng kết nối.")

if __name__ == "__main__":
    asyncio.run(mysql_shell())
