"""AI İçerik Asistanı — sosyal medya içerik üretim otomasyonu.

Bir marka için haftalık sosyal medya içerik planını Claude API ile üretir,
sonuçları SQLite veritabanına kaydeder ve markdown olarak dışa aktarır.

Kullanım:
    python main.py --marka "Kahve Dükkanı" --sektor "yiyecek-içecek" --adet 7
    python main.py --gecmis          # önceki üretimleri listele
    python main.py --disa-aktar 3    # 3 numaralı planı markdown olarak kaydet
"""

import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import anthropic

DB_PATH = Path(__file__).parent / "icerikler.db"

SISTEM_PROMPT = """Sen deneyimli bir sosyal medya içerik üreticisisin.
Verilen marka ve sektör için özgün, etkileşim odaklı Instagram içerikleri üretirsin.
Her içerik için şunları yazarsın: gönderi başlığı, açıklama metni (caption),
5 adet hashtag ve görsel önerisi. Türkçe yazarsın, marka diline uygun,
klişelerden uzak ve samimi bir ton kullanırsın."""


def veritabani_hazirla() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS planlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marka TEXT NOT NULL,
            sektor TEXT NOT NULL,
            adet INTEGER NOT NULL,
            icerik TEXT NOT NULL,
            olusturma_tarihi TEXT NOT NULL
        )
    """)
    return conn


def icerik_uret(marka: str, sektor: str, adet: int) -> str:
    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY ortam değişkeninden okunur
    istek = (
        f"Marka: {marka}\nSektör: {sektor}\n"
        f"{adet} günlük Instagram içerik planı hazırla. "
        f"Her gün için ayrı içerik, numaralandırılmış olsun."
    )
    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=SISTEM_PROMPT,
        messages=[{"role": "user", "content": istek}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        yanit = stream.get_final_message()
    print()
    return next(b.text for b in yanit.content if b.type == "text")


def plan_kaydet(conn: sqlite3.Connection, marka: str, sektor: str, adet: int, icerik: str) -> int:
    imlec = conn.execute(
        "INSERT INTO planlar (marka, sektor, adet, icerik, olusturma_tarihi) VALUES (?, ?, ?, ?, ?)",
        (marka, sektor, adet, icerik, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    return imlec.lastrowid


def gecmisi_listele(conn: sqlite3.Connection) -> None:
    satirlar = conn.execute(
        "SELECT id, marka, sektor, adet, olusturma_tarihi FROM planlar ORDER BY id DESC"
    ).fetchall()
    if not satirlar:
        print("Henüz kayıtlı plan yok.")
        return
    for pid, marka, sektor, adet, tarih in satirlar:
        print(f"[{pid}] {marka} ({sektor}) — {adet} içerik — {tarih}")


def disa_aktar(conn: sqlite3.Connection, plan_id: int) -> None:
    satir = conn.execute(
        "SELECT marka, icerik FROM planlar WHERE id = ?", (plan_id,)
    ).fetchone()
    if satir is None:
        sys.exit(f"Plan bulunamadı: {plan_id}")
    marka, icerik = satir
    dosya = Path(f"plan-{plan_id}-{marka.lower().replace(' ', '-')}.md")
    dosya.write_text(f"# {marka} — İçerik Planı\n\n{icerik}\n", encoding="utf-8")
    print(f"Kaydedildi: {dosya}")


def main() -> None:
    parser = argparse.ArgumentParser(description="AI destekli sosyal medya içerik üretimi")
    parser.add_argument("--marka", help="Marka adı")
    parser.add_argument("--sektor", default="genel", help="Markanın sektörü")
    parser.add_argument("--adet", type=int, default=7, help="Üretilecek içerik sayısı")
    parser.add_argument("--gecmis", action="store_true", help="Önceki planları listele")
    parser.add_argument("--disa-aktar", type=int, metavar="ID", help="Planı markdown olarak kaydet")
    args = parser.parse_args()

    conn = veritabani_hazirla()
    try:
        if args.gecmis:
            gecmisi_listele(conn)
        elif args.disa_aktar is not None:
            disa_aktar(conn, args.disa_aktar)
        elif args.marka:
            icerik = icerik_uret(args.marka, args.sektor, args.adet)
            plan_id = plan_kaydet(conn, args.marka, args.sektor, args.adet, icerik)
            print(f"\nPlan #{plan_id} veritabanına kaydedildi.")
        else:
            parser.print_help()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
