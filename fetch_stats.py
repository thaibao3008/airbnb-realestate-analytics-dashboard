import requests
import pandas as pd
from sqlalchemy import create_engine
import urllib
import time

# ==========================================
API_KEY = "688ac630e9b33652bde7ab2a285235dc"
SERVER_NAME = "MICHAEL\\MSSQLSERVER01"
DATABASE_NAME = "FootballAnalyticsDB"

LEAGUES_TO_FETCH = [
    {"id": 255, "season": 2025, "name": "USL Championship"},
    {"id": 103, "season": 2025, "name": "Norway Eliteserien"},
    {"id": 274, "season": 2025, "name": "Indonesia Liga 1"},
    {"id": 273, "season": 2024, "name": "Magyar Kupa"},
    {"id": 639, "season": 2025, "name": "Super Cup"}
]
# ==========================================

def get_stat_value(stats_list, stat_name):
    for s in stats_list:
        if s['type'] == stat_name:
            return s['value'] if s['value'] is not None else 0
    return 0

def fetch_multi_league_2025():
    headers = {"x-apisports-key": API_KEY}
    url_fixtures = "https://v3.football.api-sports.io/fixtures"
    url_stats = "https://v3.football.api-sports.io/fixtures/statistics"
    
    try:
        params_db = urllib.parse.quote_plus(f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;")
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params_db}")

        for league in LEAGUES_TO_FETCH:
            print(f"\n--- Đang xử lý: {league['name']} ---")
            
            # Cơ chế tự động lùi năm nếu không có dữ liệu
            seasons_to_try = [league['season'], 2024]
            fixtures = []
            current_season = league['season']

            for sn in seasons_to_try:
                res = requests.get(url_fixtures, headers=headers, params={"league": league['id'], "season": sn, "status": "FT"})
                fixtures = res.json().get('response', [])
                if fixtures:
                    current_season = sn
                    break
            
            if not fixtures:
                print(f"⚠️ Không tìm thấy trận FT nào cho giải này trong 2024/2025.")
                continue

            # Tăng lên 30 trận để biểu đồ Tableau có ý nghĩa hơn
            target_fixtures = fixtures[-30:]
            print(f"✅ Tìm thấy dữ liệu mùa {current_season}. Đang kéo Stats cho {len(target_fixtures)} trận...")

            for f in target_fixtures:
                f_id = f['fixture']['id']
                
                # Nạp thông tin League & Teams (Dùng try-except lẻ để tránh lỗi trùng Primary Key)
                try:
                    pd.DataFrame([{'league_id': league['id'], 'league_name': league['name'], 'country': f['league']['country']}]).to_sql('Leagues', engine, if_exists='append', index=False)
                except: pass
                
                for side in ['home', 'away']:
                    t = f['teams'][side]
                    try:
                        pd.DataFrame([{'team_id': t['id'], 'team_name': t['name']}]).to_sql('Teams', engine, if_exists='append', index=False)
                    except: pass

                # Nạp Match info
                try:
                    pd.DataFrame([{
                        'match_id': f_id, 'league_id': league['id'], 
                        'match_date': pd.to_datetime(f['fixture']['date']).tz_localize(None),
                        'home_team_id': f['teams']['home']['id'], 'away_team_id': f['teams']['away']['id']
                    }]).to_sql('Matches', engine, if_exists='append', index=False)
                except: pass

                # Nạp Stats chi tiết
                stat_res = requests.get(url_stats, headers=headers, params={"fixture": f_id})
                teams_stats = stat_res.json().get('response', [])
                
                stats_list = []
                for ts in teams_stats:
                    s = ts['statistics']
                    stats_list.append({
                        'match_id': f_id, 'team_id': ts['team']['id'],
                        'is_home': ts['team']['id'] == f['teams']['home']['id'],
                        'goals_scored': f['goals']['home'] if ts['team']['id'] == f['teams']['home']['id'] else f['goals']['away'],
                        'shots_on_goal': get_stat_value(s, "Shots on Goal"),
                        'shots_off_target': get_stat_value(s, "Shots off Goal"),
                        'total_shots': get_stat_value(s, "Total Shots")
                    })
                
                if stats_list:
                    pd.DataFrame(stats_list).to_sql('Team_Match_Stats', engine, if_exists='append', index=False)
                
                time.sleep(1) # Delay tránh cháy API (100/ngày)

        print("\n🎉 HOÀN THÀNH! Dữ liệu đã sẵn sàng trong SQL.")

    except Exception as e:
        print(f"❌ Lỗi hệ thống: {e}")

if __name__ == "__main__":
    fetch_multi_league_2025()