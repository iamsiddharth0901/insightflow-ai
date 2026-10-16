import pytest

from app.tools.sql.validator import UnsafeQueryError, validate_query


def test_allows_curated_select_and_adds_limit():
    sql = validate_query("SELECT region, revenue FROM v_sales_enriched")
    assert sql.endswith("LIMIT 500")


@pytest.mark.parametrize("sql", [
    "DELETE FROM sales",
    "SELECT * FROM sales",
    "SELECT * FROM v_sales_enriched; DROP TABLE sales",
    "SELECT * FROM v_sales_enriched -- no",
])
def test_blocks_unsafe_sql(sql):
    with pytest.raises(UnsafeQueryError):
        validate_query(sql)
