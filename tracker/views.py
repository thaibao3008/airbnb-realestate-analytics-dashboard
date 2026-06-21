from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection

def dashboard_home(request):
    """View thực thi Raw SQL phân tích biến động giá và đẩy ra Frontend"""
    
    query = """
        WITH PriceHistory AS (
            SELECT 
                fl.ListingName,
                ldp.RecordDate,
                ldp.Price,
                LAG(ldp.Price, 1) OVER (PARTITION BY ldp.ListingID ORDER BY ldp.RecordDate) AS PreviousPrice
            FROM Log_DailyPrices ldp
            JOIN Fact_Listings fl ON ldp.ListingID = fl.ListingID
        )
        SELECT TOP 10 ListingName, RecordDate, Price, PreviousPrice, 
               ROUND(((Price - PreviousPrice) / PreviousPrice) * 100, 2) AS ChangePct
        FROM PriceHistory
        WHERE PreviousPrice IS NOT NULL AND (Price - PreviousPrice) < 0
        ORDER BY ChangePct ASC; -- Lấy Top 10 nhà giảm giá mạnh nhất
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        # Chuyển đổi kết quả Tuple thành List of Dictionaries để HTML dễ đọc
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return render(request, 'tracker/dashboard.html', {'price_drops': results})

def chart_data_api(request):
    """API Endpoint trả về dữ liệu thống kê cho Chart.js"""
    
    # [Giữ nguyên query_trend và query_distribution ở đây...]
    query_trend = "SELECT CONVERT(VARCHAR, RecordDate, 23) AS Date, ROUND(AVG(Price), 2) AS AvgPrice FROM Log_DailyPrices GROUP BY RecordDate ORDER BY RecordDate ASC"
    query_distribution = "SELECT RoomType, COUNT(ListingID) AS Total FROM Fact_Listings GROUP BY RoomType"
    
    # THÊM MỚI: Truy vấn 3 - Phân bổ giá theo Thập kỷ xây dựng
    query_age = """
        SELECT 
            CASE 
                WHEN ConstructionYear >= 2020 THEN '2020s (Mới)'
                WHEN ConstructionYear >= 2010 THEN '2010s'
                WHEN ConstructionYear >= 2000 THEN '2000s'
                WHEN ConstructionYear >= 1990 THEN '1990s'
                ELSE 'Trước 1990 (Cổ điển)'
            END AS BuildDecade,
            ROUND(AVG(ldp.Price), 2) AS AvgPrice
        FROM Fact_Listings fl
        JOIN Log_DailyPrices ldp ON fl.ListingID = ldp.ListingID
        WHERE fl.ConstructionYear IS NOT NULL
        GROUP BY 
            CASE 
                WHEN ConstructionYear >= 2020 THEN '2020s (Mới)'
                WHEN ConstructionYear >= 2010 THEN '2010s'
                WHEN ConstructionYear >= 2000 THEN '2000s'
                WHEN ConstructionYear >= 1990 THEN '1990s'
                ELSE 'Trước 1990 (Cổ điển)'
            END
        ORDER BY BuildDecade DESC;
    """
    
    # Khai báo thêm list để chứa dữ liệu mới
    data = {
        'dates': [], 'prices': [], 
        'room_types': [], 'room_counts': [],
        'decades': [], 'decade_prices': []  # <-- Thêm 2 mảng này
    }
    
    with connection.cursor() as cursor:
        # [Giữ nguyên code lấy dữ liệu của trend và distribution...]
        cursor.execute(query_trend)
        for row in cursor.fetchall():
            data['dates'].append(row[0])
            data['prices'].append(float(row[1]))
            
        cursor.execute(query_distribution)
        for row in cursor.fetchall():
            data['room_types'].append(row[0] if row[0] else 'Unknown')
            data['room_counts'].append(row[1])
            
        # THÊM MỚI: Thực thi lấy dữ liệu giá theo thập kỷ
        cursor.execute(query_age)
        for row in cursor.fetchall():
            data['decades'].append(row[0])
            data['decade_prices'].append(float(row[1]))
            
    return JsonResponse(data)