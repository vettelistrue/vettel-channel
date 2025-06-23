import requests
import json
import gzip
from io import BytesIO
import os

def get_canli_tv_m3u():
    """
    Kablo Web TV API'sinden canlı TV kanal verilerini çeker ve
    mevcut bir M3U dosyasına yalnızca yeni kanalları ekler.
    Dosyadaki mevcut içerik ve elle eklenen kanallar korunur.
    Klonlanmış girişleri engeller.
    """
    
    url = "https://core-api.kablowebtv.com/api/channels"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Referer": "https://tvheryerde.com",
        "Origin": "https://tvheryerde.com",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJMSVZFIiwiaXBiIjoiMCIsImNnZCI6IjA5M2Q3MjBhLTUwMmMtNDFlZC1hODBmLTJiODE2OTg0ZmI5NSIsImNzaCI6IlRSS1NUIiwiZGN0IjoiM0VGNzUiLCJkaSI6ImE2OTliODNmLTgyNmItNGQ5OS05MzYxLWM4YTMxMzIxOGQ0NiIsInNnZCI6Ijg5NzQxZmVjLTFkMzMtNGMwMC1hZmNkLTNmZGFmZTBiNmEyZCIsInNwZ2QiOiIxNTJiZDUzOS02MjIwLTQ0MjctYTkxNS1iZjRiZDA2OGY3ZTgiLCJpY2giOiIwIiwiaWRtIjoiMCIsImlhIjoiOjpmZmZmOjEwLjAuMC4yMDYiLCJhcHYiOiIxLjAuMCIsImFibiI6IjEwMDAiLCJuYmYiOjE3NDUxNTI4MjUsImV4cCI6MTc0NTE1Mjg4NSwiaWF0IjoxNzQ1MTUyODI1fQ.OSlafRMxef4EjHG5t6TqfAQC7y05IiQjwwgf6yMUS9E"  # Güvenlik için normalde token burada gösterilmemeli
    }
    
    # Mevcut M3U dosyasındaki URL'leri depolamak için bir küme oluşturun
    existing_urls = set()
    m3u_filename = "vetteltv.m3u"

    # --- Mevcut M3U dosyasını oku ve URL'leri topla ---
    if os.path.exists(m3u_filename):
        try:
            with open(m3u_filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for i in range(len(lines)):
                    # Eğer satır bir URL satırı gibi görünüyorsa (http ile başlıyorsa)
                    if lines[i].strip().startswith("http"):
                        existing_urls.add(lines[i].strip())
            print(f"📄 '{m3u_filename}' dosyasındaki {len(existing_urls)} mevcut kanal URL'si yüklendi.")
        except Exception as e:
            print(f"⚠️ '{m3u_filename}' dosyasını okurken hata oluştu: {e}")
            # Hata olsa bile devam et, belki dosya yeni oluşturulacak.

    try:
        print("📡 CanliTV API'den veri alınıyor...")
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        try:
            with gzip.GzipFile(fileobj=BytesIO(response.content)) as gz:
                content = gz.read().decode('utf-8')
        except: # Gzip hatası olursa direkt içeriği dene
            content = response.content.decode('utf-8')
        
        data = json.loads(content)
        
        if not data.get('IsSucceeded') or not data.get('Data', {}).get('AllChannels'):
            print("❌ CanliTV API'den geçerli veri alınamadı!")
            return False
        
        channels = data['Data']['AllChannels']
        print(f"✅ API'den {len(channels)} kanal bulundu.")
        
        # Dosyayı "append" (ekleme) modunda açın.
        # Bu, dosyanın üzerine yazmak yerine, içeriği sonuna ekleyecektir.
        # #EXTM3U başlığı sadece dosya ilk oluşturulduğunda eklenmeli.
        # Eğer dosya boşsa (yeni oluşturulmuşsa veya içi boşaltılmışsa) #EXTM3U ekle.
        # append modunda dosya yoksa sıfırdan oluşturulur.
        write_header = not os.path.exists(m3u_filename) or os.stat(m3u_filename).st_size == 0


        with open(m3u_filename, "a", encoding="utf-8") as f:
            if write_header:
                f.write("#EXTM3U\n")
            
            eklenen_kanal_sayisi = 0
            
            for channel in channels:
                name = channel.get('Name')
                stream_data = channel.get('StreamData', {})
                hls_url = stream_data.get('HlsStreamUrl') if stream_data else None
                logo = channel.get('PrimaryLogoImageUrl', '')
                categories = channel.get('Categories', [])
                
                if not name or not hls_url:
                    continue
                
                group = categories[0].get('Name', 'Genel') if categories else 'Genel'
                
                if group == "Bilgilendirme":
                    continue

                # --- Klonlanmış girişi kontrol et ---
                if hls_url in existing_urls:
                    # print(f"🔍 '{name}' kanalı zaten mevcut, atlanıyor.") # İsteğe bağlı olarak bu satırı açabilirsiniz
                    continue # Kanal zaten varsa döngüde bir sonraki kanala geç
                
                # Kanal yeni ise, dosyaya ekle ve mevcut URL'ler kümesine ekle
                f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{name}\n')
                f.write(f'{hls_url}\n')
                existing_urls.add(hls_url) # Yeni eklenen URL'yi de kümeye ekle

                eklenen_kanal_sayisi += 1
        
        print(f"📺 '{m3u_filename}' dosyasına {eklenen_kanal_sayisi} yeni kanal eklendi!")
        print(f"Toplam kanal sayısı (yaklaşık): {len(existing_urls)}") # API'den gelenler + eski manuel ekledikleriniz
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

if __name__ == "__main__":
    get_canli_tv_m3u()
