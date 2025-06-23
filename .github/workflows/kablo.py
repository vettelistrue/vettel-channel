import requests
import json
import gzip
from io import BytesIO

def get_canli_tv_m3u():
    """
    Kablo Web TV API'sinden canlı TV kanal verilerini çeker ve
    mevcut bir M3U dosyasına ekler. Dosyadaki mevcut içerik korunur.
    """
    
    url = "https://core-api.kablowebtv.com/api/channels"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Referer": "https://tvheryerde.com",
        "Origin": "https://tvheryerde.com",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJMSVZFIiwiaXBiIjoiMCIsImNnZCI6IjA5M2Q3MjBhLTUwMmMtNDFlZC1hODBmLTJiODE2OTg0ZmI5NSIsImNzaCI6IlRSS1NUIiwiZGN0IjoiM0VGNzUiLCJkaSI6ImE2OTliODNmLTgyNmItNGQ5OS05MzYxLWM4YTMxMzIxOGQ0NiIsInNnZCI6Ijg5NzQxZmVjLTFkMzMtNGMwMC1hZmNkLTNmZGFmZTBiNmEyZCIsInNwZ2QiOiIxNTJiZDUzOS02MjIwLTQ0MjctYTkxNS1iZjRiZDA2OGQ3ZTgiLCJpY2giOiIwIiwiaWRtIjoiMCIsImlhIjoiOjpmZmZmOjEwLjAuMC4yMDYiLCJhcHYiOiIxLjAuMCIsImFibiI6IjEwMDAiLCJuYmYiOjE3NDUxNTI4MjUsImV4cCI6MTc0NTE1Mjg4NSwiaWF0IjoxNzQ1MTUyODI1fQ.OSlafRMxef4EjHG5t6TqfAQC7y05IiQjwwgf6yMUS9E"  # Güvenlik için normalde token burada gösterilmemeli
    }
    
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
        print(f"✅ {len(channels)} kanal bulundu.")
        
        # Dosyayı "append" (ekleme) modunda açın.
        # Bu, dosyanın üzerine yazmak yerine, içeriği sonuna ekleyecektir.
        with open("vetteltv.m3u", "a", encoding="utf-8") as f:
            # #EXTM3U başlığı genellikle dosyanın başında bir kez bulunur.
            # Ekleme modunda olduğumuz için her seferinde yazmamalıyız.
            # Eğer dosya hiç yoksa, Python onu oluşturur ancak #EXTM3U yazılmaz.
            # İlk kullanımda bu başlığı manuel olarak dosyanın başına eklemeniz gerekebilir
            # veya dosya boşsa kontrol eden bir mantık ekleyebilirsiniz.
            
            kanal_sayisi = 0
            
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

                # tvg-id: Eğer elle eklediğiniz kanallarla çakışma yaşamak istemiyorsanız,
                # tvg-id'yi ya API'den gelen benzersiz bir değerle doldurun
                # ya da eklediğiniz kanallar için benzersiz bir ön ek kullanın.
                # Basit bir sayaç kullanmak (mevcut kodunuzdaki gibi) çakışmalara yol açabilir.
                # Şimdilik, çakışmayı önlemek adına tvg-id'yi çıkarmayı tercih edebiliriz,
                # veya API'den uygun bir kimlik geliyorsa onu kullanırız.
                # Eğer tvg-id çok kritikse, mevcut dosyayı okuyup en yüksek tvg-id'yi bulup
                # ondan sonra devam etmek daha sağlam bir yöntemdir.
                
                f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{name}\n')
                f.write(f'{hls_url}\n')

                kanal_sayisi += 1
        
        print(f"📺 vetteltv.m3u dosyasına {kanal_sayisi} kanal eklendi! Mevcut içeriğiniz korundu.")
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

if __name__ == "__main__":
    get_canli_tv_m3u()
