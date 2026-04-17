from sqlalchemy import text
from app.db.connection import engine


def normalize_sales_table():
    """Normalize sales table values and enforce shorter column lengths."""
    with engine.begin() as conn:
        conn.execute(text("""
            ALTER TABLE sales
            ALTER COLUMN customer_number TYPE VARCHAR(3)
                USING RIGHT(customer_number::text, 3),
            ALTER COLUMN billing_id TYPE VARCHAR(3)
                USING LEFT(billing_id::text, 3)
        """))

        conn.execute(text("""
            UPDATE sales
            SET net_weight = net_weight::numeric / 29
        """))


def cleanup_daily_sales(limit: int = 100):
    """Keep only the latest `limit` rows per billing_date."""
    with engine.begin() as conn:
        conn.execute(text("""
            DELETE FROM sales
            WHERE ctid IN (
                SELECT ctid
                FROM (
                    SELECT ctid,
                           ROW_NUMBER() OVER (
                               PARTITION BY billing_date::date
                               ORDER BY billing_date DESC, billing_id DESC
                           ) AS rn
                    FROM sales
                ) t
                WHERE rn > :limit
            )
        """), {"limit": limit})


if __name__ == "__main__":
    print("Normalizing sales table...")
    normalize_sales_table()
    print("Trimming sales rows to 100 records per day...")
    cleanup_daily_sales(100)
    print("Done.")
