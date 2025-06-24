import requests
import json
import time
import os

def update_m3u_file():
    """
    KabloWebTV API'sinden kanal bilgilerini çeker ve vetteltv.m3u dosyasını günceller.
    """
    url = "https://core-api.kablowebtv.com/api/channels"
    
    # DİKKAT: Authorization token'ı belirli bir süre geçerli olabilir.
    # Bu token'ı sürekli olarak manuel olarak güncellemeniz gerekebilir.
    # Güvenlik nedeniyle gerçek uygulamalarda bu tür token'lar doğrudan kodda tutulmaz.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Referer": "https://tvheryerde.com",
        "Origin": "https://tvheryerde.com",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJMSVZFIiwiaXBiIjoiMCIsImNnZCI6IjA5M2Q3MjBhLTUwMmMtNDFlZC1hODBmLTJiODE2OTg0ZmI5NSIsImNzaCI6IlRSS1NUIiwiZGN0IjoiM0VGNzUiLCJkaSI6ImE2OTliODNmLTgyNmItNGQ5OS05MzYxLWM4YTMxMzIxOGQ0NiIsInNnZCI6Ijg5NzQxZmVjLTFkMzMtNGMwMC1hZmNkLTNmZGFmZTBiNmEyZCIsInNwZ2QiOiIxNTJiZDUzOS02MjIwLTQ0MjctYTkxNS1iZjRiZDA2OGQ3ZTgiLCJpY2giOiIwIiwiaWRtIjoiMCIsImlhIjoiOjpmZmZmOjEwLjAuMC4yMDYiLCJhcHYiOiIxLjAuMCIsImFibiI6IjEwMDAiLCJuYmYiOjE3NDUxNTI4MjUsImV4cCI6MTc0NTE1Mjg4NSwiaWF0IjoxNzQ1MTUyODI1fQ.OSlafRMxef4EjHG5t6TqfAQC7y05IiQjwwgf6yMUS9E"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTP hataları için hata fırlatır (örneğin 404 veya 500)
        
        channels_data = response.json()
        
        m3u_content = "#EXTM3U\n" # M3U dosyasının başlangıcı
        
        for channel in channels_data:
            channel_name = channel.get("name", "Bilinmeyen Kanal")
            stream_url = channel.get("streamUrl")
            channel_id = channel.get("id", "")
            channel_logo = channel.get("logo", "")

            if stream_url:
                # M3U formatında kanal bilgisi ve URL'si
                m3u_content += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{channel_name}" tvg-logo="{channel_logo}",{channel_name}\n'
                m3u_content += f"{stream_url}\n"
        
        with open("vetteltv.m3u", "w", encoding="utf-8") as f:
            f.write(m3u_content)
        
        print(f"vetteltv.m3u dosyası başarıyla güncellendi. Toplam {len(channels_data)} kanal eklendi.")
        
    except requests.exceptions.RequestException as e:
        print(f"API isteği sırasında hata oluştu: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON çözme hatası: {e}. Yanıt metni: {response.text}")
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu: {e}")

# Betiği sürekli çalıştırmak için
def start_continuous_update(interval_minutes=60):
    """
    Belirli aralıklarla M3U dosyasını günceller.
    Args:
        interval_minutes (int): Güncelleme aralığı (dakika cinsinden).
    """
    print(f"M3U dosyasını her {interval_minutes} dakikada bir güncelleyeceğim...")
    while True:
        update_m3u_file()
        print(f"Sonraki güncelleme için {interval_minutes} dakika bekleniyor...")
        time.sleep(interval_minutes * 60) # Dakikayı saniyeye çevir

if __name__ == "__main__":
    # Betiği başlat
    # Her 60 dakikada bir güncelleme yapacak şekilde ayarlandı.
    start_continuous_update(interval_minutes=60)
