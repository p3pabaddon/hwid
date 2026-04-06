import customtkinter as ctk
import threading
import subprocess
import winreg
import uuid
import random
import os
import sys
import shutil
import ctypes
import time
import json
import hashlib
import base64
from datetime import datetime
from PIL import Image, ImageTk

# Local Imports
from engine import SpoofEngine, TraceAnalyzer
from license_manager import LicenseManager

# Set AppID for Taskbar Icon Support on Windows
try:
    myappid = 'solutions.spoofer.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

# --- Localization ---
TRANSLATIONS = {
    "tr": {
        "login_title": "Solutions Lisans Girişi",
        "entry_placeholder": "Lisans anahtarınızı girin",
        "login_btn": "GİRİŞ YAP",
        "login_msg": "Lisans doğrulandı • Hazır",
        "h_info": "SİSTEM BİLGİLERİ",
        "ready": "Sistem Hazır",
        "unban_btn": "⚡  UNBAN (SPOOF)",
        "restart_msg": "İşlem sonrası bilgisayarı yeniden başlatın",
        "disk": "Disk",
        "motherboard": "Anakart",
        "mac": "Ağ (MAC)",
        "gpu": "GPU Kimliği",
        "logout": "Çıkış Yap",
        "admin": "Yönetici Paneli",
        "keys": "Lisans Anahtarı",
        "stats": "İstatistikler",
        "invalid_key": "Geçersiz anahtar kodu!",
        "expired": "Lisans süresi dolmuş!",
        "already_used": "Bu anahtar başka bir PC'ye kayıtlı!",
        "unban_running": "Unban işlemi başlatıldı...",
        "completed": "İşlem başarıyla tamamlandı!",
        "bios": "BIOS Seri No",
        "cpu": "İşlemci ID",
        "clean_val": "Valorant Temizle",
        "clean_fivem": "FiveM Temizle",
        "clean_apex": "Apex Temizle",
        "clean_ab": "Arena Breakout Temizle",
        "clean_df": "Delta Force Temizle",
        "m_original": "Orijinal",
        "m_current": "Şu Anki",
        "trace_tool": "İz Analizi",
        "trace_title": "İz Analiz Aracı",
        "trace_tool": "İz Analizi",
        "trace_title": "İz Analiz Aracı",
        "trace_scan": "İZLERİ TARA",
        "trace_clean": "İZLERİ TEMİZLE",
        "trace_none": "İz bulunmadı. Sistem temiz.",
        "trace_found": "İzler tespit edildi!",
        "trace_cleaning": "İzler temizleniyor...",
        "trace_done": "İzler başarıyla temizlendi."
    },
    "en": {
        "login_title": "Solutions License Login",
        "entry_placeholder": "Enter your license key",
        "login_btn": "ACTIVATE",
        "login_msg": "License verified • Ready",
        "h_info": "SYSTEM INFORMATION",
        "ready": "System Ready",
        "unban_btn": "⚡  UNBAN (SPOOF)",
        "restart_msg": "Restart your PC after the operation",
        "disk": "Disk",
        "motherboard": "Motherboard",
        "mac": "Network (MAC)",
        "gpu": "GPU ID",
        "logout": "Logout",
        "admin": "Admin Panel",
        "keys": "License Key",
        "stats": "Statistics",
        "invalid_key": "Invalid license key!",
        "expired": "License expired!",
        "already_used": "Key already tied to another PC!",
        "unban_running": "Unban in progress...",
        "completed": "Task completed successfully!",
        "bios": "BIOS Serial",
        "cpu": "Processor ID",
        "clean_val": "Clean Valorant",
        "clean_fivem": "Clean FiveM",
        "clean_apex": "Clean Apex",
        "clean_ab": "Clean Arena Breakout",
        "clean_df": "Clean Delta Force",
        "m_original": "Original",
        "m_current": "Current",
        "pro_features": "Pro Features",
        "raid_sim": "RAID0 Simulation",
        "fps_boost": "FPS & Stealth Boost",
        "sys_health": "System Health",
        "optimizing": "Optimizing system...",
        "opt_done": "Optimization completed!",
        "stealth_lvl": "Stealth Level",
        "trace_tool": "Trace Analysis",
        "trace_title": "Trace Analysis Tool",
        "trace_scan": "SCAN TRACES",
        "trace_clean": "CLEAN TRACES",
        "trace_none": "No traces found. System is clean.",
        "trace_found": "Traces detected!",
        "trace_cleaning": "Cleaning traces...",
        "trace_done": "Traces cleaned successfully."
    },
    "ru": {
        "login_title": "Solutions Вход по лицензии",
        "entry_placeholder": "Введите код лицензии",
        "login_btn": "АКТИВИРОВАТЬ",
        "login_msg": "Лицензия подтверждена • Готово",
        "h_info": "ИНФОРМАЦИЯ О СИСТЕМЕ",
        "ready": "Система готова",
        "unban_btn": "⚡  РАЗБАНИТЬ (SPOOF)",
        "restart_msg": "Перезагрузите ПК после завершения",
        "disk": "Диск",
        "motherboard": "Мат. плата",
        "mac": "Сеть (MAC)",
        "gpu": "GPU ID",
        "logout": "Выход",
        "admin": "Админ-панель",
        "keys": "Лицензионный ключ",
        "stats": "Статистика",
        "invalid_key": "Неверный код ключа!",
        "expired": "Срок лицензии истек!",
        "already_used": "Ключ уже привязан к другому ПК!",
        "unban_running": "Запущена разблокировка...",
        "completed": "Операция успешно завершена!",
        "bios": "BIOS Seri No",
        "cpu": "Processor ID",
        "clean_val": "Очистить Valorant",
        "clean_fivem": "Очистить FiveM",
        "clean_apex": "Очистить Apex",
        "clean_ab": "Очистить Arena Breakout",
        "clean_df": "Очистить Delta Force",
        "m_original": "Оригинал",
        "m_current": "Текущий",
        "trace_tool": "Анализ следов",
        "trace_title": "Инструмент анализа следов",
        "trace_scan": "СКАНИРОВАТЬ",
        "trace_clean": "ОЧИСТИТЬ СЛЕДЫ",
        "trace_none": "Следов не найдено. Система чиста.",
        "trace_found": "Обнаружены следы!",
        "trace_cleaning": "Очистка следов...",
        "trace_done": "Следы успешно очищены."
    }
}


# ============================================================
#                    GUI APPLICATION
# ============================================================

# Color palette
BG_DARK = "#0a0a14"
BG_CARD = "#111122"
BG_CARD_HOVER = "#161633"
ACCENT = "#7c3aed"
ACCENT_HOVER = "#6d28d9"
ACCENT_GLOW = "#a78bfa"
SUCCESS = "#10b981"
ERROR = "#ef4444"
WARNING = "#f59e0b"
TEXT_PRIMARY = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"
TEXT_DIM = "#475569"
BORDER = "#1e1b4b"
BORDER_LIGHT = "#312e81"


class LoginScreen(ctk.CTkFrame):
    """License key entry screen for customers."""

    def __init__(self, master, on_success, on_admin):
        super().__init__(master, fg_color=BG_DARK)
        self.on_success = on_success
        self.on_admin = on_admin
        self.lm = master.license_manager
        self.build()

    def build(self):
        # ---- Language Selector ----
        lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        lang_frame.pack(side="top", anchor="ne", padx=20, pady=10)
        
        for l_code, l_label in [("TR", "tr"), ("EN", "en"), ("RU", "ru")]:
            btn = ctk.CTkButton(lang_frame, text=l_code, width=35, height=22, corner_radius=6,
                                font=ctk.CTkFont(size=10, weight="bold"),
                                fg_color=BG_CARD if self.master.lang != l_label else ACCENT,
                                hover_color=ACCENT_HOVER,
                                command=lambda l=l_label: self.master.switch_lang(l))
            btn.pack(side="left", padx=2)

        # ---- Glow Top ----
        glow = ctk.CTkFrame(self, height=3, fg_color=ACCENT, corner_radius=0)
        glow.pack(fill="x")

        # ---- Spacer ----
        ctk.CTkLabel(self, text="", fg_color=BG_DARK, height=20).pack()

        # ---- Logo ----
        if self.master.logo:
            logo_label = ctk.CTkLabel(self, image=self.master.logo, text="")
            logo_label.pack(pady=(20, 0))
        else:
            ctk.CTkLabel(self, text="🛡️", font=ctk.CTkFont(size=48)).pack()

        # ---- Title ----
        ctk.CTkLabel(
            self, text="HWID SPOOFER",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(pady=(12, 0))

        ctk.CTkLabel(
            self, text=self.master.get_text("login_title"),
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT_SECONDARY
        ).pack(pady=(4, 0))

        # ---- Key Input Card ----
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=16,
                            border_width=1, border_color=BORDER)
        card.pack(padx=50, pady=(40, 0), fill="x")

        ctk.CTkLabel(
            card, text=self.master.get_text("keys"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_DIM, anchor="w"
        ).pack(padx=20, pady=(16, 4), anchor="w")

        self.key_entry = ctk.CTkEntry(
            card, height=48, corner_radius=10,
            font=ctk.CTkFont(family="Consolas", size=16),
            fg_color="#0d0d1f", border_color=BORDER_LIGHT,
            text_color=TEXT_PRIMARY, border_width=1,
            placeholder_text="XXXX-XXXX-XXXX-XXXX",
            justify="center"
        )
        self.key_entry.pack(padx=20, fill="x")
        self.key_entry.bind("<Return>", lambda e: self.validate())

        self.error_label = ctk.CTkLabel(
            card, text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=ERROR, height=20
        )
        self.error_label.pack(pady=(4, 0))

        # ---- Activate Button ----
        self.activate_btn = ctk.CTkButton(
            card, text=self.master.get_text("login_btn"), height=48, corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            command=self.validate
        )
        self.activate_btn.pack(padx=20, fill="x", pady=(12, 20))

        # ---- Admin Link ----
        admin_btn = ctk.CTkButton(
            self, text=self.master.get_text("admin"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="transparent", hover_color=BG_CARD,
            text_color=TEXT_DIM, height=30,
            command=self.on_admin
        )
        admin_btn.pack(pady=(30, 0))

        # ---- Footer ----
        ctk.CTkLabel(
            self, text="Tek kullanımlık lisans sistemi",
            font=ctk.CTkFont(size=10), text_color=TEXT_DIM
        ).pack(side="bottom", pady=16)

    def validate(self):
        key = self.key_entry.get().strip().upper()
        if not key:
            self.error_label.configure(text="Lütfen bir anahtar girin!")
            return

        valid, msg = self.lm.validate_key(key)
        if valid:
            self.error_label.configure(text="✓ Anahtar doğrulandı!", text_color=SUCCESS)
            self.activate_btn.configure(state="disabled", fg_color=SUCCESS, text="✓")
            self.after(800, lambda: self.on_success(key))
        else:
            self.error_label.configure(text=msg, text_color=ERROR)
            self.key_entry.configure(border_color=ERROR)
            self.after(2000, lambda: self.key_entry.configure(border_color=BORDER_LIGHT))


class AdminLoginScreen(ctk.CTkFrame):
    """Admin credentials screen."""

    def __init__(self, master, on_success, on_back):
        super().__init__(master, fg_color=BG_DARK)
        self.on_success = on_success
        self.on_back = on_back
        self.lm = master.license_manager
        self.build()

    def build(self):
        glow = ctk.CTkFrame(self, height=3, fg_color=WARNING, corner_radius=0)
        glow.pack(fill="x")

        ctk.CTkLabel(self, text="", fg_color=BG_DARK, height=50).pack()

        ctk.CTkLabel(
            self, text="⚙", font=ctk.CTkFont(size=40)
        ).pack()

        ctk.CTkLabel(
            self, text="YÖNETİCİ GİRİŞİ",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(pady=(10, 0))

        ctk.CTkLabel(
            self, text="Sadece yetkili kişiler için",
            font=ctk.CTkFont(size=12), text_color=TEXT_SECONDARY
        ).pack(pady=(4, 0))

        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=16,
                            border_width=1, border_color=BORDER)
        card.pack(padx=50, pady=(30, 0), fill="x")

        ctk.CTkLabel(card, text="Kullanıcı Adı", font=ctk.CTkFont(size=11),
                     text_color=TEXT_DIM, anchor="w").pack(padx=20, pady=(16, 4), anchor="w")
        self.user_entry = ctk.CTkEntry(
            card, height=42, corner_radius=10, font=ctk.CTkFont(size=14),
            fg_color="#0d0d1f", border_color=BORDER_LIGHT, text_color=TEXT_PRIMARY, border_width=1
        )
        self.user_entry.pack(padx=20, fill="x")

        ctk.CTkLabel(card, text="Şifre", font=ctk.CTkFont(size=11),
                     text_color=TEXT_DIM, anchor="w").pack(padx=20, pady=(12, 4), anchor="w")
        self.pass_entry = ctk.CTkEntry(
            card, height=42, corner_radius=10, font=ctk.CTkFont(size=14),
            fg_color="#0d0d1f", border_color=BORDER_LIGHT, text_color=TEXT_PRIMARY,
            border_width=1, show="•"
        )
        self.pass_entry.pack(padx=20, fill="x")
        self.pass_entry.bind("<Return>", lambda e: self.login())

        self.err = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=11),
                                text_color=ERROR, height=18)
        self.err.pack(pady=(6, 0))

        ctk.CTkButton(
            card, text="GİRİŞ YAP", height=44, corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=WARNING, hover_color="#d97706", text_color="#000",
            command=self.login
        ).pack(padx=20, fill="x", pady=(10, 20))

        ctk.CTkButton(
            self, text="← Geri Dön", font=ctk.CTkFont(size=12),
            fg_color="transparent", hover_color=BG_CARD,
            text_color=TEXT_DIM, command=self.on_back
        ).pack(pady=(20, 0))

    def login(self):
        u = self.user_entry.get().strip()
        p = self.pass_entry.get().strip()
        if self.lm.verify_admin(u, p):
            self.on_success()
        else:
            self.err.configure(text="Geçersiz kullanıcı adı veya şifre!")
            self.pass_entry.delete(0, "end")


class AdminPanel(ctk.CTkFrame):
    """Admin panel for generating and managing license keys."""

    def __init__(self, master, on_back):
        super().__init__(master, fg_color=BG_DARK)
        self.on_back = on_back
        self.lm = master.license_manager
        self.build()

    def build(self):
        glow = ctk.CTkFrame(self, height=3, fg_color=WARNING, corner_radius=0)
        glow.pack(fill="x")

        # ---- Header ----
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 0))

        ctk.CTkButton(
            header, text="← " + self.master.get_text("logout"), width=80, height=32, corner_radius=8,
            font=ctk.CTkFont(size=12), fg_color=BG_CARD,
            hover_color=BG_CARD_HOVER, text_color=TEXT_SECONDARY,
            command=self.on_back
        ).pack(side="left")

        ctk.CTkLabel(
            header, text=self.master.get_text("admin").upper(),
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="right")

        # ---- Stats ----
        total, used, available = self.lm.get_stats()
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(padx=30, pady=(20, 0), fill="x")

        for val, label, color in [
            (str(total), "Toplam", TEXT_SECONDARY),
            (str(used), "Kullanılmış", ERROR),
            (str(available), "Aktif", SUCCESS)
        ]:
            stat_card = ctk.CTkFrame(stats_frame, fg_color=BG_CARD, corner_radius=12,
                                      border_width=1, border_color=BORDER)
            stat_card.pack(side="left", expand=True, fill="x", padx=4)
            ctk.CTkLabel(stat_card, text=val, font=ctk.CTkFont(size=22, weight="bold"),
                         text_color=color).pack(pady=(12, 0))
            ctk.CTkLabel(stat_card, text=label, font=ctk.CTkFont(size=10),
                         text_color=TEXT_DIM).pack(pady=(0, 10))

        # ---- Duration Selection ----
        ctk.CTkLabel(
            self, text="Lisans Süresi", font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_SECONDARY, anchor="w"
        ).pack(padx=30, pady=(20, 6), anchor="w")

        duration_frame = ctk.CTkFrame(self, fg_color="transparent")
        duration_frame.pack(padx=30, fill="x")

        self.duration_var = ctk.StringVar(value="0") # 0 = Lifetime
        self.pro_var = ctk.BooleanVar(value=True) # Default to PRO keys
        durations = [("Tek", "-1"), ("1G", "1"), ("7G", "7"), ("30G", "30"), ("Sın.", "0")]
        for text, val in durations:
            rb = ctk.CTkRadioButton(
                duration_frame, text=text, variable=self.duration_var, value=val,
                font=ctk.CTkFont(size=10), fg_color=ACCENT, border_color=BORDER_LIGHT,
                hover_color=ACCENT_HOVER, width=65
            )
            rb.pack(side="left", padx=2)

        # ---- Pro Toggle ----
        pro_frame = ctk.CTkFrame(self, fg_color="transparent")
        pro_frame.pack(padx=30, pady=(10, 0), fill="x")
        
        self.pro_switch = ctk.CTkSwitch(
            pro_frame, text="Professional Sürüm (Özellikleri Açar)", 
            variable=self.pro_var,
            font=ctk.CTkFont(size=11, weight="bold"),
            progress_color=ACCENT, text_color=TEXT_SECONDARY
        )
        self.pro_switch.pack(side="left")

        # ---- Custom Key Entry ----
        ctk.CTkLabel(
            self, text="Özel Anahtar (Opsiyonel)", font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_DIM, anchor="w"
        ).pack(padx=30, pady=(10, 2), anchor="w")
        
        self.custom_key_entry = ctk.CTkEntry(
            self, height=32, corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=BG_CARD, border_color=BORDER,
            placeholder_text="Örn: ADMIN-KEY-2024"
        )
        self.custom_key_entry.pack(padx=30, fill="x", pady=(0, 10))

        # ---- Generate Button ----
        ctk.CTkButton(
            self, text="+ YENİ ANAHTAR OLUŞTUR", height=48, corner_radius=12,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            command=self.generate_key
        ).pack(padx=30, fill="x", pady=(20, 0))

        self.err_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11), text_color=ERROR)
        self.err_label.pack(pady=(2, 0))

        self.new_key_entry = ctk.CTkEntry(
            self, font=ctk.CTkFont(family="Consolas", size=16),
            text_color=ACCENT_GLOW, height=32, width=300,
            fg_color="transparent", border_width=0, justify="center"
        )
        self.new_key_entry.pack(pady=(8, 0))

        # ---- Key List ----
        ctk.CTkLabel(
            self, text="Anahtarlar", font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_SECONDARY, anchor="w"
        ).pack(padx=30, pady=(16, 6), anchor="w")

        list_frame = ctk.CTkScrollableFrame(
            self, fg_color=BG_CARD, corner_radius=12,
            border_width=1, border_color=BORDER, height=220
        )
        list_frame.pack(padx=30, fill="both", expand=True, pady=(0, 20))

        keys = self.lm.get_all_keys()
        if not keys:
            ctk.CTkLabel(list_frame, text="Henüz anahtar yok",
                         font=ctk.CTkFont(size=12), text_color=TEXT_DIM).pack(pady=30)
        else:
            for entry in reversed(keys):
                row = ctk.CTkFrame(list_frame, fg_color="transparent", height=36)
                row.pack(fill="x", padx=8, pady=2)

                status_color = ERROR if entry["used"] else SUCCESS
                status_text = "●"

                ctk.CTkLabel(row, text=status_text, font=ctk.CTkFont(size=10),
                             text_color=status_color, width=20).pack(side="left")
                
                key_box = ctk.CTkEntry(row, height=28, border_width=0,
                                       font=ctk.CTkFont(family="Consolas", size=11),
                                       fg_color="transparent",
                                       text_color=TEXT_PRIMARY if not entry["used"] else TEXT_DIM,
                                       width=180) # Corrected: width in constructor
                key_box.insert(0, entry["key"])
                key_box.configure(state="readonly")
                key_box.pack(side="left", padx=(4, 0)) # Corrected: width removed from pack

                # Duration/Expiry info
                expiry_str = entry.get("expiry", "")
                
                if expiry_str:
                    try:
                        exp_dt = datetime.fromisoformat(expiry_str)
                        rem = exp_dt.timestamp() - time.time()
                        if rem > 0:
                            hrs = int(rem / 3600)
                            rem_text = f"{hrs}h" if hrs < 48 else f"{int(rem/86400)}d"
                        else:
                            rem_text = "EXPIRED"
                    except:
                        rem_text = "∞"
                else:
                    rem_text = "∞"
                
                ctk.CTkLabel(row, text=rem_text, font=ctk.CTkFont(size=9),
                             text_color=WARNING if rem_text == "EXPIRED" else ACCENT_GLOW, width=35).pack(side="left", padx=2)

                if entry.get("is_pro"):
                    ctk.CTkLabel(row, text="[PRO]", font=ctk.CTkFont(size=9, weight="bold"),
                                 text_color=ACCENT_GLOW).pack(side="left", padx=2)

                hwid_txt = (entry.get("hwid") or "")[:8]
                if hwid_txt:
                    ctk.CTkLabel(row, text=f"[{hwid_txt}]", font=ctk.CTkFont(size=9),
                                 text_color=TEXT_DIM).pack(side="right", padx=5)

    def generate_key(self):
        try:
            val = int(self.duration_var.get())
            is_pro = self.pro_var.get()
            custom = self.custom_key_entry.get().strip() or None
            
            key = self.lm.generate_key(duration_days=val, is_pro=is_pro, custom_key=custom)
            
            if "ERROR" in key:
                self.err_label.configure(text=f"Hata: {key}")
                return

            self.err_label.configure(text="")
            self.new_key_entry.configure(state="normal")
            self.new_key_entry.delete(0, "end")
            self.new_key_entry.insert(0, f"🔑 {key}")
            self.new_key_entry.configure(state="readonly")
            
            # Copy to clipboard
            self.clipboard_clear()
            self.clipboard_append(key)
            
            # Rebuild to update stats and list
            self.after(1200, self.refresh)
        except Exception as e:
            self.err_label.configure(text=f"Hata: {str(e)}")

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self.build()


class SpooferScreen(ctk.CTkFrame):
    """Main spoofer screen with UNBAN button."""

    def __init__(self, master, on_logout, key):
        super().__init__(master, fg_color=BG_DARK)
        self.on_logout = on_logout
        self.key = key
        self.engine = SpoofEngine(
            os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, 'frozen', False)
            else os.path.dirname(sys.executable)
        )
        self.engine.status_callback = lambda t: self.after(0, self._set_status, t)
        self.engine.progress_callback = lambda v: self.after(0, self._set_progress, v)
        self.running = False
        self.key_info = self.master.license_manager.get_key_info(key)
        self.is_pro = self.key_info.get("is_pro", False) if self.key_info else False
        self.original_info = self.engine.get_hardware_info()
        self.build()

    def build(self):
        glow = ctk.CTkFrame(self, height=3, fg_color=SUCCESS, corner_radius=0)
        glow.pack(fill="x")

        # ---- Main Container (Two Columns) ----
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, pady=(20, 0))

        left_col = ctk.CTkFrame(container, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(40, 20))

        right_col = ctk.CTkFrame(container, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True, padx=(20, 40))

        # ---- LEFT COLUMN: Branding & HW Info ----
        # Logo
        if self.master.logo:
            logo_label = ctk.CTkLabel(left_col, image=self.master.logo, text="")
            logo_label.pack(pady=(12, 0))
        else:
            ctk.CTkLabel(left_col, text="🛡️", font=ctk.CTkFont(size=52)).pack(pady=(10, 0))

        ctk.CTkLabel(
            left_col, text="HWID SPOOFER",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(pady=(8, 0))

        ctk.CTkLabel(
            left_col, text=self.master.get_text("login_msg"),
            font=ctk.CTkFont(size=11), text_color=SUCCESS
        ).pack(pady=(0, 10))

        # Logout Link (Top Left)
        ctk.CTkButton(
            self, text="🚪 " + self.master.get_text("logout"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="transparent", hover_color=BG_CARD,
            text_color=TEXT_DIM, height=24, width=80,
            command=self.on_logout
        ).place(x=10, y=10)

        # Feature Chips
        chips = ctk.CTkFrame(left_col, fg_color="transparent")
        chips.pack(pady=(10, 0))
        for icon, txt in [("🔒", "17 Spoof"), ("🛡️", "6 AC"), ("🌐", "VPN")]:
            c = ctk.CTkFrame(chips, fg_color=BG_CARD, corner_radius=20,
                             border_width=1, border_color=BORDER)
            c.pack(side="left", padx=3)
            ctk.CTkLabel(c, text=f"{icon} {txt}", font=ctk.CTkFont(size=10),
                         text_color=TEXT_SECONDARY).pack(padx=10, pady=5)

        # Hardware Info Card
        hw_card = ctk.CTkFrame(left_col, fg_color=BG_CARD, corner_radius=14,
                                border_width=1, border_color=BORDER)
        hw_card.pack(fill="x", pady=(25, 0))

        hw_header = ctk.CTkFrame(hw_card, fg_color="transparent")
        hw_header.pack(fill="x", padx=10, pady=(5, 0))
        
        ctk.CTkLabel(hw_header, text=self.master.get_text("h_info"), 
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_DIM).pack(side="left")
        
        ctk.CTkButton(hw_header, text="🔄", width=20, height=20, corner_radius=5,
                      fg_color="transparent", hover_color=BG_CARD_HOVER,
                      command=self.update_hw_info).pack(side="right")

        hw_inner = ctk.CTkFrame(hw_card, fg_color="transparent")
        hw_inner.pack(fill="x", padx=15, pady=(0, 15))

        self.hw_labels = {}
        for i, (key, label) in enumerate([("disk", "Disk"), ("motherboard", "Board"), 
                                         ("mac", "MAC"), ("gpu", "GPU"),
                                         ("bios", "BIOS"), ("cpu", "CPU")]):
            lbl = ctk.CTkLabel(hw_inner, text=f"{label}: --", 
                               font=ctk.CTkFont(family="Consolas", size=10),
                               text_color=TEXT_SECONDARY, anchor="w")
            lbl.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            self.hw_labels[key] = lbl
        
        self.original_info = self.engine.get_hardware_info()
        self.update_hw_info()

        # ---- RIGHT COLUMN: Cleaners & Actions ----
        # Cleaner Section (taking more space)
        clean_card = ctk.CTkFrame(right_col, fg_color=BG_CARD, corner_radius=14,
                                   border_width=1, border_color=BORDER)
        clean_card.pack(fill="both", expand=True, pady=(10, 0))
        
        ctk.CTkLabel(clean_card, text="DEEP CLEANER", 
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_DIM).pack(pady=(12, 0))

        clean_btns = ctk.CTkFrame(clean_card, fg_color="transparent")
        clean_btns.pack(fill="both", expand=True, padx=20, pady=(10, 15))

        games = ["clean_val", "clean_fivem", "clean_apex", "clean_ab", "clean_df"]
        
        for i, cmd_key in enumerate(games):
            row = i // 2
            col = i % 2
            
            frame = ctk.CTkFrame(clean_btns, fg_color="transparent")
            if i == 4: # Delta Force (lone element)
                frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(8, 0))
            else:
                frame.grid(row=row, column=col, sticky="ew", padx=8, pady=8)
            
            btn = ctk.CTkButton(frame, text=self.master.get_text(cmd_key), 
                                width=140, height=42, 
                                corner_radius=12, fg_color="#0f172a", 
                                font=ctk.CTkFont(size=11, weight="bold"),
                                hover_color=BG_CARD_HOVER, border_width=1, 
                                border_color=BORDER_LIGHT,
                                command=lambda g=cmd_key: threading.Thread(target=self.engine.deep_clean_game, args=(g,), daemon=True).start())
            btn.pack(expand=True)

        for c in range(2): clean_btns.grid_columnconfigure(c, weight=1)

        # Status & Action Area
        action_area = ctk.CTkFrame(right_col, fg_color="transparent")
        action_area.pack(fill="x", pady=(20, 0))

        self.status_card = ctk.CTkFrame(action_area, fg_color=BG_CARD, corner_radius=12,
                                         border_width=1, border_color=BORDER)
        self.status_card.pack(fill="x")

        status_inner = ctk.CTkFrame(self.status_card, fg_color="transparent")
        status_inner.pack(fill="x", padx=16, pady=12)

        self.status_dot = ctk.CTkLabel(status_inner, text="◉", font=ctk.CTkFont(size=12),
                                        text_color=SUCCESS, width=20)
        self.status_dot.pack(side="left")

        self.status_label = ctk.CTkLabel(status_inner, text=self.master.get_text("ready"),
                                          font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_PRIMARY,
                                          anchor="w")
        self.status_label.pack(side="left", fill="x", expand=True, padx=(6, 0))

        # ---- Pro Features (New) ----
        if self.is_pro:
            self.pro_panel = ProFeaturesFrame(right_col, self.engine)
            self.pro_panel.pack(fill="x", pady=(20, 0))

        # Progress
        prog_frame = ctk.CTkFrame(action_area, fg_color="transparent")
        prog_frame.pack(fill="x", pady=(15, 0))

        self.progress = ctk.CTkProgressBar(prog_frame, height=8, corner_radius=4,
                                            fg_color="#1a1a2e", progress_color=ACCENT)
        self.progress.pack(fill="x")
        self.progress.set(0)

        self.pct_label = ctk.CTkLabel(prog_frame, text="0%", font=ctk.CTkFont(size=11),
                                       text_color=TEXT_DIM)
        self.pct_label.pack(anchor="e", pady=(2, 0))

        # UNBAN Button
        self.unban_btn = ctk.CTkButton(
            action_area, text=self.master.get_text("unban_btn"), height=48, corner_radius=14,
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            command=self.on_unban
        )
        self.unban_btn.pack(fill="x", pady=(15, 0))

        # Trace Analysis Tool Button
        self.trace_btn = ctk.CTkButton(
            action_area, text="🔍 " + self.master.get_text("trace_tool"), height=40, corner_radius=12,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0f172a", border_width=1, border_color=BORDER_LIGHT,
            hover_color=BG_CARD_HOVER,
            command=self.open_trace_tool
        )
        self.trace_btn.pack(fill="x", pady=(10, 0))

        # Warning & Footer
        ctk.CTkLabel(
            right_col, text="⚠ " + self.master.get_text("restart_msg"),
            font=ctk.CTkFont(size=11), text_color=TEXT_DIM
        ).pack(pady=(12, 5))

        ctk.CTkLabel(self, text="v2.1 Professional Edition", font=ctk.CTkFont(size=9),
                     text_color="#1e1b4b").pack(side="bottom", pady=5)

    def open_trace_tool(self):
        TraceAnalysisWindow(self.master, self.engine)

    def update_hw_info(self):
        def _fetch():
            info = self.engine.get_hardware_info()
            self.after(0, lambda: self._apply_hw_info(info))
        threading.Thread(target=_fetch, daemon=True).start()

    def _apply_hw_info(self, info):
        for key, val in info.items():
            if key in self.hw_labels:
                orig = self.original_info.get(key, "--")[:10]
                curr = info.get(key, "--")[:10]
                label_name = {"disk": self.master.get_text("disk"), 
                              "motherboard": self.master.get_text("motherboard"), 
                              "mac": self.master.get_text("mac"), 
                              "gpu": self.master.get_text("gpu"),
                              "bios": self.master.get_text("bios"),
                              "cpu": self.master.get_text("cpu")}[key]
                
                status_color = SUCCESS if orig != curr and curr != "N/A" else TEXT_SECONDARY
                arrow = " -> " if orig != curr else " | "
                self.hw_labels[key].configure(text=f"{label_name}: {orig}{arrow}{curr}", text_color=status_color)

    def _set_status(self, text):
        try:
            self.status_label.configure(text=text)
        except:
            pass

    def _set_progress(self, val):
        try:
            self.progress.set(val)
            self.pct_label.configure(text=f"{int(val * 100)}%")
        except:
            pass

    def on_unban(self):
        if self.running:
            return
        self.running = True
        # Bind and consume license usage ONLY NOW
        self.master.license_manager.consume_key(self.key)
        self.master.license_manager.consume_spoof(self.key)
        
        self.unban_btn.configure(state="disabled", fg_color="#3a3a5a", text="İşleniyor...")
        self.status_dot.configure(text_color=WARNING)
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            self.engine.execute_all()
            self.after(1000, self.update_hw_info) # Refresh info after spoof
            self.after(0, self._done, True)
        except Exception as e:
            self.after(0, self._done, False, str(e))

    def _done(self, ok, err=None):
        self.running = False
        if ok:
            self.unban_btn.configure(fg_color=SUCCESS, text="✓ TAMAMLANDI", state="disabled")
            self.status_dot.configure(text_color=SUCCESS)
            self._set_status("Tüm işlemler başarıyla tamamlandı!")
        else:
            self.unban_btn.configure(fg_color=ERROR, text="HATA!", state="normal")
            self.status_dot.configure(text_color=ERROR)
            self._set_status(f"Hata: {err}")
            self.after(4000, self._reset_btn)

    def _reset_btn(self):
        self.unban_btn.configure(fg_color=ACCENT, hover_color=ACCENT_HOVER, text="⚡  UNBAN")


class DashboardGraphics(ctk.CTkCanvas):
    """Visual representation of system health and spoof status."""
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=BG_CARD, highlightthickness=0, **kwargs)
        self.metrics_data = {}
        self.draw()

    def update(self, metrics_data):
        self.metrics_data = metrics_data
        self.draw()

    def draw(self):
        self.delete("all")
        
        # Draw 3 status bars
        metrics = [
            ("Stealth", self.metrics_data.get("stealth", 0.95), SUCCESS),
            ("Kernel", self.metrics_data.get("kernel", 0.85), ACCENT),
            ("Storage", self.metrics_data.get("storage", 0.70), WARNING)
        ]
        
        for i, (name, val, color) in enumerate(metrics):
            y = 20 + (i * 28)
            # Label
            self.create_text(10, y, text=name, fill=TEXT_SECONDARY, font=("Inter", 8, "bold"), anchor="w")
            # Track
            self.create_rectangle(75, y-5, 240, y+5, fill="#1e293b", outline="")
            # Progress
            self.create_rectangle(75, y-5, 75 + (165 * val), y+5, fill=color, outline="")
            # Text %
            self.create_text(250, y, text=f"{int(val*100)}%", fill=TEXT_PRIMARY, font=("Inter", 8, "bold"), anchor="w")

class ProFeaturesFrame(ctk.CTkFrame):
    """Premium features dashboard for Pro users."""
    def __init__(self, master, engine):
        super().__init__(master, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=ACCENT)
        self.engine = engine
        self.build()
        self.refresh_metrics()

    def refresh_metrics(self):
        metrics = self.engine.get_pro_metrics()
        self.graphics.update(metrics)
        # Refresh every 10 seconds for real-time feel
        self.after(10000, self.refresh_metrics)

    def build(self):
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(title_frame, text="PRO DASHBOARD", 
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=ACCENT_GLOW).pack(side="left")
        
        ctk.CTkLabel(title_frame, text="UNLOCKED", 
                     font=ctk.CTkFont(size=9, weight="bold"),
                     fg_color=ACCENT, text_color="white", corner_radius=4).pack(side="right", padx=5)

        # Dashboard Graphics
        self.graphics = DashboardGraphics(self, width=280, height=100)
        self.graphics.pack(fill="x", padx=15, pady=5)

        # Process Shield (Ghost Mode)
        self.shield_var = ctk.BooleanVar(value=False)
        shield_frame = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=10)
        shield_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(shield_frame, text="PROCESS SHIELD (GHOST MODE)", font=("Inter", 11, "bold"), text_color=TEXT_PRIMARY).pack(side="left", padx=15, pady=10)
        self.shield_switch = ctk.CTkSwitch(shield_frame, text="", 
                                           variable=self.shield_var,
                                           command=self.toggle_shield,
                                           progress_color=SUCCESS)
        self.shield_switch.pack(side="right", padx=15)

        # Kernel Layer Manager
        kernel_frame = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=10)
        kernel_frame.pack(fill="x", padx=15, pady=5)
        
        k_info = ctk.CTkFrame(kernel_frame, fg_color="transparent")
        k_info.pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(k_info, text="KERNEL LAYER MANAGER", font=("Inter", 11, "bold"), text_color=TEXT_PRIMARY, anchor="w").pack(anchor="w")
        ctk.CTkLabel(k_info, text="Low-level HWID driver control", font=("Inter", 9), text_color=TEXT_DIM, anchor="w").pack(anchor="w")
        
        self.kernel_btn = ctk.CTkButton(kernel_frame, text="LOAD DRIVER", width=100, height=32, corner_radius=6,
                                        fg_color=BG_DARK, border_width=1, border_color=ACCENT,
                                        font=("Inter", 10, "bold"),
                                        command=self.load_kernel)
        self.kernel_btn.pack(side="right", padx=15)

        # Self-Destruct (Stealth)
        ctk.CTkButton(self, text="SYSTEM STEALTH (SELF-DESTRUCT)", 
                      fg_color="transparent", border_width=1, border_color="#ef4444",
                      text_color="#ef4444", hover_color="#450a0a",
                      command=self.engine.system_stealth).pack(fill="x", padx=15, pady=(10, 15))

    def toggle_shield(self):
        enabled = self.shield_var.get()
        root = self.winfo_toplevel()
        self.engine.toggle_ghost_mode(enabled, root)

    def load_kernel(self):
        self.kernel_btn.configure(state="disabled", text="LOADING...")
        success = self.engine.load_kernel_driver()
        if success:
            self.kernel_btn.configure(text="KERNEL ACTIVE", fg_color=SUCCESS, border_color=SUCCESS)
        else:
            self.kernel_btn.configure(text="FAILED: NO .SYS", fg_color="#450a0a", state="normal")
            self.kernel_btn.configure(text="LOAD DRIVER", fg_color=BG_DARK)



class TraceAnalysisWindow(ctk.CTkToplevel):
    def __init__(self, master, engine):
        super().__init__(master)
        self.title(master.get_text("trace_title"))
        self.geometry("500x550")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)
        self.engine = engine
        self.analyzer = TraceAnalyzer(engine)
        self.found_traces = []
        self.build()
        self.attributes("-topmost", True)
        self._center()

    def _center(self):
        self.update_idletasks()
        w, h = 500, 550
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def build(self):
        # Header
        ctk.CTkLabel(self, text="🔍", font=ctk.CTkFont(size=40)).pack(pady=(20, 10))
        ctk.CTkLabel(self, text=self.master.get_text("trace_title"), 
                     font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_PRIMARY).pack()
        
        self.status_lbl = ctk.CTkLabel(self, text=self.master.get_text("trace_scan") + "...", 
                                        font=ctk.CTkFont(size=12), text_color=TEXT_SECONDARY)
        self.status_lbl.pack(pady=5)

        # Traces List
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=BG_CARD, corner_radius=12, 
                                                   border_width=1, border_color=BORDER, height=280)
        self.scroll_frame.pack(padx=30, pady=20, fill="both", expand=True)

        # Action Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=30, pady=(0, 25))

        self.clean_btn = ctk.CTkButton(self.btn_frame, text=self.master.get_text("trace_clean"), 
                                        height=45, corner_radius=10, fg_color=ACCENT, 
                                        hover_color=ACCENT_HOVER, state="disabled",
                                        command=self.start_cleaning)
        self.clean_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.rescan_btn = ctk.CTkButton(self.btn_frame, text="RE-SCAN", 
                                        height=45, corner_radius=10, fg_color=BG_CARD, 
                                        hover_color=BG_CARD_HOVER, border_width=1, border_color=BORDER_LIGHT,
                                        command=self.start_scan)
        self.rescan_btn.pack(side="right", expand=True, fill="x", padx=(5, 0))

        self.after(500, self.start_scan)

    def start_scan(self):
        self.status_lbl.configure(text=self.master.get_text("trace_scan") + "...", text_color=TEXT_SECONDARY)
        for w in self.scroll_frame.winfo_children(): w.destroy()
        self.found_traces = self.analyzer.scan()
        self.display_results()

    def display_results(self):
        if not self.found_traces:
            ctk.CTkLabel(self.scroll_frame, text="✅ " + self.master.get_text("trace_none"), 
                         font=ctk.CTkFont(size=13), text_color=SUCCESS).pack(pady=100)
            self.status_lbl.configure(text=self.master.get_text("trace_none"), text_color=SUCCESS)
            self.clean_btn.configure(state="disabled")
        else:
            self.status_lbl.configure(text=f"{len(self.found_traces)} " + self.master.get_text("trace_found"), text_color=WARNING)
            for t in self.found_traces:
                f = ctk.CTkFrame(self.scroll_frame, fg_color="#0f172a", corner_radius=8)
                f.pack(fill="x", pady=4, padx=5)
                ctk.CTkLabel(f, text="⚠️", width=30).pack(side="left", padx=5)
                info = ctk.CTkFrame(f, fg_color="transparent")
                info.pack(side="left", fill="both", expand=True, pady=8)
                ctk.CTkLabel(info, text=t["name"], font=ctk.CTkFont(size=12, weight="bold"), 
                             text_color=TEXT_PRIMARY, anchor="w").pack(fill="x")
                ctk.CTkLabel(info, text=t["path"], font=ctk.CTkFont(size=9), 
                             text_color=TEXT_DIM, anchor="w").pack(fill="x")
            self.clean_btn.configure(state="normal")

    def start_cleaning(self):
        self.clean_btn.configure(state="disabled", text=self.master.get_text("trace_cleaning"))
        self.status_lbl.configure(text=self.master.get_text("trace_cleaning"), text_color=ACCENT_GLOW)
        self.after(1000, self._do_clean)

    def _do_clean(self):
        self.analyzer.clean(self.found_traces)
        self.scroll_frame.destroy()
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=BG_CARD, corner_radius=12, 
                                                   border_width=1, border_color=BORDER, height=280)
        self.scroll_frame.pack(padx=30, pady=20, fill="both", expand=True)
        ctk.CTkLabel(self.scroll_frame, text="✨ " + self.master.get_text("trace_done"), 
                     font=ctk.CTkFont(size=14, weight="bold"), text_color=SUCCESS).pack(pady=100)
        self.status_lbl.configure(text=self.master.get_text("trace_done"), text_color=SUCCESS)
        self.clean_btn.configure(text=self.master.get_text("trace_clean"))
        self.found_traces = []


# ============================================================
#                    MAIN APP
# ============================================================

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.lang = self._load_lang()

        # Auto-elevate to admin with absolute path
        if not self._is_admin():
            script_path = os.path.abspath(sys.argv[0])
            params = f'"{script_path}" ' + " ".join(f'"{a}"' for a in sys.argv[1:])
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, params, None, 1
            )
            sys.exit(0)

        self.engine = SpoofEngine()

        self.title("Solutions HWID Spoofer")
        self.geometry("900x650")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)
        ctk.set_appearance_mode("dark")

        # Determine base path
        if getattr(sys, 'frozen', False):
            bp = os.path.dirname(sys.executable)
        else:
            bp = os.path.dirname(os.path.abspath(__file__))

        self.license_manager = LicenseManager(bp)
        
        # Load Branding
        logo_path = os.path.join(bp, "assets", "icon.png")
        if os.path.exists(logo_path):
            self.logo = ctk.CTkImage(light_image=Image.open(logo_path),
                                     dark_image=Image.open(logo_path),
                                     size=(120, 120))
            # Set window icon (after a short delay to ensure window is created)
            self.after(250, lambda: self._set_icon(logo_path))
        else:
            self.logo = None

        self.current_screen = None
        self.current_key = None
        self.show_login()
        self._center()

    def _set_icon(self, path):
        try:
            # Load image and convert to PhotoImage for window icon
            img = Image.open(path)
            # Use iconphoto for universal support of PNG/other formats as window/taskbar icon
            photo = ImageTk.PhotoImage(img)
            self.wm_iconphoto(True, photo)
            # Try iconbitmap for titlebar as well (some systems prefer it)
            # but usually wm_iconphoto is enough for PNG with true.
        except Exception as e:
            print(f"[SPOOFER ERROR] Icon set failed: {e}")

    def _load_lang(self):
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    return json.load(f).get("lang", "tr")
        except:
            pass
        return "tr"

    def _save_lang(self, lang):
        try:
            config = {}
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
            config["lang"] = lang
            with open("config.json", "w") as f:
                json.dump(config, f)
        except:
            pass

    def get_text(self, key):
        return TRANSLATIONS.get(self.lang, TRANSLATIONS["tr"]).get(key, key)

    def switch_lang(self, lang):
        self.lang = lang
        self._save_lang(lang)
        # Refresh current screen
        if isinstance(self.current_screen, LoginScreen):
            self.show_login()
        elif isinstance(self.current_screen, SpooferScreen):
            self.show_spoofer(self.current_key)
        elif isinstance(self.current_screen, AdminPanel):
            self.show_admin_panel()
        else:
            self.show_login()
        self._center()

    def _is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _switch(self, screen_cls, *args):
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = screen_cls(self, *args)
        self.current_screen.pack(fill="both", expand=True)

    def show_login(self):
        self._switch(LoginScreen, self.show_spoofer, self.show_admin)

    def show_spoofer(self, key):
        self.current_key = key
        self._switch(SpooferScreen, self.show_login, key)

    def show_admin(self):
        self._switch(AdminLoginScreen, self.show_admin_panel, self.show_login)

    def show_admin_panel(self):
        self._switch(AdminPanel, self.show_login)


if __name__ == "__main__":
    print("[SPOOFER STARTUP] Main starting...")
    app = App()
    app.mainloop()
