#!/usr/bin/env python3
"""
UIサンプル パターン3：ウォーム＆ナチュラル
深いネイビー＋ゴールドのアクセント・落ち着いた和洋折衷スタイル
"""

import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

NAVY     = "#0f1628"
NAVY_MID = "#16213e"
NAVY_LT  = "#1a2952"
GOLD     = "#f5a623"
GOLD_LT  = "#ffc85a"
CREAM    = "#f5f0e8"
MUTED    = "#8896b0"
SUCCESS  = "#4caf88"
DANGER   = "#e05c5c"

class SampleHome(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("UIサンプル 3 - ウォーム＆ナチュラル")
        self.geometry("920x680")
        self.minsize(800, 580)
        self.configure(fg_color=NAVY)
        self._build()

    def _build(self):
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=32, pady=24)

        # ── ヘッダー ─────────────────────────────────────
        header = ctk.CTkFrame(root, fg_color=NAVY_MID, corner_radius=16, height=72)
        header.pack(fill="x", pady=(0, 20))
        header.pack_propagate(False)

        h_inner = ctk.CTkFrame(header, fg_color="transparent")
        h_inner.pack(fill="both", expand=True, padx=20)

        # アプリ名（ゴールド）
        ctk.CTkLabel(h_inner,
                     text="英検単語マスター",
                     font=ctk.CTkFont("Yu Gothic UI", 22, "bold"),
                     text_color=GOLD).pack(side="left", pady=16)

        # レベル選択（右寄せ）
        lv_var = ctk.StringVar(value="2級")
        for lv in ("2級", "準1級"):
            ctk.CTkRadioButton(
                h_inner, text=f"英検{lv}", variable=lv_var, value=lv,
                font=ctk.CTkFont("Yu Gothic UI", 13),
                fg_color=GOLD, border_color=GOLD,
                hover_color=NAVY_LT, text_color=CREAM,
            ).pack(side="right", padx=16, pady=18)
        ctk.CTkLabel(h_inner, text="レベル：",
                     font=ctk.CTkFont("Yu Gothic UI", 12),
                     text_color=MUTED).pack(side="right", pady=18)

        # ── コンテンツ 2カラム ───────────────────────────
        content = ctk.CTkFrame(root, fg_color="transparent")
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)

        # ── 左カラム ─────────────────────────────────────
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        # 進捗カード
        prog = ctk.CTkFrame(left, fg_color=NAVY_MID, corner_radius=16)
        prog.pack(fill="x", pady=(0, 14))
        p_inner = ctk.CTkFrame(prog, fg_color="transparent")
        p_inner.pack(fill="x", padx=20, pady=18)

        ctk.CTkLabel(p_inner, text="現在のバッチ",
                     font=ctk.CTkFont("Yu Gothic UI", 11),
                     text_color=MUTED).pack(anchor="w")
        ctk.CTkLabel(p_inner, text="英検2級　バッチ 1 / 4",
                     font=ctk.CTkFont("Yu Gothic UI", 18, "bold"),
                     text_color=CREAM).pack(anchor="w", pady=(2, 12))

        bar_row = ctk.CTkFrame(p_inner, fg_color="transparent")
        bar_row.pack(fill="x")
        bar = ctk.CTkProgressBar(bar_row, height=14, corner_radius=7,
                                 fg_color=NAVY_LT, progress_color=GOLD)
        bar.set(0.23)
        bar.pack(fill="x", side="left", expand=True)
        ctk.CTkLabel(bar_row, text=" 23%",
                     font=ctk.CTkFont("Yu Gothic UI", 12, "bold"),
                     text_color=GOLD).pack(side="left")

        ctk.CTkLabel(p_inner, text="習得済み  23 / 100 語",
                     font=ctk.CTkFont("Yu Gothic UI", 12),
                     text_color=MUTED).pack(anchor="w", pady=(8, 0))

        # クイズ開始ボタン（大）
        ctk.CTkButton(
            left, text="▶  クイズを開始する",
            height=60, corner_radius=14,
            font=ctk.CTkFont("Yu Gothic UI", 17, "bold"),
            fg_color=GOLD, hover_color=GOLD_LT,
            text_color=NAVY,
        ).pack(fill="x", pady=(0, 10))

        # 次のバッチ
        ctk.CTkButton(
            left, text="次のバッチへ →  （全習得後に活性）",
            height=44, corner_radius=12,
            font=ctk.CTkFont("Yu Gothic UI", 13),
            fg_color=NAVY_LT, hover_color=NAVY_LT,
            text_color=MUTED, state="disabled",
        ).pack(fill="x", pady=(0, 14))

        # 一覧ボタン
        list_row = ctk.CTkFrame(left, fg_color="transparent")
        list_row.pack(fill="x")
        list_row.columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            list_row, text="⭐  習得済み一覧", height=44, corner_radius=12,
            font=ctk.CTkFont("Yu Gothic UI", 13),
            fg_color="#1d2b1d", hover_color="#263526",
            text_color=SUCCESS,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(
            list_row, text="📉  苦手単語一覧", height=44, corner_radius=12,
            font=ctk.CTkFont("Yu Gothic UI", 13),
            fg_color="#2b1d1d", hover_color="#352626",
            text_color=DANGER,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # ── 右カラム ─────────────────────────────────────
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")

        # 集中特訓カード
        drill = ctk.CTkFrame(right, fg_color=NAVY_MID, corner_radius=16)
        drill.pack(fill="x", pady=(0, 14))
        d_inner = ctk.CTkFrame(drill, fg_color="transparent")
        d_inner.pack(fill="x", padx=20, pady=18)

        # アクセントライン
        accent = ctk.CTkFrame(d_inner, height=3, fg_color=GOLD, corner_radius=2)
        accent.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(d_inner, text="⚡  集中特訓モード",
                     font=ctk.CTkFont("Yu Gothic UI", 15, "bold"),
                     text_color=CREAM).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(d_inner,
                     text="間違えた回数が多い単語を\n集中して練習できます。",
                     font=ctk.CTkFont("Yu Gothic UI", 12),
                     text_color=MUTED, justify="left").pack(anchor="w", pady=(0, 12))

        th_row = ctk.CTkFrame(d_inner, fg_color="transparent")
        th_row.pack(anchor="w")
        ctk.CTkLabel(th_row, text="しきい値",
                     font=ctk.CTkFont("Yu Gothic UI", 12),
                     text_color=MUTED).pack(side="left")
        ctk.CTkEntry(th_row, width=54, placeholder_text="3",
                     font=ctk.CTkFont("Yu Gothic UI", 13),
                     border_color=GOLD, fg_color=NAVY_LT,
                     text_color=CREAM).pack(side="left", padx=8)
        ctk.CTkLabel(th_row, text="回以上",
                     font=ctk.CTkFont("Yu Gothic UI", 12),
                     text_color=MUTED).pack(side="left")

        ctk.CTkButton(d_inner, text="特訓開始", height=40, corner_radius=10,
                      font=ctk.CTkFont("Yu Gothic UI", 13, "bold"),
                      fg_color=GOLD, hover_color=GOLD_LT,
                      text_color=NAVY).pack(fill="x", pady=(12, 0))

        # 統計カード
        stat = ctk.CTkFrame(right, fg_color=NAVY_MID, corner_radius=16)
        stat.pack(fill="x")
        s_inner = ctk.CTkFrame(stat, fg_color="transparent")
        s_inner.pack(fill="x", padx=20, pady=16)
        ctk.CTkLabel(s_inner, text="クイック統計",
                     font=ctk.CTkFont("Yu Gothic UI", 13, "bold"),
                     text_color=CREAM).pack(anchor="w", pady=(0, 10))

        stats = [
            ("習得済み", "23 語", SUCCESS),
            ("苦手単語", "8 語", DANGER),
            ("残り",     "77 語", MUTED),
        ]
        for label, val, color in stats:
            row = ctk.CTkFrame(s_inner, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=label,
                         font=ctk.CTkFont("Yu Gothic UI", 12),
                         text_color=MUTED).pack(side="left")
            ctk.CTkLabel(row, text=val,
                         font=ctk.CTkFont("Yu Gothic UI", 12, "bold"),
                         text_color=color).pack(side="right")

SampleHome().mainloop()
