import pandas as pd
import pyodbc
import numpy as np
import time

class SQLServerConnector:
    """Quản lý kết nối an toàn tới SQL Server"""
    def __init__(self):
        # Điền chính xác tên Server Instance của bạn dưới dạng Raw String
        self.server = r'MICHAEL\MSSQLSERVER01'  
        self.database = 'AirbnbAnalytics'
        
        # Chuỗi kết nối tự động gọi biến self.server phía trên
        self.conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"Trusted_Connection=yes;"
        )
        self.conn = None

    def get_connection(self):
        if not self.conn:
            self.conn = pyodbc.connect(self.conn_str)
        return self.conn

class DataPipeline:
    """Đóng gói logic ETL tối ưu hóa hiệu năng (Bulk Insert)"""
    def __init__(self, db_connection, df_data):
        self.conn = db_connection
        self.df = df_data

    def load_dim_neighborhoods(self):
        cursor = self.conn.cursor()
        unique_areas = self.df[['neighbourhood_group', 'neighbourhood']].drop_duplicates()
        
        # Chuyển đổi sang danh sách các Tuple để chuẩn bị cho executemany
        records = list(unique_areas.itertuples(index=False, name=None))
        
        # Sử dụng kết hợp câu lệnh SQL kiểm tra tránh trùng lặp danh mục
        query = """
            IF NOT EXISTS (
                SELECT 1 FROM Dim_Neighborhoods 
                WHERE NeighbourhoodGroup = ? AND Neighbourhood = ?
            )
            INSERT INTO Dim_Neighborhoods (NeighbourhoodGroup, Neighbourhood) VALUES (?, ?);
        """
        # Gấp đôi tham số cho câu lệnh IF NOT EXISTS và INSERT
        bulk_data = [r + r for r in records]
        cursor.executemany(query, bulk_data)
        self.conn.commit()

    def load_fact_listings(self):
        cursor = self.conn.cursor()
        # Kích hoạt tính năng tăng tốc ghi hàng loạt của pyodbc
        cursor.fast_executemany = True
        
        listings_df = self.df[['id', 'name', 'host_id', 'room_type', 'construction_year']].copy()
        # Thay thế NaN thành None để SQL Server hiểu là giá trị NULL
        listings_df = listings_df.replace({np.nan: None})
        
        records = list(listings_df.itertuples(index=False, name=None))
        
        # Cấu trúc MERGE (UPSERT) tối ưu dữ liệu lớn
        query = """
            MERGE Fact_Listings AS Target
            USING (SELECT ? AS ListingID) AS Source
            ON (Target.ListingID = Source.ListingID)
            WHEN MATCHED THEN
                UPDATE SET ListingName = ?, HostID = ?, RoomType = ?, ConstructionYear = ?
            WHEN NOT MATCHED THEN
                INSERT (ListingID, ListingName, HostID, RoomType, ConstructionYear)
                VALUES (Source.ListingID, ?, ?, ?, ?);
        """
        # Ánh xạ tham số tương ứng cho cấu trúc MERGE
        bulk_data = [(r[0], r[1], r[2], r[3], r[4], r[1], r[2], r[3], r[4]) for r in records]
        
        cursor.executemany(query, bulk_data)
        self.conn.commit()

    def load_log_prices(self):
        cursor = self.conn.cursor()
        cursor.fast_executemany = True
        
        prices_df = self.df[['id', 'price', 'service_fee']].copy()
        prices_df = prices_df.replace({np.nan: None})
        
        records = list(prices_df.itertuples(index=False, name=None))
        
        query = "INSERT INTO Log_DailyPrices (ListingID, Price, ServiceFee) VALUES (?, ?, ?)"
        cursor.executemany(query, records)
        self.conn.commit()

if __name__ == "__main__":
    # 1. Khai báo đúng tên file bao gồm cả đuôi nén .gz
    file_path = "airbnb_cleaned_v2.csv.gz"
    
    print("-> Đang nạp file dữ liệu nén vào bộ nhớ...")
    # 2. Bổ sung tham số compression='gzip' để Pandas tự động giải nén ngầm trên RAM
    df_clean = pd.read_csv(file_path, compression='gzip', low_memory=False)
    
    db_connector = SQLServerConnector()
    # ... (giữ nguyên toàn bộ code phía dưới)
    connection = db_connector.get_connection()
    pipeline = DataPipeline(connection, df_clean)
    
    # Đo lường thời gian thực thi để kiểm định hiệu năng
    start_time = time.time()
    
    print("-> Đang thực hiện Bulk Insert vào Dim_Neighborhoods...")
    pipeline.load_dim_neighborhoods()
    
    print("-> Đang thực hiện Bulk Insert vào Fact_Listings...")
    pipeline.load_fact_listings()
    
    print("-> Đang thực hiện Bulk Insert vào Log_DailyPrices...")
    pipeline.load_log_prices()
    
    end_time = time.time()
    print(f"=== HOÀN THÀNH NẠP DỮ LIỆU TRONG: {round(end_time - start_time, 2)} GIÂY ===")