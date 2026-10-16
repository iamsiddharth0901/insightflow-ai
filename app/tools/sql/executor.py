import pandas as pd

from app.db.database import connect
from app.tools.sql.validator import validate_query


def execute(sql: str) -> tuple[pd.DataFrame, str]:
    validated = validate_query(sql)
    connection = connect(read_only=True)
    try:
        return pd.read_sql_query(validated, connection), validated
    finally:
        connection.close()
