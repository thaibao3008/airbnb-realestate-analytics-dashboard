import pandas as pd
from sqlalchemy import create_engine
import urllib

# Cấu hình
SERVER_NAME = "MICHAEL\\MSSQLSERVER01"
DATABASE_NAME = "FootballAnalyticsDB"

def export_latest_data():
    try:
        params = urllib.parse.quote_plus(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SERVER_NAME};"
            f"DATABASE={DATABASE_NAME};"
            f"Trusted_Connection=yes;"
        )
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        
        # Truy vấn dữ liệu từ View đã cập nhật
        query = "SELECT * FROM View_Football_Analysis ORDER BY match_date DESC"
        df = pd.read_sql(query, engine)
        
        # Xuất file đè lên file cũ
        df.to_csv('Football_Analysis_Data.csv', index=False, encoding='utf-8-sig')
        print(f"✅ Đã cập nhật xong! Tổng cộng có {len(df)} dòng dữ liệu từ các giải đấu.")
        
    except Exception as e:
        print("❌ Lỗi xuất file:", e)

if __name__ == "__main__":
    export_latest_data()