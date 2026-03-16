#!/usr/bin/env python3
"""
UIサンプル パターン1：クリーン＆ライト
白ベース・シンプル・明るい配色
"""

import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class SampleHome(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("UIサンプル 1 - クリーン＆ライト")
        self.geometry("900x660")
        self.minsize(800, 580)
        self.configure(fg_color="#f0f4f8")
        self._build()

    def _build(self):
        # ── サイドバー ──────────────────────────────────────
        sidebar = ctk.CTkFrame(self, width=220, fg_color="#ffffff",
                               corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="英検\n単語マスター",
                     font=ctk.CTkFont("Yu Gothic UI", 22, "bold"),
                     text_color="#1a73e8").pack(pady=(32, 8))

        ctk.CTkLabel(sidebar, text="学習ナビ",
                     font=ctk.CTkFont("Yu Gothic UI", 11),
                     text_color="#888").pack(pady=(16, 4))

        menu_items = [
            ("🏠  ホーム",       True),
            ("📝  クイズ",       False),
            ("🎯  集中特訓",     False),
            ("⭐  習得済み一覧", False),
            ("📉  苦手単語一覧", False),
        ]
        for label, active in menu_items:
            fg = "#e8f0fe" if active else "transparent"
            tc = "#1a73e8" if active else "#444"
            ctk.CTkButton(
                sidebar, text=label, width=180, height=38, anchor="w",
                fg_color=fg, hover_color="#e8f0fe",
                text_color=tc, font=ctk.CTkFont("Yu Gothic UI", 13),
                corner_radius=8,
            ).pack(pady=3, padx=16)

        # ── メインコンテンツ ────────────────────────────────
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(side="left", fill="both", expand=True, padx=24, pady=24)

        # グリーティング
        ctk.CTkLabel(main, text="おかえりなさい 👋",
                     font=ctk.CTkFont("Yu Gothic UI", 14),
                     text_color="#666").pack(anchor="w")
        ctk.CTkLabel(main, text="今日も単語を覚えよう",
                     font=ctk.CTkFont("Yu Gothic UI", 22, "bold"),
                     text_color="#1a1a2e").pack(anchor="w", pady=(0, 16))

        # レベル選択カード
        lf = ctk.CTkFrame(main, fg_color="#ffffff", corner_radius=12)
        lf.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(lf, text="レベル",
                     font=ctk.CTkFont("Yu Gothic UI", 12),
                     text_color="#888").pack(anchor="w", padx=16, pady=(12, 4))
        rb_row = ctk.CTkFrame(lf, fg_color="transparent")
        rb_row.pack(anchor="w", padx=12, pady=(0, 12))
        lv_var = ctk.StringVar(value="2級")
        for lv in ("2級", "準1級"):
            ctk.CTkRadioButton(rb_row, text=f"英検{lv}", variable=lv_var, value=lv,
                               font=ctk.CTkFont("Yu Gothic UI", 13),
                               fg_color="#1a73e8").pack(side="left", padx=12)

        # 進捗カード
        prog_card = ctk.CTkFrame(main, fg_color="#ffffff", corner_radius=12)
        prog_card.pack(fill="x", pady=(0, 12))
        prog_inner = ctk.CTkFrame(prog_card, fg_color="transparent")
        prog_inner.pack(fill="x", padx=16, pady=14)

        ctk.CTkLabel(prog_inner, text="バッチ 1 / 4　　英検2級",
                     font=ctk.CTkFont("Yu Gothic UI", 14, "bold"),
                     text_color="#1a1a2e").pack(anchor="w")
        ctk.CTkLabel(prog_inner, text="習得済み  23 / 100",
                     font=ctk.CTkFont("Yu Gothic UI", 12),
                     text_color="#666").pack(anchor="w", pady=(4, 8))
        bar = ctk.CTkProgressBar(prog_inner, height=10, corner_radius=5,
                                 fg_color="#e0e7ef", progress_color="#1a73e8")
        bar.set(0.23)
        bar.pack(fill="x")

        # アクションボタン行
        btn_row = ctk.CTkFrame(main, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 12))

        ctk.CTkButton(btn_row, text="クイズ開始",
                      width=200, height=50,
                      font=ctk.CTkFont("Yu Gothic UI", 15, "bold"),
                      fg_color="#1a73e8", hover_color="#1557c0",
                      corner_radius=10).pack(side="left", padx=(0, 12))

        ctk.CTkButton(btn_row, text="次のバッチへ →",
                      width=160, height=50,
                      font=ctk.CTkFont("Yu Gothic UI", 13),
                      fg_color="#e8f0fe", hover_color="#d2e3fc",
                      text_color="#1a73e8", corner_radius=10,
                      state="disabled").pack(side="left")

        # 集中特訓カード
        drill_card = ctk.CTkFrame(main, fg_color="#ffffff", corner_radius=12)
        drill_card.pack(fill="x", pady=(0, 12))
        drill_inner = ctk.CTkFrame(drill_card, fg_color="transparent")
        drill_inner.pack(fill="x", padx=16, pady=14)
        ctk.CTkLabel(drill_inner, text="集中特訓モード",
                     font=ctk.CTkFont("Yu Gothic UI", 13, "bold"),
                     text_color="#1a1a2e").pack(anchor="w", pady=(0, 6))
        drill_row = ctk.CTkFrame(drill_inner, fg_color="transparent")
        drill_row.pack(anchor="w")
        ctk.CTkLabel(drill_row, text="間違い回数 ≥",
                     font=ctk.CTkFont("Yu Gothic UI", 13),
                     text_color="#555").pack(side="left")
        ctk.CTkEntry(drill_row, width=52, placeholder_text="3",
                     font=ctk.CTkFont("Yu Gothic UI", 13)).pack(side="left", padx=8)
        ctk.CTkLabel(drill_row, text="回",
                     font=ctk.CTkFont("Yu Gothic UI", 13),
                     text_color="#555").pack(side="left")
        ctk.CTkButton(drill_row, text="特訓開始", width=100, height=34,
                      font=ctk.CTkFont("Yu Gothic UI", 13),
                      fg_color="#34a853", hover_color="#2d8a4e",
                      corner_radius=8).pack(side="left", padx=12)

        # 一覧ボタン行
        list_row = ctk.CTkFrame(main, fg_color="transparent")
        list_row.pack(fill="x")
        for label, color, hover in [
            ("⭐ 習得済み単語一覧", "#f4f0ff", "#e8d5ff"),
            ("📉 苦手単語一覧",    "#fff4f0", "#ffd5cc"),
        ]:
            ctk.CTkButton(list_row, text=label, height=40,
                          font=ctk.CTkFont("Yu Gothic UI", 13),
                          fg_color=color, hover_color=hover,
                          text_color="#333", corner_radius=8
                          ).pack(side="left", expand=True, fill="x", padx=6)

SampleHome().mainloop()
