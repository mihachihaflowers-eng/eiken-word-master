#!/usr/bin/env python3
"""
UIサンプル パターン2：ネオン＆ダーク
黒ベース・シアン/パープルのネオンアクセント・ゲーミング風
"""

import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

NEON_CYAN   = "#00e5ff"
NEON_PURPLE = "#b040fb"
NEON_GREEN  = "#39ff14"
BG_DEEP     = "#0a0a14"
BG_CARD     = "#12121e"
BG_CARD2    = "#1a1a2e"
TEXT_DIM    = "#7a7a9a"

class SampleHome(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("UIサンプル 2 - ネオン＆ダーク")
        self.geometry("900x660")
        self.minsize(800, 580)
        self.configure(fg_color=BG_DEEP)
        self._build()

    def _build(self):
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=28, pady=20)

        # ── タイトルバー ────────────────────────────────────
        title_row = ctk.CTkFrame(root, fg_color="transparent")
        title_row.pack(fill="x", pady=(0, 20))

        title_lbl = ctk.CTkLabel(
            title_row, text="英検単語マスター",
            font=ctk.CTkFont("Yu Gothic UI", 28, "bold"),
            text_color=NEON_CYAN,
        )
        title_lbl.pack(side="left")

        # レベル選択をタイトル右に
        lv_var = ctk.StringVar(value="2級")
        lv_frame = ctk.CTkFrame(title_row, fg_color=BG_CARD, corner_radius=20)
        lv_frame.pack(side="right", padx=4)
        for lv in ("2級", "準1級"):
            ctk.CTkRadioButton(
                lv_frame, text=f"英検{lv}", variable=lv_var, value=lv,
                font=ctk.CTkFont("Yu Gothic UI", 13),
                fg_color=NEON_CYAN, border_color=NEON_CYAN,
                hover_color=BG_CARD2,
            ).pack(side="left", padx=16, pady=8)

        # ── 上段：進捗カード ────────────────────────────────
        prog_card = ctk.CTkFrame(root, fg_color=BG_CARD, corner_radius=16)
        prog_card.pack(fill="x", pady=(0, 16))
        prog_inner = ctk.CTkFrame(prog_card, fg_color="transparent")
        prog_inner.pack(fill="x", padx=20, pady=16)

        # 上行
        top_row = ctk.CTkFrame(prog_inner, fg_color="transparent")
        top_row.pack(fill="x")
        ctk.CTkLabel(top_row, text="バッチ 1 / 4",
                     font=ctk.CTkFont("Yu Gothic UI", 18, "bold"),
                     text_color="#ffffff").pack(side="left")
        ctk.CTkLabel(top_row, text="英検2級",
                     font=ctk.CTkFont("Yu Gothic UI", 13),
                     text_color=TEXT_DIM).pack(side="left", padx=12)
        ctk.CTkLabel(top_row, text="習得済み  23 / 100",
                     font=ctk.CTkFont("Yu Gothic UI", 13),
                     text_color=NEON_CYAN).pack(side="right")

        # プログレスバー（グロー風）
        ctk.CTkFrame(prog_inner, height=1, fg_color="#1e1e3a").pack(fill="x", pady=10)
        bar = ctk.CTkProgressBar(prog_inner, height=12, corner_radius=6,
                                 fg_color="#1a1a2e", progress_color=NEON_CYAN)
        bar.set(0.23)
        bar.pack(fill="x")
        ctk.CTkLabel(prog_inner, text="23%",
                     font=ctk.CTkFont("Yu Gothic UI", 11),
                     text_color=NEON_CYAN).pack(anchor="e", pady=(4, 0))

        # ── 中段：アクションボタン ──────────────────────────
        btn_row = ctk.CTkFrame(root, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 16))
        btn_row.columnconfigure((0, 1, 2), weight=1)

        # クイズ開始（シアン光彩風）
        quiz_btn = ctk.CTkButton(
            btn_row, text="▶  クイズ開始",
            height=56, corner_radius=12,
            font=ctk.CTkFont("Yu Gothic UI", 15, "bold"),
            fg_color=NEON_CYAN, hover_color="#00b8cc",
            text_color="#000000",
        )
        quiz_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        # 集中特訓（パープル）
        drill_btn = ctk.CTkButton(
            btn_row, text="⚡ 集中特訓",
            height=56, corner_radius=12,
            font=ctk.CTkFont("Yu Gothic UI", 15, "bold"),
            fg_color=NEON_PURPLE, hover_color="#8a30d0",
            text_color="#ffffff",
        )
        drill_btn.grid(row=0, column=1, padx=5, sticky="ew")

        # 次のバッチ（グレーアウト）
        next_btn = ctk.CTkButton(
            btn_row, text="次バッチへ →",
            height=56, corner_radius=12,
            font=ctk.CTkFont("Yu Gothic UI", 14),
            fg_color=BG_CARD2, hover_color=BG_CARD2,
            text_color=TEXT_DIM,
            state="disabled",
        )
        next_btn.grid(row=0, column=2, padx=(10, 0), sticky="ew")

        # ── 集中特訓 しきい値設定 ───────────────────────────
        thresh_card = ctk.CTkFrame(root, fg_color=BG_CARD, corner_radius=14)
        thresh_card.pack(fill="x", pady=(0, 16))
        th_inner = ctk.CTkFrame(thresh_card, fg_color="transparent")
        th_inner.pack(fill="x", padx=20, pady=14)
        ctk.CTkLabel(th_inner, text="集中特訓モード　設定",
                     font=ctk.CTkFont("Yu Gothic UI", 13, "bold"),
                     text_color=NEON_PURPLE).pack(anchor="w", pady=(0, 8))
        th_row = ctk.CTkFrame(th_inner, fg_color="transparent")
        th_row.pack(anchor="w")
        ctk.CTkLabel(th_row, text="間違い回数 ≥",
                     font=ctk.CTkFont("Yu Gothic UI", 13),
                     text_color="#ccc").pack(side="left")
        ctk.CTkEntry(th_row, width=56, placeholder_text="3",
                     font=ctk.CTkFont("Yu Gothic UI", 13),
                     border_color=NEON_PURPLE, fg_color=BG_CARD2,
                     text_color="#fff").pack(side="left", padx=10)
        ctk.CTkLabel(th_row, text="回",
                     font=ctk.CTkFont("Yu Gothic UI", 13),
                     text_color="#ccc").pack(side="left")
        ctk.CTkButton(th_row, text="開始", width=80, height=32,
                      corner_radius=8,
                      font=ctk.CTkFont("Yu Gothic UI", 13),
                      fg_color=NEON_PURPLE, hover_color="#8a30d0"
                      ).pack(side="left", padx=14)

        # ── 下段：一覧ボタン ────────────────────────────────
        list_row = ctk.CTkFrame(root, fg_color="transparent")
        list_row.pack(fill="x")
        list_row.columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            list_row, text="⭐  習得済み単語一覧", height=46,
            font=ctk.CTkFont("Yu Gothic UI", 13),
            fg_color="#1a2a1a", hover_color="#243324",
            text_color=NEON_GREEN, corner_radius=12,
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")
        ctk.CTkButton(
            list_row, text="📉  苦手単語一覧", height=46,
            font=ctk.CTkFont("Yu Gothic UI", 13),
            fg_color="#2a1a1a", hover_color="#332424",
            text_color="#ff6b6b", corner_radius=12,
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

SampleHome().mainloop()
