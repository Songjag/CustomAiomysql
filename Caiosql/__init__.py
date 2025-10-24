"""
CAiosql - Custom AioMySQL
~~~~~~~~~~~~~~~~~~~~~~~~~~
Module hỗ trợ kết nối MariaDB và MySQL (async)
Tác giả: Songjag
"""

import logging
from .Caiosql import CAioMysql
msql = CAioMysql()
connect = msql.connect
execute = msql.execute
fetchone = msql.fetchone
fetchall = msql.fetchall
session = msql.session

__all__ = ["msql", "connect", "disconnect", "execute", "fetchone", "fetchall", "session"]
