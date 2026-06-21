import requests

API_KEY = "688ac630e9b33652bde7ab2a285235dc"
HEADERS = {"x-apisports-key": API_KEY}

# Danh sách các ID bạn muốn kiểm tra
CHECK_LIST = [273, 255, 103, 274, 639]

def check_available_seasons():
    url = "https://v3.football.api-sports.io/leagues"
    
    for l_id in CHECK_LIST:
        print(f"\n🔍 Kiểm tra ID: {l_id}")
        response = requests.get(url, headers=HEADERS, params={"id": l_id})
        data = response.json().get('response', [])
        
        if data:
            league_name = data[0]['league']['name']
            # Lấy danh sách các năm có dữ liệu
            seasons = [s['year'] for s in data[0]['seasons']]
            print(f"✅ Tên giải: {league_name}")
            print(f"📅 Các mùa giải có sẵn: {seasons}")
            
            # Kiểm tra xem mùa gần nhất có bao nhiêu trận
            latest_season = seasons[-1]
            fix_url = "https://v3.football.api-sports.io/fixtures"
            f_res = requests.get(fix_url, headers=HEADERS, params={"league": l_id, "season": latest_season})
            total_matches = len(f_res.json().get('response', []))
            print(f"📊 Mùa {latest_season} hiện có: {total_matches} trận")
        else:
            print(f"❌ Không tìm thấy thông tin cho ID: {l_id}")

check_available_seasons()