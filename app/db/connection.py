from sqlalchemy import create_engine

DB_URI = "postgresql://admin:admin@localhost:5432/sales_db"

engine = create_engine(DB_URI)