#!/usr/bin/env python3
"""英検単語マスター - 英検2級・準1級 単語学習アプリ"""

import customtkinter as ctk
import sqlite3
import json
import random
import re
import sys
import threading
import urllib.request
import urllib.parse
from datetime import date
from pathlib import Path

# PyInstaller exe では __file__ が一時展開フォルダを指すため sys.executable を使う
if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).parent
else:
    APP_DIR = Path(__file__).parent

DB_PATH = APP_DIR / "eiken.db"
MD_PATH = APP_DIR / "eiken_vocabulary.md"

LEVELS = ["2級", "準1級"]
MAX_BATCHES = 4
SESSION_SIZE = 10
MASTERY_STREAK = 2

# ============================================================
# Database
# ============================================================

class Database:
    def __init__(self, path: Path):
        self.path = path

    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self):
        with self.connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS words (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    word        TEXT    NOT NULL,
                    meanings    TEXT    NOT NULL,
                    level       TEXT    NOT NULL,
                    batch_number INTEGER NOT NULL,
                    word_type   TEXT    NOT NULL DEFAULT 'word'
                );
                CREATE TABLE IF NOT EXISTS progress (
                    word_id        INTEGER PRIMARY KEY,
                    correct_count  INTEGER NOT NULL DEFAULT 0,
                    incorrect_count INTEGER NOT NULL DEFAULT 0,
                    streak         INTEGER NOT NULL DEFAULT 0,
                    is_mastered    INTEGER NOT NULL DEFAULT 0,
                    mastered_date  TEXT    DEFAULT NULL,
                    FOREIGN KEY (word_id) REFERENCES words(id)
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    level           TEXT    NOT NULL,
                    batch_number    INTEGER NOT NULL,
                    mode            TEXT    NOT NULL,
                    drill_threshold INTEGER NOT NULL DEFAULT 0,
                    current_question INTEGER NOT NULL DEFAULT 0,
                    word_ids        TEXT    NOT NULL DEFAULT '[]',
                    answers         TEXT    NOT NULL DEFAULT '[]',
                    is_completed    INTEGER NOT NULL DEFAULT 0,
                    created_at      TEXT    DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS app_state (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS word_details (
                    word_id     INTEGER PRIMARY KEY,
                    details_json TEXT NOT NULL,
                    fetched_at  TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (word_id) REFERENCES words(id)
                );
            """)

    def is_populated(self) -> bool:
        with self.connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM words").fetchone()[0] > 0

    def insert_words(self, words: list):
        with self.connect() as conn:
            conn.executemany(
                "INSERT INTO words (word, meanings, level, batch_number, word_type) VALUES (?,?,?,?,?)",
                [(w["word"], json.dumps(w["meanings"], ensure_ascii=False),
                  w["level"], w["batch"], w["type"]) for w in words],
            )
            # Bug4修正: 新規挿入分のみ progress 行を作成（全件取得の無駄と二重登録を回避）
            conn.execute(
                "INSERT OR IGNORE INTO progress (word_id) SELECT id FROM words"
            )

    # --- State ---
    def get_state(self, key: str, default=None):
        with self.connect() as conn:
            row = conn.execute("SELECT value FROM app_state WHERE key=?", (key,)).fetchone()
            return json.loads(row[0]) if row else default

    def set_state(self, key: str, value):
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO app_state (key, value) VALUES (?,?)",
                (key, json.dumps(value, ensure_ascii=False)),
            )

    # --- Progress queries ---
    def get_batch_progress(self, level: str, batch: int):
        """Returns (total, mastered)."""
        with self.connect() as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM words WHERE level=? AND batch_number=?",
                (level, batch),
            ).fetchone()[0]
            mastered = conn.execute(
                "SELECT COUNT(*) FROM words w JOIN progress p ON w.id=p.word_id "
                "WHERE w.level=? AND w.batch_number=? AND p.is_mastered=1",
                (level, batch),
            ).fetchone()[0]
            return total, mastered

    def get_unmastered_for_batch(self, level: str, batch: int) -> list:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT w.id, w.word, w.meanings, w.word_type, p.streak, p.incorrect_count "
                "FROM words w JOIN progress p ON w.id=p.word_id "
                "WHERE w.level=? AND w.batch_number=? AND p.is_mastered=0",
                (level, batch),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_drill_words(self, level: str, threshold: int) -> list:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT w.id, w.word, w.meanings, w.word_type, p.streak, p.incorrect_count "
                "FROM words w JOIN progress p ON w.id=p.word_id "
                "WHERE w.level=? AND p.incorrect_count>=? AND p.is_mastered=0",
                (level, threshold),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_word(self, word_id: int) -> dict:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM words WHERE id=?", (word_id,)
            ).fetchone()
            return dict(row) if row else {}

    def get_all_meanings_for_level(self, level: str) -> dict:
        """word_id -> list[str]  (for distractor generation)"""
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT id, meanings FROM words WHERE level=?", (level,)
            ).fetchall()
            return {r["id"]: json.loads(r["meanings"]) for r in rows}

    def record_answer(self, word_id: int, is_correct: bool):
        today = date.today().isoformat()
        with self.connect() as conn:
            if is_correct:
                conn.execute(
                    """UPDATE progress SET
                        correct_count  = correct_count + 1,
                        streak         = streak + 1,
                        is_mastered    = CASE WHEN streak + 1 >= ? THEN 1 ELSE is_mastered END,
                        mastered_date  = CASE WHEN streak + 1 >= ? AND is_mastered = 0
                                              THEN ? ELSE mastered_date END
                    WHERE word_id=?""",
                    (MASTERY_STREAK, MASTERY_STREAK, today, word_id),
                )
            else:
                conn.execute(
                    "UPDATE progress SET incorrect_count=incorrect_count+1, streak=0 WHERE word_id=?",
                    (word_id,),
                )

    def get_mastered_words(self, level: str) -> list:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT w.id, w.word, w.meanings, w.batch_number, p.incorrect_count, p.mastered_date "
                "FROM words w JOIN progress p ON w.id=p.word_id "
                "WHERE w.level=? AND p.is_mastered=1 ORDER BY p.mastered_date DESC",
                (level,),
            ).fetchall()
            return [dict(r) for r in rows]

    def unmaster_word(self, word_id: int):
        """習得済みを解除して苦手単語リストへ移動する。"""
        with self.connect() as conn:
            conn.execute(
                """UPDATE progress SET
                    is_mastered    = 0,
                    mastered_date  = NULL,
                    streak         = 0,
                    incorrect_count = CASE WHEN incorrect_count < 1 THEN 1 ELSE incorrect_count END
                WHERE word_id=?""",
                (word_id,),
            )

    def get_word_details(self, word_id: int) -> dict | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT details_json FROM word_details WHERE word_id=?", (word_id,)
            ).fetchone()
            return json.loads(row["details_json"]) if row else None

    def save_word_details(self, word_id: int, details: dict):
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO word_details (word_id, details_json) VALUES (?,?)",
                (word_id, json.dumps(details, ensure_ascii=False)),
            )

    def delete_word_details(self, word_id: int):
        with self.connect() as conn:
            conn.execute("DELETE FROM word_details WHERE word_id=?", (word_id,))

    def get_weak_words(self, level: str) -> list:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT w.id, w.word, w.meanings, w.batch_number, p.incorrect_count, p.streak "
                "FROM words w JOIN progress p ON w.id=p.word_id "
                "WHERE w.level=? AND p.incorrect_count>0 AND p.is_mastered=0 "
                "ORDER BY p.incorrect_count DESC",
                (level,),
            ).fetchall()
            return [dict(r) for r in rows]

    # --- Session management ---
    def get_active_session(self, level: str, batch: int, mode: str) -> dict | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE level=? AND batch_number=? AND mode=? "
                "AND is_completed=0 ORDER BY id DESC LIMIT 1",
                (level, batch, mode),
            ).fetchone()
            return dict(row) if row else None

    def has_any_active_session(self, level: str) -> bool:
        with self.connect() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM sessions WHERE level=? AND is_completed=0",
                (level,),
            ).fetchone()[0]
            return count > 0

    def create_session(self, level: str, batch: int, mode: str,
                       word_ids: list, drill_threshold: int = 0) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                "INSERT INTO sessions (level, batch_number, mode, drill_threshold, word_ids) "
                "VALUES (?,?,?,?,?)",
                (level, batch, mode, drill_threshold, json.dumps(word_ids)),
            )
            return cur.lastrowid

    def update_session(self, session_id: int, current_q: int, answers: list):
        with self.connect() as conn:
            conn.execute(
                "UPDATE sessions SET current_question=?, answers=? WHERE id=?",
                (current_q, json.dumps(answers), session_id),
            )

    def complete_session(self, session_id: int):
        with self.connect() as conn:
            conn.execute("UPDATE sessions SET is_completed=1 WHERE id=?", (session_id,))


# ============================================================
# Google Translate detail fetcher
# ============================================================

def fetch_word_details(word: str) -> dict:
    """Google翻訳の非公式APIから単語の詳細情報を取得する（urllib標準ライブラリ使用）。"""
    params = urllib.parse.urlencode([
        ("client", "gtx"), ("sl", "en"), ("tl", "ja"),
        ("dt", "t"), ("dt", "bd"), ("dt", "ex"), ("q", word),
    ])
    url = f"https://translate.googleapis.com/translate_a/single?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    result: dict = {}

    # メイン翻訳
    if data[0]:
        result["translation"] = "".join(item[0] for item in data[0] if item[0])

    # 品詞別の意味
    if len(data) > 1 and data[1]:
        pos_entries = []
        for item in data[1]:
            if len(item) >= 2 and item[1]:
                pos_entries.append({"pos": item[0], "words": list(item[1])[:6]})
        if pos_entries:
            result["pos_definitions"] = pos_entries

    # 用例（HTMLタグを除去）
    if len(data) > 5 and data[5]:
        examples = []
        for ex_group in data[5]:
            if ex_group and len(ex_group) > 1:
                for ex in ex_group[1][:2]:
                    if ex and ex[0]:
                        examples.append(re.sub(r"<[^>]+>", "", ex[0]))
            if len(examples) >= 4:
                break
        if examples:
            result["examples"] = examples

    return result


def open_detail_popup(parent, word: str, word_id: int, db, colors: dict):
    """単語詳細ポップアップを開く共通関数。"""
    C_BG      = colors["C_BG"]
    C_TEXT    = colors["C_TEXT"]
    C_PRIMARY = colors["C_PRIMARY"]
    C_PRIMARY_H = colors["C_PRIMARY_H"]
    C_MUTED   = colors["C_MUTED"]
    C_DANGER  = colors["C_DANGER"]

    def _render(details: dict):
        for w in scroll.winfo_children():
            w.destroy()
        ctk.CTkLabel(scroll, text=word,
                     font=ctk.CTkFont("Yu Gothic UI", 22, "bold"),
                     text_color=C_TEXT).pack(anchor="w")
        if "translation" in details:
            ctk.CTkLabel(scroll, text=f"翻訳：{details['translation']}",
                         font=ctk.CTkFont("Yu Gothic UI", 14),
                         text_color=C_PRIMARY).pack(anchor="w", pady=(8, 0))
        if "pos_definitions" in details:
            ctk.CTkLabel(scroll, text="品詞別の意味",
                         font=ctk.CTkFont("Yu Gothic UI", 13, "bold"),
                         text_color=C_TEXT).pack(anchor="w", pady=(12, 4))
            for entry in details["pos_definitions"]:
                txt = f"【{entry['pos']}】 " + "、".join(entry["words"])
                ctk.CTkLabel(scroll, text=txt,
                             font=ctk.CTkFont("Yu Gothic UI", 13),
                             text_color=C_TEXT, wraplength=460, justify="left"
                             ).pack(anchor="w", pady=2)
        if "examples" in details:
            ctk.CTkLabel(scroll, text="用例",
                         font=ctk.CTkFont("Yu Gothic UI", 13, "bold"),
                         text_color=C_TEXT).pack(anchor="w", pady=(12, 4))
            for ex in details["examples"]:
                ctk.CTkLabel(scroll, text=f"• {ex}",
                             font=ctk.CTkFont("Yu Gothic UI", 12),
                             text_color=C_MUTED, wraplength=460, justify="left"
                             ).pack(anchor="w", pady=2)

    def _delete():
        db.delete_word_details(word_id)
        popup.destroy()

    popup = ctk.CTkToplevel(parent)
    popup.title(f"詳細情報：{word}")
    popup.geometry("540x500")
    popup.grab_set()

    scroll = ctk.CTkScrollableFrame(popup, fg_color=C_BG)
    scroll.pack(fill="both", expand=True, padx=16, pady=(16, 8))

    btn_row = ctk.CTkFrame(popup, fg_color="transparent")
    btn_row.pack(fill="x", padx=16, pady=(0, 12))
    btn_row.columnconfigure(0, weight=1)
    btn_row.columnconfigure(1, weight=1)

    ctk.CTkButton(btn_row, text="この詳細情報を削除", height=36, corner_radius=8,
                  font=ctk.CTkFont("Yu Gothic UI", 13),
                  fg_color="#fff0f0", hover_color="#ffd5d5",
                  text_color=C_DANGER, border_width=1, border_color="#ffbbbb",
                  command=_delete).grid(row=0, column=0, sticky="ew", padx=(0, 6))
    ctk.CTkButton(btn_row, text="閉じる", height=36, corner_radius=8,
                  font=ctk.CTkFont("Yu Gothic UI", 13),
                  fg_color=C_PRIMARY, hover_color=C_PRIMARY_H,
                  command=popup.destroy).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    # キャッシュ確認 → なければフェッチ
    cached = db.get_word_details(word_id)
    if cached:
        _render(cached)
        return

    status_lbl = ctk.CTkLabel(scroll, text="Google翻訳から情報を取得中...",
                              font=ctk.CTkFont("Yu Gothic UI", 14),
                              text_color=C_MUTED)
    status_lbl.pack(pady=40)

    def _fetch():
        try:
            details = fetch_word_details(word)
            db.save_word_details(word_id, details)
            popup.after(0, lambda: _render(details))
        except Exception as e:
            popup.after(0, lambda: status_lbl.configure(
                text=f"取得に失敗しました。\nネットワーク接続を確認してください。\n({e})",
                text_color=C_DANGER))

    threading.Thread(target=_fetch, daemon=True).start()


# ============================================================
# Markdown Parser
# ============================================================

def parse_vocabulary_md(filepath: Path) -> list:
    """
    Parse eiken_vocabulary.md.
    Returns list of dicts: {word, meanings, level, batch, type}
    Batch assigned sequentially per level: every 100 words = next batch (max 4).
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    all_words: dict[str, list] = {"2級": [], "準1級": []}

    # Split on level-2 headings
    sections = re.split(r"(?m)^## ", content)

    for section in sections:
        if not section.strip():
            continue
        first_line = section.split("\n")[0].strip()

        if "英検準1級" in first_line:
            level = "準1級"
        elif "英検2級" in first_line:
            level = "2級"
        else:
            continue

        word_type = "phrase" if "連語" in first_line else "word"

        # Match table data rows: | number | word/phrase | meaning |
        rows = re.findall(
            r"^\|\s*\d+\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|",
            section,
            re.MULTILINE,
        )
        for word_text, meaning_text in rows:
            word_text = word_text.strip()
            meaning_text = meaning_text.strip()
            # Skip column headers
            if word_text in ("単語", "連語", "---", "word", "phrase"):
                continue
            # Split multiple meanings on ・ or 、
            meanings = [m.strip() for m in re.split(r"[・、]", meaning_text) if m.strip()]
            if not meanings:
                meanings = [meaning_text]
            all_words[level].append(
                {"word": word_text, "meanings": meanings[:3], "level": level, "type": word_type}
            )

    result = []
    for level, words in all_words.items():
        for i, w in enumerate(words):
            batch = min((i // 100) + 1, MAX_BATCHES)
            result.append({**w, "batch": batch})

    return result


# ============================================================
# GUI — Theme & helpers
# ============================================================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Colour palette (sample-1 style)
C_BG        = "#f0f4f8"
C_SIDEBAR   = "#ffffff"
C_CARD      = "#ffffff"
C_PRIMARY   = "#1a73e8"
C_PRIMARY_H = "#1557c0"
C_PRIMARY_L = "#e8f0fe"
C_PRIMARY_LH= "#d2e3fc"
C_TEXT      = "#1a1a2e"
C_MUTED     = "#888888"
C_BORDER    = "#e0e4ea"
C_SUCCESS   = "#2d8a4e"
C_SUCCESS_L = "#e8f5ee"
C_DANGER    = "#b03a2e"
C_DANGER_L  = "#fbeaea"
C_WARN      = "#b07800"
C_WARN_H    = "#8a5c00"
C_BAR_BG    = "#e0e7ef"
C_GREEN_BTN = "#34a853"
C_GREEN_H   = "#1e8a3e"

def F(size: int, bold: bool = False) -> ctk.CTkFont:
    return ctk.CTkFont("Yu Gothic UI", size, "bold" if bold else "normal")


def card(parent, **kw) -> ctk.CTkFrame:
    """White rounded card."""
    return ctk.CTkFrame(parent, fg_color=C_CARD, corner_radius=12, **kw)


# ============================================================
# App shell
# ============================================================

class App(ctk.CTk):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.title("英検単語マスター")
        self.geometry("980x680")
        self.minsize(840, 580)
        self.configure(fg_color=C_BG)

        self.current_level: str = self.db.get_state("current_level", "2級")
        self.current_batch: int = self.db.get_state(f"batch_{self.current_level}", 1)

        # Permanent sidebar
        self._sidebar = SidebarFrame(self, self)
        self._sidebar.pack(side="left", fill="y")

        # Content area
        self._container = ctk.CTkFrame(self, fg_color=C_BG, corner_radius=0)
        self._container.pack(side="left", fill="both", expand=True)

        self.show_home()

    def _clear(self):
        for w in self._container.winfo_children():
            w.destroy()

    def show_home(self):
        self._clear()
        self._sidebar.set_active("home")
        HomeFrame(self._container, self).pack(fill="both", expand=True)

    def show_quiz(self, mode: str = "quiz", drill_threshold: int = 0):
        self._clear()
        self._sidebar.set_active("home")
        QuizFrame(self._container, self, mode=mode,
                  drill_threshold=drill_threshold).pack(fill="both", expand=True)

    def show_word_list(self, list_type: str):
        self._clear()
        self._sidebar.set_active(list_type)
        WordListFrame(self._container, self, list_type=list_type).pack(fill="both", expand=True)

    def set_level(self, level: str):
        self.current_level = level
        self.current_batch = self.db.get_state(f"batch_{level}", 1)
        self.db.set_state("current_level", level)
        self._sidebar.refresh()

    def advance_batch(self):
        if self.current_batch < MAX_BATCHES:
            self.current_batch += 1
            self.db.set_state(f"batch_{self.current_level}", self.current_batch)
        self._sidebar.refresh()


# ============================================================
# Sidebar Frame
# ============================================================

class SidebarFrame(ctk.CTkFrame):
    def __init__(self, parent, app: App):
        super().__init__(parent, width=220, fg_color=C_SIDEBAR, corner_radius=0)
        self.app = app
        self.pack_propagate(False)
        self._active = "home"
        self._nav_btns: dict[str, ctk.CTkButton] = {}
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="英検\n単語マスター",
                     font=F(20, True), text_color=C_PRIMARY,
                     justify="center").pack(pady=(28, 4))

        ctk.CTkFrame(self, height=1, fg_color=C_BORDER).pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(self, text="メニュー", font=F(11),
                     text_color=C_MUTED).pack(anchor="w", padx=20, pady=(0, 6))

        nav_items = [
            ("home",     "🏠   ホーム"),
            ("mastered", "⭐   習得済み一覧"),
            ("weak",     "📉   苦手単語一覧"),
        ]
        for key, label in nav_items:
            active = key == self._active
            btn = ctk.CTkButton(
                self, text=label, width=188, height=38, anchor="w",
                fg_color=C_PRIMARY_L if active else "transparent",
                hover_color=C_PRIMARY_L,
                text_color=C_PRIMARY if active else "#444",
                font=F(13), corner_radius=8,
                command=self._make_nav(key),
            )
            btn.pack(pady=2, padx=16)
            self._nav_btns[key] = btn

        # Spacer
        ctk.CTkFrame(self, fg_color="transparent").pack(fill="both", expand=True)

        ctk.CTkFrame(self, height=1, fg_color=C_BORDER).pack(fill="x", padx=16, pady=8)

        self._info_lbl = ctk.CTkLabel(self, text=self._info_text(),
                                      font=F(12), text_color=C_MUTED,
                                      justify="center")
        self._info_lbl.pack(pady=(0, 20))

    def _make_nav(self, key: str):
        if key == "home":
            return self.app.show_home
        elif key == "mastered":
            return lambda: self.app.show_word_list("mastered")
        else:
            return lambda: self.app.show_word_list("weak")

    def _info_text(self) -> str:
        return f"英検{self.app.current_level}\nバッチ {self.app.current_batch} / {MAX_BATCHES}"

    def set_active(self, screen: str):
        self._active = screen
        for key, btn in self._nav_btns.items():
            active = key == screen
            btn.configure(
                fg_color=C_PRIMARY_L if active else "transparent",
                text_color=C_PRIMARY if active else "#444",
            )

    def refresh(self):
        self._info_lbl.configure(text=self._info_text())


# ============================================================
# Home Frame
# ============================================================

class HomeFrame(ctk.CTkFrame):
    def __init__(self, parent, app: App):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=28, pady=22)

        # ── Greeting ────────────────────────────────────────
        ctk.CTkLabel(root, text="今日も単語を覚えよう",
                     font=F(22, True), text_color=C_TEXT).pack(anchor="w", pady=(0, 16))

        # ── Level card ──────────────────────────────────────
        lc = card(root)
        lc.pack(fill="x", pady=(0, 12))
        lc_inner = ctk.CTkFrame(lc, fg_color="transparent")
        lc_inner.pack(fill="x", padx=16, pady=14)
        ctk.CTkLabel(lc_inner, text="レベル", font=F(11),
                     text_color=C_MUTED).pack(anchor="w", pady=(0, 6))
        rb_row = ctk.CTkFrame(lc_inner, fg_color="transparent")
        rb_row.pack(anchor="w")
        self._level_var = ctk.StringVar(value=self.app.current_level)
        for lv in LEVELS:
            ctk.CTkRadioButton(
                rb_row, text=f"英検{lv}", variable=self._level_var, value=lv,
                font=F(14), fg_color=C_PRIMARY,
                command=self._on_level_change,
            ).pack(side="left", padx=14)

        # ── Progress card ───────────────────────────────────
        pc = card(root)
        pc.pack(fill="x", pady=(0, 12))
        pc_inner = ctk.CTkFrame(pc, fg_color="transparent")
        pc_inner.pack(fill="x", padx=16, pady=16)

        self._batch_lbl = ctk.CTkLabel(pc_inner, text="", font=F(16, True), text_color=C_TEXT)
        self._batch_lbl.pack(anchor="w")
        self._prog_lbl = ctk.CTkLabel(pc_inner, text="", font=F(12), text_color=C_MUTED)
        self._prog_lbl.pack(anchor="w", pady=(3, 10))
        self._prog_bar = ctk.CTkProgressBar(pc_inner, height=10, corner_radius=5,
                                            fg_color=C_BAR_BG, progress_color=C_PRIMARY)
        self._prog_bar.pack(fill="x")

        # ── Action buttons ──────────────────────────────────
        ab = ctk.CTkFrame(root, fg_color="transparent")
        ab.pack(fill="x", pady=(0, 12))

        self._quiz_btn = ctk.CTkButton(
            ab, text="クイズ開始", height=52, corner_radius=10,
            font=F(15, True), fg_color=C_PRIMARY, hover_color=C_PRIMARY_H,
            command=self._start_quiz,
        )
        self._quiz_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))

        self._next_btn = ctk.CTkButton(
            ab, text="次のバッチへ →", height=52, corner_radius=10,
            font=F(14), fg_color=C_PRIMARY_L, hover_color=C_PRIMARY_LH,
            text_color=C_PRIMARY, state="disabled",
            command=self._next_batch,
        )
        self._next_btn.pack(side="left", expand=True, fill="x")

        # ── Drill card ──────────────────────────────────────
        dc = card(root)
        dc.pack(fill="x", pady=(0, 12))
        dc_inner = ctk.CTkFrame(dc, fg_color="transparent")
        dc_inner.pack(fill="x", padx=16, pady=14)
        ctk.CTkLabel(dc_inner, text="集中特訓モード", font=F(13, True),
                     text_color=C_TEXT).pack(anchor="w", pady=(0, 8))
        dr_row = ctk.CTkFrame(dc_inner, fg_color="transparent")
        dr_row.pack(anchor="w")
        ctk.CTkLabel(dr_row, text="間違い回数 ≥", font=F(13),
                     text_color=C_TEXT).pack(side="left")
        self._thresh_var = ctk.StringVar(value="3")
        ctk.CTkEntry(dr_row, textvariable=self._thresh_var, width=52, font=F(13),
                     border_color=C_BORDER, fg_color="#f8fafc",
                     text_color=C_TEXT).pack(side="left", padx=8)
        ctk.CTkLabel(dr_row, text="回", font=F(13), text_color=C_TEXT).pack(side="left")
        ctk.CTkButton(dr_row, text="特訓開始", width=100, height=34,
                      font=F(13), fg_color=C_GREEN_BTN, hover_color=C_GREEN_H,
                      corner_radius=8, command=self._start_drill).pack(side="left", padx=12)

        # ── List buttons ────────────────────────────────────
        lb = ctk.CTkFrame(root, fg_color="transparent")
        lb.pack(fill="x")
        lb.columnconfigure((0, 1), weight=1)
        ctk.CTkButton(
            lb, text="⭐  習得済み単語一覧", height=42, corner_radius=10,
            font=F(13), fg_color="#f0faf4", hover_color="#d8f0e2",
            text_color=C_SUCCESS,
            command=lambda: self.app.show_word_list("mastered"),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(
            lb, text="📉  苦手単語一覧", height=42, corner_radius=10,
            font=F(13), fg_color="#fdf0f0", hover_color="#f8d8d8",
            text_color=C_DANGER,
            command=lambda: self.app.show_word_list("weak"),
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self._refresh()

    def _refresh(self):
        level = self.app.current_level
        batch = self.app.current_batch
        total, mastered = self.app.db.get_batch_progress(level, batch)

        self._batch_lbl.configure(text=f"英検{level}　バッチ {batch} / {MAX_BATCHES}")
        self._prog_lbl.configure(text=f"習得済み　{mastered} / {total} 語")
        self._prog_bar.set(mastered / total if total else 0)

        has_session = self.app.db.get_active_session(level, batch, "quiz") is not None
        self._quiz_btn.configure(text="セッションを再開" if has_session else "クイズ開始")

        all_done = total > 0 and mastered == total
        if all_done and batch >= MAX_BATCHES:
            self._next_btn.configure(text="全バッチ習得完了！",
                                     fg_color="#fff4cc", hover_color="#fff4cc",
                                     text_color="#c9a000", state="disabled")
        else:
            self._next_btn.configure(
                text="次のバッチへ →",
                fg_color=C_PRIMARY_L, hover_color=C_PRIMARY_LH,
                text_color=C_PRIMARY,
                state="normal" if all_done else "disabled",
            )

    def _on_level_change(self):
        self.app.set_level(self._level_var.get())
        self._refresh()

    def _start_quiz(self):
        self.app.show_quiz(mode="quiz")

    def _start_drill(self):
        try:
            thr = max(1, int(self._thresh_var.get()))
        except ValueError:
            thr = 3
        self.app.show_quiz(mode="drill", drill_threshold=thr)

    def _next_batch(self):
        self.app.advance_batch()
        self._refresh()


# ============================================================
# Quiz Frame
# ============================================================

class QuizFrame(ctk.CTkFrame):
    def __init__(self, parent, app: App, mode: str = "quiz", drill_threshold: int = 0):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.mode = mode
        self.drill_threshold = drill_threshold

        self.session_id: int | None = None
        self.word_ids: list[int] = []
        self.current_q: int = 0
        self.answers: list[bool] = []
        self.all_meanings: dict[int, list[str]] = {}
        self.answered: bool = False
        self.current_word_id: int = 0
        self.correct_meaning: str = ""
        self.correct_meanings_all: list[str] = []

        self._build_ui()
        self._load_session()

    def _build_ui(self):
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=28, pady=18)

        # ── Header ──────────────────────────────────────────
        hdr = card(root)
        hdr.pack(fill="x", pady=(0, 14))
        hdr_inner = ctk.CTkFrame(hdr, fg_color="transparent")
        hdr_inner.pack(fill="x", padx=16, pady=10)
        self._q_lbl = ctk.CTkLabel(hdr_inner, text="", font=F(14), text_color=C_TEXT)
        self._q_lbl.pack(side="left")
        ctk.CTkButton(
            hdr_inner, text="中断", width=76, height=30,
            fg_color=C_PRIMARY_L, hover_color=C_PRIMARY_LH,
            text_color=C_PRIMARY, font=F(13), corner_radius=8,
            command=self._interrupt,
        ).pack(side="right")

        # ── Word card ────────────────────────────────────────
        wc = card(root)
        wc.pack(fill="x", pady=(0, 10))
        self._word_lbl = ctk.CTkLabel(wc, text="", font=F(36, True), text_color=C_TEXT)
        self._word_lbl.pack(pady=24)

        # ── Feedback ─────────────────────────────────────────
        self._feedback_lbl = ctk.CTkLabel(root, text="", font=F(14), text_color=C_TEXT)
        self._feedback_lbl.pack(pady=(0, 6))

        # ── Choices (3 rows × 2 cols) ────────────────────────
        self._choices_frame = ctk.CTkFrame(root, fg_color="transparent")
        self._choices_frame.pack(fill="both", expand=True)
        self._choices_frame.columnconfigure((0, 1), weight=1)

        self._choice_btns: list[ctk.CTkButton] = []
        for i in range(6):
            r, c = divmod(i, 2)
            btn = ctk.CTkButton(
                self._choices_frame, text="", height=46,
                font=F(14), fg_color=C_PRIMARY, hover_color=C_PRIMARY_H,
                text_color="#ffffff", corner_radius=8,
                command=lambda idx=i: self._answer(idx),
            )
            btn.grid(row=r, column=c, padx=6, pady=4, sticky="ew")
            self._choice_btns.append(btn)

        # ── わからない button ────────────────────────────────
        self._dont_know_btn = ctk.CTkButton(
            root, text="わからない", height=38, corner_radius=8,
            font=F(14), fg_color="#fff4e0", hover_color="#ffe8b8",
            text_color=C_WARN, border_width=1, border_color="#f0d090",
            command=self._dont_know,
        )
        self._dont_know_btn.pack(fill="x", pady=(8, 0))
        self._dont_know_btn.pack_forget()

        # ── さらに詳しく button ───────────────────────────────
        self._detail_btn = ctk.CTkButton(
            root, text="さらに詳しく表示", height=38, corner_radius=8,
            font=F(13), fg_color="#f0f4ff", hover_color="#dce8ff",
            text_color=C_PRIMARY, border_width=1, border_color=C_PRIMARY_L,
            command=self._show_details,
        )
        self._detail_btn.pack(fill="x", pady=(4, 0))
        self._detail_btn.pack_forget()

        # ── Next button ──────────────────────────────────────
        self._next_btn = ctk.CTkButton(
            root, text="次の問題 →", height=44, corner_radius=8,
            font=F(14, True), fg_color=C_PRIMARY, hover_color=C_PRIMARY_H,
            command=self._next_question,
        )
        self._next_btn.pack(fill="x", pady=(8, 0))
        self._next_btn.pack_forget()

    def _load_session(self):
        level = self.app.current_level
        batch = self.app.current_batch

        existing = self.app.db.get_active_session(level, batch, self.mode)
        if existing:
            self.session_id = existing["id"]
            self.word_ids   = json.loads(existing["word_ids"])
            self.current_q  = existing["current_question"]
            self.answers    = json.loads(existing["answers"])
        else:
            if self.mode == "quiz":
                candidates = self.app.db.get_unmastered_for_batch(level, batch)
            else:
                candidates = self.app.db.get_drill_words(level, self.drill_threshold)

            if not candidates:
                self._show_no_words()
                return

            selected  = random.sample(candidates, min(SESSION_SIZE, len(candidates)))
            word_ids  = [w["id"] for w in selected]
            self.session_id = self.app.db.create_session(
                level, batch, self.mode, word_ids, self.drill_threshold
            )
            self.word_ids  = word_ids
            self.current_q = 0
            self.answers   = []

        self.all_meanings = self.app.db.get_all_meanings_for_level(level)
        self._show_question()

    def _show_no_words(self):
        for w in self.winfo_children():
            w.destroy()
        ctk.CTkLabel(self, text="出題できる単語がありません。\n全て習得済み、または条件に合う単語がありません。",
                     font=F(16), text_color=C_TEXT).pack(expand=True)
        ctk.CTkButton(self, text="ホームへ戻る", width=160, height=42,
                      font=F(14), fg_color=C_PRIMARY, hover_color=C_PRIMARY_H,
                      command=self.app.show_home).pack(pady=20)

    def _show_question(self):
        if self.current_q >= len(self.word_ids):
            self._show_result()
            return

        self.answered = False
        word_id = self.word_ids[self.current_q]
        self.current_word_id = word_id

        w = self.app.db.get_word(word_id)
        # Bug2修正: DBに該当単語が存在しない場合はスキップして次問へ
        if not w:
            self.current_q += 1
            self._show_question()
            return
        word_text = w["word"]
        meanings  = json.loads(w["meanings"])

        self._q_lbl.configure(
            text=f"問題  {self.current_q + 1} / {len(self.word_ids)}　"
                 f"{'クイズ' if self.mode == 'quiz' else '集中特訓'}モード"
        )
        self._word_lbl.configure(text=word_text)
        self._feedback_lbl.configure(text="", text_color=C_TEXT)

        self.correct_meaning      = meanings[0]
        self.correct_meanings_all = meanings

        other_ids = [i for i in self.all_meanings if i != word_id]
        random.shuffle(other_ids)
        distractors: list[str] = []
        for oid in other_ids:
            m = self.all_meanings[oid][0]
            if m != self.correct_meaning and m not in distractors:
                distractors.append(m)
            if len(distractors) == 5:
                break

        choices = [self.correct_meaning] + distractors[:5]
        random.shuffle(choices)

        for i, btn in enumerate(self._choice_btns):
            if i < len(choices):
                btn.configure(text=choices[i], state="normal",
                              fg_color=C_PRIMARY, hover_color=C_PRIMARY_H,
                              text_color="#ffffff")
                btn.grid()
            else:
                btn.configure(text="")   # Bug3: 古いテキストをクリアして誤判定を防ぐ
                btn.grid_remove()

        self._dont_know_btn.pack(fill="x", pady=(8, 0))
        self._detail_btn.pack_forget()
        self._next_btn.pack_forget()

    def _answer(self, idx: int):
        if self.answered:
            return
        self.answered = True

        chosen     = self._choice_btns[idx].cget("text")
        is_correct = chosen == self.correct_meaning

        self.app.db.record_answer(self.current_word_id, is_correct)
        self.answers.append(is_correct)
        # Bug1修正: current_q+1（次問題番号）で保存。中断時に同問題が再表示されるのを防ぐ
        self.app.db.update_session(self.session_id, self.current_q + 1, self.answers)

        self._dont_know_btn.pack_forget()

        for i, btn in enumerate(self._choice_btns):
            btn.configure(state="disabled")
            if btn.cget("text") == self.correct_meaning:
                btn.configure(fg_color=C_SUCCESS, hover_color=C_SUCCESS, text_color="#ffffff")
            elif i == idx and not is_correct:
                btn.configure(fg_color=C_DANGER, hover_color=C_DANGER, text_color="#ffffff")
            else:
                btn.configure(fg_color="#e0e4ea", text_color=C_MUTED)

        if is_correct:
            meaning_str = "　/　".join(self.correct_meanings_all)
            self._feedback_lbl.configure(
                text=f"✓ 正解！　意味：{meaning_str}", text_color=C_SUCCESS)
        else:
            self._feedback_lbl.configure(
                text=f"✗ 不正解　正解：{self.correct_meaning}", text_color=C_DANGER)
            self._detail_btn.configure(text="さらに詳しく表示", state="normal")
            self._detail_btn.pack(fill="x", pady=(4, 0))

        self._next_btn.pack(fill="x", pady=(8, 0))

    def _dont_know(self):
        if self.answered:
            return
        self.answered = True

        self.app.db.record_answer(self.current_word_id, False)
        self.answers.append(False)
        # Bug1修正: current_q+1（次問題番号）で保存
        self.app.db.update_session(self.session_id, self.current_q + 1, self.answers)

        self._dont_know_btn.pack_forget()

        for btn in self._choice_btns:
            btn.configure(state="disabled")
            if btn.cget("text") == self.correct_meaning:
                btn.configure(fg_color=C_SUCCESS, hover_color=C_SUCCESS, text_color="#ffffff")
            else:
                btn.configure(fg_color="#e0e4ea", text_color=C_MUTED)

        meaning_str = "　/　".join(self.correct_meanings_all)
        # Bug2修正: "正解：" は「正解した」と誤解されるため "✗ わからない" を明示
        self._feedback_lbl.configure(
            text=f"✗ わからない　正解：{meaning_str}", text_color=C_WARN)

        self._detail_btn.configure(text="さらに詳しく表示", state="normal")
        self._detail_btn.pack(fill="x", pady=(4, 0))
        self._next_btn.pack(fill="x", pady=(8, 0))

    def _show_details(self):
        word = self._word_lbl.cget("text")
        open_detail_popup(self, word, self.current_word_id, self.app.db, {
            "C_BG": C_BG, "C_TEXT": C_TEXT, "C_PRIMARY": C_PRIMARY,
            "C_PRIMARY_H": C_PRIMARY_H, "C_PRIMARY_L": C_PRIMARY_L,
            "C_MUTED": C_MUTED, "C_DANGER": C_DANGER,
        })

    def _next_question(self):
        self.current_q += 1
        # Bug1修正: 保存は _answer/_dont_know 側で current_q+1 として済んでいるため不要
        self._show_question()

    def _interrupt(self):
        # Bug1修正: 回答後は既に current_q+1 で保存済み。未回答時もセッション作成時の
        # 状態（current_q=0）または前回の保存状態が DB に残っているため追加保存不要
        self.app.show_home()

    def _show_result(self):
        # Bug3修正: session_id が None の場合（稀なエラーケース）は安全にホームへ戻る
        if self.session_id is None:
            self.app.show_home()
            return
        self.app.db.complete_session(self.session_id)
        for w in self.winfo_children():
            w.destroy()

        correct = sum(self.answers)
        total   = len(self.answers)
        rate    = round(correct / total * 100) if total else 0

        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=40, pady=30)

        rc = card(root)
        rc.pack(fill="x", pady=(0, 16))
        rc_inner = ctk.CTkFrame(rc, fg_color="transparent")
        rc_inner.pack(fill="x", padx=24, pady=28)

        ctk.CTkLabel(rc_inner, text="セッション結果",
                     font=F(22, True), text_color=C_TEXT).pack(anchor="w")
        ctk.CTkLabel(rc_inner,
                     text=f"正解　{correct} / {total}　　正答率　{rate}%",
                     font=F(18), text_color=C_PRIMARY).pack(anchor="w", pady=(10, 0))

        if rate >= 80:
            comment = "素晴らしい！この調子で続けましょう！"
            tc = C_SUCCESS
        elif rate >= 60:
            comment = "よくできました！もう少しで完璧です。"
            tc = C_PRIMARY
        else:
            comment = "もう少し練習しましょう！繰り返しが大切です。"
            tc = C_WARN
        ctk.CTkLabel(rc_inner, text=comment, font=F(14), text_color=tc).pack(anchor="w", pady=(8, 0))

        ctk.CTkButton(root, text="ホームへ戻る", height=48, corner_radius=10,
                      font=F(15, True), fg_color=C_PRIMARY, hover_color=C_PRIMARY_H,
                      command=self.app.show_home).pack(fill="x", pady=16)


# ============================================================
# Word List Frame
# ============================================================

class WordListFrame(ctk.CTkFrame):
    def __init__(self, parent, app: App, list_type: str = "mastered"):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.list_type = list_type
        self.sort_col = ""
        self.sort_rev = False
        self._words: list[dict] = []
        self._columns: list[str] = []
        self._col_w: list[int] = []
        self._build()

    def _build(self):
        level = self.app.current_level

        if self.list_type == "mastered":
            title        = f"英検{level}　習得済み単語一覧"
            self._words  = self.app.db.get_mastered_words(level)
            self._columns= ["word", "meanings", "batch_number", "incorrect_count", "mastered_date"]
            headers      = ["単語 / 連語", "意味", "バッチ", "間違い", "習得日", "操作"]
            self._col_w  = [140, 230, 50, 50, 86, 88]
        else:
            title        = f"英検{level}　苦手単語一覧"
            self._words  = self.app.db.get_weak_words(level)
            self._columns= ["word", "meanings", "batch_number", "incorrect_count", "streak"]
            headers      = ["単語 / 連語", "意味", "バッチ", "間違い", "連続正解", "詳細"]
            self._col_w  = [150, 250, 55, 55, 70, 72]

        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=24, pady=18)

        # ── Header card ──────────────────────────────────────
        hc = card(root)
        hc.pack(fill="x", pady=(0, 12))
        hc_inner = ctk.CTkFrame(hc, fg_color="transparent")
        hc_inner.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(hc_inner, text=title, font=F(17, True),
                     text_color=C_TEXT).pack(side="left")
        ctk.CTkLabel(hc_inner, text=f"{len(self._words)} 件",
                     font=F(12), text_color=C_MUTED).pack(side="left", padx=10)
        ctk.CTkButton(hc_inner, text="← 戻る", width=84, height=30,
                      font=F(13), fg_color=C_PRIMARY_L, hover_color=C_PRIMARY_LH,
                      text_color=C_PRIMARY, corner_radius=8,
                      command=self.app.show_home).pack(side="right")

        # ── Column headers ───────────────────────────────────
        col_hdr = ctk.CTkFrame(root, fg_color=C_CARD, corner_radius=8)
        col_hdr.pack(fill="x", pady=(0, 4))
        # Bug4修正: zip を self._columns で止めてソート可能列のみボタン化し、
        # 操作列は別途ラベルで追加する
        for col, hdr_txt, w in zip(self._columns, headers, self._col_w):
            ctk.CTkButton(
                col_hdr, text=hdr_txt, width=w, height=30,
                fg_color="transparent", hover_color=C_PRIMARY_L,
                text_color=C_MUTED, font=F(12),
                corner_radius=0,
                command=lambda c=col: self._sort(c),
            ).pack(side="left", padx=1)
        if self.list_type == "mastered":
            ctk.CTkLabel(col_hdr, text="操作", width=88, height=30,
                         font=F(12), text_color=C_MUTED,
                         anchor="center").pack(side="left", padx=1)
        else:
            ctk.CTkLabel(col_hdr, text="詳細", width=72, height=30,
                         font=F(12), text_color=C_MUTED,
                         anchor="center").pack(side="left", padx=1)

        # ── Scrollable rows ──────────────────────────────────
        self._scroll = ctk.CTkScrollableFrame(root, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True)

        self._render_rows()

    def _render_rows(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        for i, row in enumerate(self._words):
            meanings = json.loads(row["meanings"]) if isinstance(row["meanings"], str) else row["meanings"]
            values = {
                "word":            row["word"],
                "meanings":        " / ".join(meanings),
                "batch_number":    str(row["batch_number"]),
                "incorrect_count": str(row["incorrect_count"]),
                "mastered_date":   str(row.get("mastered_date", "")),
                "streak":          str(row.get("streak", "")),
            }
            bg = C_CARD if i % 2 == 0 else "#f7f9fc"
            rf = ctk.CTkFrame(self._scroll, fg_color=bg, corner_radius=6)
            rf.pack(fill="x", pady=1)
            for col, w in zip(self._columns, self._col_w):
                ctk.CTkLabel(
                    rf, text=values.get(col, ""), width=w, anchor="w",
                    font=F(12), text_color=C_TEXT,
                ).pack(side="left", padx=8, pady=6)

            word_id = row["id"]
            if self.list_type == "mastered":
                btn_frame = ctk.CTkFrame(rf, fg_color="transparent")
                btn_frame.pack(side="left", padx=4, pady=4)
                ctk.CTkButton(
                    btn_frame, text="苦手に移す", width=84, height=26,
                    font=F(11), fg_color=C_DANGER_L, hover_color="#f8d8d8",
                    text_color=C_DANGER, corner_radius=6,
                    command=lambda wid=word_id: self._unmaster(wid),
                ).pack(pady=(0, 2))
                ctk.CTkButton(
                    btn_frame, text="詳細", width=84, height=26,
                    font=F(11), fg_color="#f0f4ff", hover_color="#dce8ff",
                    text_color=C_PRIMARY, corner_radius=6,
                    command=lambda wid=word_id, wt=row["word"]: self._open_detail(wid, wt),
                ).pack()
            else:
                ctk.CTkButton(
                    rf, text="詳細", width=68, height=28,
                    font=F(11), fg_color="#f0f4ff", hover_color="#dce8ff",
                    text_color=C_PRIMARY, corner_radius=6,
                    command=lambda wid=word_id, wt=row["word"]: self._open_detail(wid, wt),
                ).pack(side="left", padx=6, pady=6)

    def _unmaster(self, word_id: int):
        self.app.db.unmaster_word(word_id)
        self._words = self.app.db.get_mastered_words(self.app.current_level)
        self._render_rows()

    def _open_detail(self, word_id: int, word: str):
        open_detail_popup(self, word, word_id, self.app.db, {
            "C_BG": C_BG, "C_TEXT": C_TEXT, "C_PRIMARY": C_PRIMARY,
            "C_PRIMARY_H": C_PRIMARY_H, "C_PRIMARY_L": C_PRIMARY_L,
            "C_MUTED": C_MUTED, "C_DANGER": C_DANGER,
        })

    def _sort(self, col: str):
        if self.sort_col == col:
            self.sort_rev = not self.sort_rev
        else:
            self.sort_col = col
            self.sort_rev = False

        def key_fn(r):
            val = r.get(col, "")
            if val is None:
                return ""
            try:
                return int(val)
            except (ValueError, TypeError):
                return str(val)

        self._words.sort(key=key_fn, reverse=self.sort_rev)
        self._render_rows()


# ============================================================
# Entry point
# ============================================================

def main():
    # Check vocabulary file
    if not MD_PATH.exists():
        import tkinter as tk
        import tkinter.messagebox as mb
        root = tk.Tk()
        root.withdraw()
        mb.showerror(
            "ファイルが見つかりません",
            f"単語ファイルが見つかりません:\n{MD_PATH}\n\n"
            "eiken_vocabulary.md を同じフォルダに置いてください。",
        )
        sys.exit(1)

    db = Database(DB_PATH)
    db.init()

    # Import words on first run
    if not db.is_populated():
        words = parse_vocabulary_md(MD_PATH)
        if not words:
            import tkinter as tk
            import tkinter.messagebox as mb
            root = tk.Tk()
            root.withdraw()
            mb.showerror("読み込みエラー", "単語データの読み込みに失敗しました。\neiken_vocabulary.md の形式を確認してください。")
            sys.exit(1)
        db.insert_words(words)

    app = App(db)
    app.mainloop()


if __name__ == "__main__":
    main()
