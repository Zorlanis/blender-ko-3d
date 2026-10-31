# Blender KO 3D CLI veri biçimi

`analysis_version: 1.1.0` · `schema_version: 1`

Bu belge Blender eklentisinden bağımsız JSON analizini açıklar. `python -m
blender_ko_3d` ve `ko-assets` aynı CLI girişini kullanır. `bpy` yalnızca Blender
modunda yüklenir. Oyun dosyaları bu depoya veya kuruluma dahil değildir.

## Dosya kimlikleri ve okuma

Asset kimliği client köküne göre yolun casefold edilmiş biçimidir. JSON dosya
adı orijinal uzantıyı da korur: `assets/Chr/character.n3chr.json`.

- Kaynak dosya limiti 256 MiB, tek dize limiti 1 MiB'dir.
- Sayısal veriler little-endian'dır. Sabit boyutlu okuma ve skip sınırları kontrol edilir.
- Negatif sayılar geçerli değer olarak korunur; negatif eleman sayıları reddedilir.
- Dizeler `int32 byte_length + bytes` olarak okunur. Auto kodlaması ASCII,
  UTF-8, CP949, CP950 ve CP1254 sırasını dener; dil kesinliği iddia etmez.
- Bilinen optional alanlarda `-1` uzunluk sentinel'i ayrı ham kayıtla korunur.
- Dize metadata'sında uzunluk alanının dosya konumu, codec ve orijinal hex bulunur.
- NaN/Infinity float32 değerleri `raw_float32_hex` / `classification` nesnesine
  çevrilir; özgün bit deseni korunur. Kaynak kusuru geçerli sayıya dönüştürülmez.

CLI yalnızca bir asset'in kendi alanlarını okur. Bağlı dosyalar ayrı kayıtlar
olarak tarama kuyruğuna eklenir. Tek bir eksik referans diğer dosyaların verisini
silmez. Symlink/reparse point'ler takip edilmez ve seçilen çıktı ağacı taranmaz.

## Asset JSON alanları

| Alan | İçerik |
| --- | --- |
| `source` | Göreli/tam yol, kaynak boyutu ve SHA-256. |
| `format` | Uzantı, dize kodlaması ve koordinat/UV kuralları. |
| `summary` | Vertex/triangle/skin/joint/clip sayıları ve yerel geometri sınırları. |
| `data` | Tipin tüm dışa aktarılan alanları; aşağıdaki tip notlarına bakın. |
| `resources` | Kaynak alanı, orijinal referans, eşleşme durumu, gerçek dosya ve yöntem. |
| `binary` | Okuma kapsamı, dizelerin ham baytları, atlanan bölgeler ve sonda kalan veri. |
| `warnings` | Kaynak kusurları, yorumlanmamış alanlar ve eşleşme sorunları. |

`binary.complete_consumption`, cursor'un dosya sonuna ulaştığını belirtir;
`byte_roundtrip_verified` ayrı bir alan olup şu sürümde `false` kalır. Bu kontroller
oyun davranışı veya alan anlamı doğrulaması değildir. `--include-raw`, orijinal
şifreli/düz kaynak dosyayı `source_base64` alanıyla ekler.

## Geometri, iskelet ve materyaller

CLI konum ve normalleri N3 kaynak uzayında, quaternion'ları `(x,y,z,w)`, matrisleri
kaynak satır sırasıyla korur. V değeri çevrilmez. Blender okuyucusu ise mevcut
`v = 1-v` ve koordinat dönüşümünü korur. CLI verisine Blender dönüşümü uygulanmış
varsayımıyla ikinci kez dönüşüm uygulanmamalıdır.

`n3pmesh` vertex'leri position, normal ve UV taşır. İndeksler unsigned uint16'dır.
LOD çökertme kayıtları 24 baytlık opak blok olarak; indeks değişimleri ve LOD
kontrol değerleri ayrıca korunur. CLI yalnızca en yüksek LOD'yi dışa aktarmaz;
LOD geçişi için kaynak kayıtları da taşır. Blender'ın görünür mesh oluşturması
en yüksek vertex/indeks kümesini kullanır.

`n3cskins`, `name` ve `lods` alanlarıyla kapsayıcı adını, dört LOD slotunu ve boş
slotların alanlarını korur. Her skin; vertex,
face/UV indeksleri, UV'ler, skin origin, joint indeksleri ve ağırlıklar içerir.
Tek influence için ağırlık kaynak kuralıyla 1.0 olarak türetilir; serialized pointer
sayıları opak değer olarak korunur. Skinned mesh'lerde tüm LOD'ların vertex sayısı
özetlendiğinden bu sayı tek sahnede görünen vertex sayısı değildir.

Materyal kaydı **92 bayttır**: dört float RGBA renk, power float ve altı uint32
(color operation/arguments, render flags, source/destination blend). Ham değerler
Unity shader karşılıkları varsayılmadan dışa aktarılır.

`n3chr` transform anahtarlarını, collision/climb, joint, part, plug, animasyon,
FX plug, collision skin referanslarını ve gövde animasyon aralıklarını korur.
Gözlenen bazı varyantlar CPlug düzeninde gömülü ek kayıt taşır. Bu kayıtlar
ayrıştırılır; karakter üzerindeki runtime kullanım rolü doğrulanmış sayılmaz.

`n3cplug`, trace alanlarını ve `use_vmesh` ile gelen gömülü **CN3PMesh**'i korur.
Bu bayrağın adı gömülü kaydın CN3VMesh olduğu anlamına gelmez. Bazı varyantlardaki
version/altı dize ek düzeni gözlenen tam tüketimle okunur; alan işlevleri belirsizdir.
Kaynak isimleri ve ham baytlar üzerinden tüketici incelemesi gerekir.

`n3vmesh` çarpışma vertex ve unsigned indekslerini verir. `n3fxplug`, FXB yolu,
joint referans indeksi, yerel pos/dir offset'leri ve varsa iki ek opak alanı korur.
FXB efektine veya Unity ParticleSystem'e dönüşüm yapılmaz.

## Animasyonlar ve şifreli kayıtlar

`n3joint` iki düzeni dener: orient kanalı bulunan ve eski orient kanalsız düzen.
Yalnızca tüm iskeleti tüketen profil kabul edilir. Hiyerarşi ve dört anahtar kanalı
varsa korunur. `AnimKey.data`, kaynak `count` kadar örnek taşır; Blender
interpolasyonu için çoğaltılan son örnek JSON'a yazılmaz.
Her kemikteki `joint_index_preorder` ve `parent_joint_index_preorder`, kökten
başlayan derinlik öncelikli sırayı verir; skin joint indeksleriyle eşleştirmeyi
kolaylaştırır. Oyun sürümüne özgü runtime kemik davranışını doğrulamaz.

`n3anim`, eski düz kayıtları ve kayıt uzunluğu + 16 bayt magic/boyut çerçeveli
şifreli kayıtları okur. Tanınan modified DES katmanı çözülür. TBL'ye özgü ikinci
LCG katmanı animasyona uygulanmaz. Şifre çözümü sonrası prefix adayları
(0/2/4 bayt) tam kayıt tüketimiyle denenir; birden fazla geçerli profil varsa
belirsiz sonuç kabul edilmez. Her şifreli clip kendi kaynak konumunu, prefix ve
plaintext hex'ini, çözülmüş dize konumlarını taşır. Prefix işlevi varsayılmaz.

`reserved`, frame start/end/FPS, trace/sound/strike frame marker'ları, blend time,
blend flags ve isim korunur. Frame marker, hangi sesin oynatıldığını veya oyun
kodundaki olay işlevini tek başına kanıtlamaz. Gerçekte INI metni olan bir
`.n3anim` dosyası `container_type` ile farklı sınıflandırılır; metni korunur.

## Görseller

CLI doku dosyasının kaynak yolunu, NTF/DDS/PNG başlık bilgisini ve mevcut PNG
adaylarını verir. Aynalanmış PNG yolu içerik eşitliği kanıtı değildir;
`pixel_equivalence_verified: false` korunur. Aynı dizine taşınmış kaynaklar
`same_directory_basename_rebase` yöntemiyle raporlanır; orijinal referans kaybolmaz.

Blender doku okuyucusu DXT1–DXT5, ham 24/32/16 bit biçimler ve TGA'nın üst
kaynak görüntüsünü çözer. DXT3 explicit alpha, DXT5 interpolated alpha olarak
ayrı işlenir; DXT2/4 RGB'si straight alpha'ya çevrilir. NTF7, SHA-1'den türetilen
16 bayt anahtarla RC4 çözümü kullanır; ham scanline'larda akış satır başında
sıfırlanır. Kaynak ek mip/yardımcı verileri `extra_data` içinde korunur. Üst
mip dışındaki görüntüler çözülmüş gibi sunulmaz.

## Toplu raporlar

`manifest` son taramanın dosya durumlarını ve kısmi olup olmadığını gösterir.
`dependency_index`, `texture_index`, `character_index`, `geometry_index` ve
`animation_index` ilişkilerde gezinmek içindir. `asset_inventory` hiçbir dosyayı
kullanılmıyor diye elemez. `migration_report.ready_for_identical_Unity_import`
gerçek Unity/client karşılaştırması yapılmadan `true` olmaz. Kaynakta olmayan
bağımlılıklar, yeni sürüm anlamları, shader ve skin/bind eşitliği uydurulmaz.

Lisans bildirimleri: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
