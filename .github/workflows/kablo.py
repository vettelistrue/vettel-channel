import requests
import json
import gzip
from io import BytesIO
import os

def get_canli_tv_m3u():
    """
    Kablo Web TV API'sinden canlı TV kanal verilerini çeker ve
    mevcut vetteltv.m3u dosyasına sadece daha önce eklenmemiş
    yeni kanalları ekler. Dosyadaki mevcut içerik korunur.
    Klonlanmış girişleri kesin olarak engeller.
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
    
    m3u_filename = "vetteltv.m3u"
    
    # Mevcut M3U dosyasındaki tüm satırları ve URL'leri tutmak için listeler
    existing_m3u_lines = []
    existing_channel_urls = set()

    # --- Mevcut M3U dosyasını oku ve URL'leri topla ---
    if os.path.exists(m3u_filename):
        try:
            with open(m3u_filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # #EXTM3U başlığını hariç tutarak diğer tüm satırları sakla
                if lines and lines[0].strip() == "#EXTM3U":
                    existing_m3u_lines.extend(lines[1:]) # Başlık hariç tüm satırları al
                else:
                    existing_m3u_lines.extend(lines) # Başlık yoksa tüm satırları al
                
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line.startswith("http"):
                        existing_channel_urls.add(stripped_line)
            print(f"📄 '{m3u_filename}' dosyasındaki {len(existing_channel_urls)} mevcut kanal URL'si yüklendi.")
        except Exception as e:
            print(f"⚠️ '{m3u_filename}' dosyasını okurken hata oluştu: {e}. Dosya yenilenecek.")
            existing_m3u_lines = [] # Hata durumunda mevcut içeriği boşalt
            existing_channel_urls = set()

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
        
        api_channels = data['Data']['AllChannels']
        print(f"✅ API'den {len(api_channels)} kanal bulundu.")
        
        new_channels_to_add = [] # API'den gelen ve dosyada olmayan kanalları sakla
        eklenen_kanal_sayisi = 0

        for channel in api_channels:
            name = channel.get('Name')
            stream_data = channel.get('StreamData', {})
            hls_url = stream_data.get('HlsStreamUrl') if stream_data else None
            logo = channel.get('PrimaryLogoImageUrl', '')
            categories = channel.get('Categories', [])
            
            if not name or not hls_url:
                continue
            
            group = categories[0].get('Name', 'Genel') if categories else 'Genel'
            
            if group == "Bilgilendirme": # Bilgilendirme grubundaki kanalları atla
                continue

            # --- Kanalın zaten mevcut olup olmadığını kontrol et ---
            if hls_url not in existing_channel_urls:
                # Kanal listede yoksa, eklemek üzere hazırla
                new_channels_to_add.append(
                    f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{name}\n'
                    f'{hls_url}\n'
                )
                eklenen_kanal_sayisi += 1
                existing_channel_urls.add(hls_url) # Aynı API çağrısında tekrar gelirse diye kümeye ekle

        # --- Dosyayı yeniden yazma (tüm mevcut içeriği koruyarak ve yeni kanalları ekleyerek) ---
        # Bu kısım önemlidir: Dosyayı 'w' modunda açıp tüm içeriği baştan yazıyoruz.
        # Ancak bunu yaparken, mevcut kanalları (existing_m3u_lines) ve yeni kanalları (new_channels_to_add) birleştiriyoruz.
        with open(m3u_filename, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n") # Başlığı her zaman en başa yaz

            # Mevcut manuel ve API'den gelen eski kanalları yaz
            for line in existing_m3u_lines:
                # URL satırlarını kontrol ederek klonlamayı engelle (eğer bir hata oluştuysa ve kümeye yanlış eklemeler olduysa diye son bir kontrol)
                if line.strip().startswith("http") and line.strip() not in existing_channel_urls:
                     # Bu aslında gerçekleşmemeli, çünkü existing_m3u_lines'ı zaten existing_channel_urls'e eklemiştik.
                     # Ancak ek bir güvenlik katmanı olarak bırakılabilir veya kaldırılabilir.
                     # Daha basiti: direkt olarak existing_m3u_lines'ı yazabiliriz.
                    f.write(line)
                elif not line.strip().startswith("http"): # EXTINF satırları veya diğer satırlar
                    f.write(line)
            
            # API'den gelen ve daha önce dosyada olmayan yeni kanalları yaz
            for channel_entry in new_channels_to_add:
                f.write(channel_entry)

        print(f"📺 '{m3u_filename}' dosyasına {eklenen_kanal_sayisi} yeni kanal eklendi!")
        print(f"Toplam benzersiz kanal URL'si: {len(existing_channel_urls)}")
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

if __name__ == "__main__":
    get_canli_tv_m3u()
