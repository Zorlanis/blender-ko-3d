<div align="center">

# Blender KO 3D

### Blender eklentisi · Python CLI · Unity ve yapay zekâ için N3 analiz verisi

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Blender](https://img.shields.io/badge/Blender-4.2%2B-E87D0D?style=flat-square&logo=blender&logoColor=white)
![Version](https://img.shields.io/badge/Version-1.1.0-2563EB?style=flat-square)
[![License](https://img.shields.io/badge/License-GPL--2.0--or--later-334155?style=flat-square)](LICENSE)

**Yapımcı ve geliştirici: Zorlanis**

</div>

---

Knight Online model dosyalarını Blender'a aktarın veya **Blender çalıştırmadan**
Python CLI ile JSON'a çözümleyin. Geometri, UV, materyal, iskelet, kemik ağırlıkları,
animasyon kayıtları ve dosya bağlantıları kaynaklarıyla birlikte dışa aktarılır.

Mevcut Blender eklentisi korunur. CLI kaynak client dosyalarına yazmaz; seçilen
çıktı klasöründe rapor üretir. Ek çalışma zamanı Python paketi gerektirmez.

## İki kullanım biçimi

| Blender eklentisi | Python CLI |
| --- | --- |
| Modeli sahneye alır; mesh, materyal, armature ve Action oluşturur. | Dosyayı okuyup kaynak uzayındaki veriyi ve bağlantıları JSON'a aktarır. |
| Blender 4.2+ gerekir. | Python 3.11+ yeterlidir; `bpy` import edilmez. |
| Blender için koordinat ve UV dönüşümü uygular. | Konum, normal, quaternion, matris ve UV'leri N3 kaynak değerleriyle korur. |

## Python CLI

Proje klasöründe:

```powershell
python -m blender_ko_3d
```

Terminal model dosyası veya klasörü sorar. Enter ile varsayılan client seçilir:
`C:\NTTGame\KnightOnlineEn`. Varsayılanı `KO_CLIENT_ROOT` ortam değişkeniyle veya
`--client-root` seçeneğiyle değiştirin.

Bir karakteri ve bağlı dosyalarını çözmek için:

```powershell
python -m blender_ko_3d "D:\Client\Chr\el_dong_gold.n3chr" --client-root "D:\Client" --compact
```

Client'in tamamını taramak için:

```powershell
python -m blender_ko_3d --client-root "D:\Client" --non-interactive --compact
```

Komut olarak kurmak için:

```powershell
python -m pip install .
ko-assets --help
```

Kaynak uzayındaki JSON bir Unity importer, FBX veya glTF çıktısı değildir.
Aktarım yapan yapay zekâ önce `outputs/AI_GUIDE.md` ve `migration_report.json`
dosyalarını okumalıdır. DXT ve mevcut PNG adaylarının yolları gösterilir;
CLI görüntü veya FXB dönüşümü yapmaz.

### Seçenekler

| Seçenek | İşlev |
| --- | --- |
| `input` | Tek desteklenen dosya veya taranacak klasör. |
| `--client-root DIR` | Dosya kimliklerinin ve bağımlılıkların client kökü. Giriş bu kökün içinde olmalıdır. |
| `-o DIR` | Çıktı yolu; varsayılan çalışma klasöründeki `outputs/`. |
| `--compact` | JSON boşluklarını azaltır. |
| `--overwrite` | Mevcut asset JSON'larını günceller. |
| `--encoding CODEC` | Dize kodlaması; varsayılan `auto`. Orijinal dize baytları korunur. |
| `--include-raw` | Kaynak dosyanın tamamını JSON'a base64 olarak ekler. |
| `--no-follow-dependencies` | Referans verilen model dosyalarını ayrıca kuyruğa eklemez. |
| `--extensions LIST` | İlk dosya seçimini filtreler; örnek `n3chr,n3shape`. |
| `--limit N` | En fazla N dosya işler. Tamamlanmayan tarama `scan_complete: false` olur. |
| `--strict-assets` | Eksik veya belirsiz kaynak varsa çıkış kodunu 1 yapar. |
| `--non-interactive` | Kullanıcı girişi beklemez. |
| `--json` / `--quiet` | NDJSON olayları / yalnızca hata ve sonuçlar. |

Bağımlılık takibi varsayılan olarak açıktır. Başlangıç dosyası az olsa bile
başka klasörlerdeki bağlı modeller sıraya eklenebilir; terminalde toplam sayı
güncellenir. Uzantı filtresi ilk seçimi etkiler, bağlı dosyaların türünü sınırlamaz.

Mevcut JSON kaynak SHA-256'sı, sürüm, kodlama ve kaynak eşleşmeleriyle güncel
değilse `--overwrite` gerekir. Her tarama sonunda toplu raporlar yenilenir;
önceki çalışmalardan kalan JSON'lar için son manifestteki durumu kontrol edin.

### Çıktı düzeni

```text
outputs/
├── AI_GUIDE.md
├── manifest.json
├── migration_report.json
├── dependency_index.json
├── unresolved_dependencies.json
├── texture_index.json
├── geometry_index.json
├── animation_index.json
├── character_index.json
├── asset_inventory.json
└── assets/
    ├── Chr/el_dong_gold.n3chr.json
    ├── Chr/el_dong_gold.n3joint.json
    └── Item/part.n3cpart.json
```

Orijinal uzantı çıktı adında korunur; aynı isimli iskelet ve animasyon dosyaları
birbirinin üzerine yazılmaz. `dependency_index.json` kaynakların ters kullanımını,
`character_index.json` karakterin bağlı dosyalarını gösterir. Her asset belgesi
kaynak hash'ini, ayrıntılı veriyi, referansları, okuma kapsamını ve uyarıları içerir.

## Desteklenen biçimler

| Biçim | Veri | Blender | CLI |
| --- | --- | --- | --- |
| `.n3chr` | Karakter, iskelet/part/plug/animasyon bağlantıları | Evet | Evet |
| `.n3shape` | Statik sahne nesnesi, parçalar ve materyaller | Evet | Evet |
| `.n3pmesh` | Geometri, indeksler ve LOD verileri | Evet | Evet |
| `.n3cpart` | Materyal, doku ve skinned mesh referansları | Evet | Evet |
| `.n3cplug` | Kemik eki, iz parametreleri ve gömülü PMesh | Evet | Evet |
| `.n3joint` | İskelet ve animasyon kanalları | Evet | Evet |
| `.n3anim` | Klipler, kare aralıkları ve olay işaretçileri | Evet | Evet |
| `.n3cskins` / `.n3cskin` | LOD'lar ve kemik ağırlıkları | Part üzerinden | Evet |
| `.n3vmesh` | Çarpışma geometrisi | Referans olarak | Evet |
| `.n3fxplug` | Efekt dosyası, joint referansı ve offset verileri | Referans olarak | Evet |

Animasyonlarda eski düz kayıtlar ve tanınan DES çerçeveli kayıtlar desteklenir.
İskelet okuyucusu orientation kanalı bulunan/bulunmayan düzenleri tam tüketimle
ayırt eder. Bir `.n3anim` dosyası gerçekte INI metniyse animasyon diye sunulmaz;
gerçek içerik ve uzantı uyuşmazlığı kaydedilir.

## Blender eklentisi

ZIP üretin:

```powershell
python build_zip.py
```

Blender'da **Edit → Preferences → Extensions → Install from Disk** yoluyla
`blender-ko-3d.zip` dosyasını kurup **Blender KO 3D** eklentisini etkinleştirin.
Ardından **File → Import → KnightOnline Assets** menüsünü kullanın.

LOD, ölçek, doku/animasyonları atlama ve ışık ekleme seçenekleri korunur.
Tam karakter içe aktarımı iskelet, skinned parçalar, ekipman ve animasyonları
bir koleksiyonda birleştirir. Statik mesh'ler UV ve materyalleriyle oluşturulur.

Doku okuyucusu DXT1–DXT5, desteklenen ham renk biçimleri ve TGA'yı açar.
DXT2/4 premultiplied alpha düzeltilir; NTF7 RC4/SHA-1 katmanı desteklenir.
Blender için üst görüntü çözülür; ek kaynak mip/yardımcı baytları korunur.
CLI görsel dosya üretmez.

## Otomasyon ve kapsam

```powershell
ko-assets --client-root "D:\Client" --non-interactive --compact --overwrite --json
```

Olaylar `schema_version: 1` içerir: `indexing`, `found`, `file`, `error`,
`summary`, `cancelled`. Çıkış kodları: **0** tamamlandı, **1** dosya/ayrıştırma
hatası veya strict kaynak hatası, **2** geçersiz seçenek, **130** kullanıcı iptali.
Diğer dosyalar bir dosya hatasından sonra işlenmeye devam eder.

- Tam dosya okuması, bütün alanların oyun içindeki anlamının bilindiğini kanıtlamaz.
- Tanınmayan ek değerler ve özgün baytları korunur; çalışma anı rolleri tahmin edilmez.
- NaN/Infinity kaynak değerleri CLI JSON'unda ham float32 baytlarıyla temsil edilir;
  geçerli sayı uydurulmaz. Bu kaynak veriler ayrıca uyarı üretir.
- Eksik dosyalar oluşturulmaz; birden fazla olası kaynakta rastgele seçim yapılmaz.
- `--include-raw` kullanılmazsa aktarım için orijinal client'e erişim gerekir.
- Byte round-trip, bütün client sürümleri ve Unity'de birebir görüntü eşitliği garanti edilmez.

CLI veri şeması ve sınırlar: [FORMAT.md](FORMAT.md).

## Lisans

**Geliştirme: Zorlanis.** Bu dağıtım **GPL-2.0-or-later** olarak sunulur.
[LICENSE](LICENSE).

Üçüncü taraf lisans bildirimleri:
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
