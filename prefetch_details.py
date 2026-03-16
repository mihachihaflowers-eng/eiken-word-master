#!/usr/bin/env python3
"""
一括詳細取得スクリプト
eiken.db 内の全単語について詳細情報を取得して word_details テーブルに保存します。
完了後はアプリがオフラインで詳細表示できるようになります。
"""

import sqlite3
import json
import urllib.request
import urllib.parse
import re
import time
from pathlib import Path

DB_PATH = Path(__file__).parent / "eiken.db"
DELAY   = 0.4   # API へのリクエスト間隔（秒）


def fetch_word_details(word: str) -> dict:
    result: dict = {}
    ua = {"User-Agent": "Mozilla/5.0"}

    # ── Google翻訳（品詞別の意味）──────────────────────────────
    params = urllib.parse.urlencode([
        ("client", "gtx"), ("sl", "en"), ("tl", "ja"),
        ("dt", "t"), ("dt", "bd"), ("q", word),
    ])
    url = f"https://translate.googleapis.com/translate_a/single?{params}"
    req = urllib.request.Request(url, headers=ua)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    if data[0]:
        result["translation"] = "".join(item[0] for item in data[0] if item[0])

    if len(data) > 1 and data[1]:
        pos_entries = []
        for item in data[1]:
            if len(item) >= 2 and item[1]:
                pos_entries.append({"pos": item[0], "words": list(item[1])[:6]})
        if pos_entries:
            result["pos_definitions"] = pos_entries

    time.sleep(DELAY)

    # ── Free Dictionary API（発音記号・例文）─────────────────────
    try:
        dict_url = (
            "https://api.dictionaryapi.dev/api/v2/entries/en/"
            + urllib.parse.quote(word.split()[0])
        )
        dict_req = urllib.request.Request(dict_url, headers=ua)
        with urllib.request.urlopen(dict_req, timeout=10) as dict_resp:
            dict_data = json.loads(dict_resp.read().decode("utf-8"))

        for entry in dict_data:
            for ph in entry.get("phonetics", []):
                text = ph.get("text", "").strip()
                if text:
                    result["phonetic"] = text
                    break
            if "phonetic" in result:
                break

        sentences: list[str] = []
        for entry in dict_data:
            for meaning in entry.get("meanings", []):
                for defn in meaning.get("definitions", []):
                    ex = defn.get("example", "")
                    if ex and ex not in sentences:
                        sentences.append(ex)
                    if len(sentences) >= 2:
                        break
                if len(sentences) >= 2:
                    break
            if len(sentences) >= 2:
                break
        if sentences:
            result["example_sentences"] = sentences

    except Exception:
        pass  # 辞書APIは任意のため失敗しても続行

    return result


def main():
    if not DB_PATH.exists():
        print(f"エラー: DBが見つかりません → {DB_PATH}")
        print("先にアプリを一度起動してDBを生成してください。")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # word_details テーブルがなければ作成
    conn.execute("""
        CREATE TABLE IF NOT EXISTS word_details (
            word_id     INTEGER PRIMARY KEY,
            details_json TEXT NOT NULL,
            fetched_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (word_id) REFERENCES words(id)
        )
    """)
    conn.commit()

    # 未取得の単語のみ対象
    rows = conn.execute("""
        SELECT w.id, w.word FROM words w
        LEFT JOIN word_details wd ON w.id = wd.word_id
        WHERE wd.word_id IS NULL
        ORDER BY w.level, w.batch_number, w.id
    """).fetchall()

    total     = len(rows)
    succeeded = 0
    failed    = 0

    if total == 0:
        print("全単語の詳細情報は既に取得済みです。")
        conn.close()
        return

    print(f"取得対象: {total} 件  （1件あたり約{DELAY*2:.1f}秒 × 2API）")
    print(f"推定時間: 約 {total * DELAY * 2 / 60:.0f} 分")
    print("-" * 50)

    for i, row in enumerate(rows, 1):
        word_id   = row["id"]
        word_text = row["word"]
        try:
            details = fetch_word_details(word_text)
            conn.execute(
                "INSERT OR REPLACE INTO word_details (word_id, details_json) VALUES (?,?)",
                (word_id, json.dumps(details, ensure_ascii=False)),
            )
            conn.commit()
            ph   = details.get("phonetic", "")
            info = f"  {ph}" if ph else ""
            print(f"[{i:3d}/{total}] OK {word_text}{info}")
            succeeded += 1
        except Exception as e:
            print(f"[{i:3d}/{total}] NG {word_text}  ({e})")
            failed += 1

        time.sleep(DELAY)

    conn.close()
    print("-" * 50)
    print(f"完了！  成功 {succeeded} 件 / 失敗 {failed} 件")
    if failed > 0:
        print("※ 失敗分は次回実行時に再取得されます。")


if __name__ == "__main__":
    main()
