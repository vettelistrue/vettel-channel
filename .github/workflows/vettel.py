import re
import os

KANAL_ADLARI = {
    "Szc Tv": "3002",
    "Sinema Tv": "1908",
    "FX": "313131",
    "Now": "2213",
    "Tv 8,5":"1901",
    "Sinema Yerli": "3304",
    "Sinema Aile": "1911",
    "Sinema 1001": "2602",
    "Sinema Komedi": "1110",
    "Sinema Aksiyon": "1109",
    "Trt Çocuk": "2212",
    "Cnn Türk": "2813",
    "A Haber": "2402",
    "Minika Çocuk": "2608",
    "Minika Go": "2404",
    "Trt Diyanet Çocuk": "2703",
    "Spacetoon": "3715",
    "Azoomee": "1314",
    "Baby Tv": "2601",
    "Disney Junior": "3601",
    "Cartoon Network": "1608",
    "Duck Tv": "1610",
    "English Club": "2506",
    "Da Vinci": "2704",
    "LangLab": "3802",
    "LingoToons": "3803",
    "TinyTeen": "3801",
    "Kanal D": "3131",
    "Trt Eba TV": "1616",
    "Cnbc-e": "2003",
    "Ulusal Kanal": "2310",
    "beIN Sports Haber": "2114",
    "Nba Tv": "3903",
    "Eurosport 1": "2002",
    "Eurosport 2": "1809",
    "S Sport": "1810",
    "S Sport 2": "3901"
}

def parse_m3u(file_path):
    kanallar = {}
    mevcut_kanal_adi = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for satir in f:
            satir = satir.strip()
            if satir.startswith('#EXTINF'):
                eslesme = re.search(r',\s*(.*)$', satir)
                mevcut_kanal_adi = eslesme.group(1).strip() if eslesme else None
            elif satir and not satir.startswith('#') and mevcut_kanal_adi:
                kanallar[mevcut_kanal_adi] = satir
                mevcut_kanal_adi = None
    return kanallar

def update_kerim_m3u():
    yeni_kanallar = parse_m3u('vetteltv.m3u')
    hedef_dosya = 'vetteltv.m3u'

    if not os.path.exists(hedef_dosya):
        print("kerim.m3u bulunamadı. Yeni oluşturuluyor...")
        os.makedirs('Kanallar', exist_ok=True)
        with open(hedef_dosya, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")

    with open(hedef_dosya, 'r', encoding='utf-8') as f:
        satirlar = f.readlines()

    guncellenmis = []
    i = 0
    while i < len(satirlar):
        satir = satirlar[i].strip()
        guncellenmis.append(satirlar[i])

        if satir.startswith('#EXTINF'):
            eslesme = re.search(r',\s*(.*)$', satir)
            kanal_adi = eslesme.group(1).strip() if eslesme else None

            if kanal_adi in KANAL_ADLARI and i + 1 < len(satirlar):
                eski_url = satirlar[i + 1].strip()
                yeni_url = yeni_kanallar.get(kanal_adi)

                i += 1
                if yeni_url and eski_url != yeni_url:
                    print(f"🔁 {kanal_adi} güncellendi.")
                    guncellenmis.append(yeni_url + '\n')
                else:
                    guncellenmis.append(satirlar[i])
            elif i + 1 < len(satirlar):
                i += 1
                guncellenmis.append(satirlar[i])
        i += 1

    with open(hedef_dosya, 'w', encoding='utf-8') as f:
        f.writelines(guncellenmis)

    print("✅ kablo.m3u başarıyla güncellendi!")

if __name__ == "__main__":
    update_kerim_m3u()
