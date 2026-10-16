"""Seed deterministic demo data with a planted South-region Q3 decline."""
from datetime import date, timedelta

from app.core.config import settings
from app.db.database import connect

SCHEMA = """
DROP VIEW IF EXISTS v_sales_enriched;
DROP VIEW IF EXISTS v_target_attainment;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS targets;
CREATE TABLE regions (region_id INTEGER PRIMARY KEY, region_name TEXT UNIQUE NOT NULL);
CREATE TABLE products (product_id INTEGER PRIMARY KEY, product_name TEXT UNIQUE NOT NULL, category TEXT NOT NULL, list_price REAL NOT NULL);
CREATE TABLE sales (sale_id INTEGER PRIMARY KEY, sale_date TEXT NOT NULL, product_id INTEGER NOT NULL, region_id INTEGER NOT NULL, units_sold INTEGER NOT NULL, revenue REAL NOT NULL, cost REAL NOT NULL, discount REAL NOT NULL);
CREATE TABLE targets (target_id INTEGER PRIMARY KEY, month TEXT NOT NULL, product_id INTEGER NOT NULL, region_id INTEGER NOT NULL, revenue_target REAL NOT NULL);
CREATE VIEW v_sales_enriched AS
SELECT s.sale_id, s.sale_date, r.region_name AS region, p.product_name AS product, p.category,
       s.units_sold, s.revenue, s.cost, s.discount
FROM sales s JOIN regions r ON r.region_id=s.region_id JOIN products p ON p.product_id=s.product_id;
CREATE VIEW v_target_attainment AS
SELECT substr(s.sale_date,1,7) AS month, r.region_name AS region, p.product_name AS product,
       round(sum(s.revenue), 2) AS actual_revenue, round(t.revenue_target, 2) AS revenue_target
FROM sales s JOIN regions r ON r.region_id=s.region_id JOIN products p ON p.product_id=s.product_id
LEFT JOIN targets t ON t.region_id=s.region_id AND t.product_id=s.product_id AND t.month=substr(s.sale_date,1,7)
GROUP BY month, region, product, t.revenue_target;
"""


def quarter(day: date) -> int:
    return (day.month - 1) // 3 + 1


def seed() -> None:
    connection = connect()
    connection.executescript(SCHEMA)
    regions = [(1, "North"), (2, "South"), (3, "West")]
    products = [(1, "Atlas", "Hardware", 120.0), (2, "Beacon", "Software", 80.0), (3, "Cobalt", "Services", 60.0)]
    connection.executemany("INSERT INTO regions VALUES (?, ?)", regions)
    connection.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)
    rows, targets, sale_id, target_id = [], [], 1, 1
    current = date(2026, 4, 1)
    end = date(2026, 9, 30)
    while current <= end:
        for region_id, region in regions:
            for product_id, product, _, price in products:
                base_units = {"Atlas": 18, "Beacon": 28, "Cobalt": 22}[product]
                # Planted Q3 South effect: campaign ended and competitor pressure hit Atlas/Beacon.
                multiplier = 0.72 if (region == "South" and quarter(current) == 3 and product != "Cobalt") else 1.0
                units = max(1, round(base_units * multiplier + (current.day % 5) - 2))
                revenue = round(units * price, 2)
                rows.append((sale_id, current.isoformat(), product_id, region_id, units, revenue, round(revenue * .56, 2), 0.0))
                sale_id += 1
        current += timedelta(days=1)
    for month in ("2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"):
        for region_id, region in regions:
            for product_id, product, _, price in products:
                monthly = {"Atlas": 18, "Beacon": 28, "Cobalt": 22}[product] * price * 30
                targets.append((target_id, month, product_id, region_id, monthly,))
                target_id += 1
    connection.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows)
    connection.executemany("INSERT INTO targets VALUES (?, ?, ?, ?, ?)", targets)
    connection.commit()
    connection.close()
    write_documents()


def write_documents() -> None:
    settings.documents_dir.mkdir(parents=True, exist_ok=True)
    documents = {
        "south_campaign_q3.txt": """title: South Campaign Summary Q3 2026
region: South
period: 2026-Q3
page: 1

The South demand-generation campaign ended on 30 June 2026 and was not renewed for Q3. The campaign had primarily promoted Atlas and Beacon. Sales leadership recommended measuring post-campaign demand before attributing all change to the campaign.""",
        "south_competitor_q3.txt": """title: South Competitive Brief Q3 2026
region: South
period: 2026-Q3
page: 2

In July, competitor Nova introduced a temporary 15 percent discount on comparable Atlas and Beacon offerings in South. Field teams reported increased price objections. This is supporting evidence, not proof of the cause of any revenue change.""",
        "south_operations_q3.txt": """title: South Operations Summary Q3 2026
region: South
period: 2026-Q3
page: 4

No material service outages were recorded for Cobalt in South during Q3. Inventory availability was normal for the reviewed products.""",
    }
    for name, content in documents.items():
        (settings.documents_dir / name).write_text(content, encoding="utf-8")


if __name__ == "__main__":
    seed()
