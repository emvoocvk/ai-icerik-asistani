# AI İçerik Asistanı 🤖✍️

Sosyal medya içerik üretimini otomatikleştiren Python aracı. Bir marka için
haftalık Instagram içerik planını **Claude API** ile üretir, tüm planları
**SQLite** veritabanında saklar ve markdown olarak dışa aktarır.

> Gerçek bir ihtiyaçtan doğdu: yönettiğim markaların haftalık içerik üretim
> süreci elle ~8 saat sürüyordu. Bu otomasyonla aynı iş ~2 saate indi
> (üretim + insan onayı/düzenleme dahil).

## Özellikler

- 🎯 Marka ve sektöre özel, Türkçe içerik üretimi (başlık, caption, hashtag, görsel önerisi)
- 💾 Üretilen tüm planlar SQLite'ta saklanır — geçmişe dönüp bakabilirsin
- 📄 Tek komutla markdown dışa aktarma
- ⚡ Streaming çıktı — içerik üretilirken ekranda akar

## Kurulum

```bash
pip install -r requirements.txt
```

[Anthropic API anahtarını](https://platform.claude.com/) ortam değişkeni olarak tanımla:

```bash
# Windows (PowerShell)
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Linux / macOS
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Kullanım

```bash
# 7 günlük içerik planı üret
python main.py --marka "Kahve Durağı" --sektor "yiyecek-içecek" --adet 7

# Önceki planları listele
python main.py --gecmis

# 3 numaralı planı markdown olarak kaydet
python main.py --disa-aktar 3
```

## Teknolojiler

| Alan | Araç |
|---|---|
| Dil | Python 3.10+ |
| AI | Claude API (`claude-opus-4-8`, adaptive thinking) |
| Veritabanı | SQLite |
| Arayüz | CLI (argparse) |

## Lisans

MIT
