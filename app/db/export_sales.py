import pandas as pd
from app.db.connection import engine
import os

def export_sales_to_csv(output_path: str = "sales_export.csv"):
    """Export sales table to CSV file."""
    query = "SELECT * FROM sales"
    df = pd.read_sql(query, engine)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"Exported {len(df)} rows to {output_path}")

if __name__ == "__main__":
    export_sales_to_csv()