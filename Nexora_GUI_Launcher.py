#!/usr/bin/env python3
"""
Nexora Enterprise Knowledge Agent - 1-Click Graphical Control Panel
A modern desktop GUI launcher built with Tkinter for managing all project services.
"""

import os
import sys
import socket
import subprocess
import webbrowser
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

# Project paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_SERVICE_DIR = os.path.join(ROOT_DIR, "ai-service")
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

# Colors (Modern Dark Theme)
BG_COLOR = "#1e1e2e"
PANEL_COLOR = "#181825"
CARD_COLOR = "#313244"
TEXT_COLOR = "#cdd6f4"
MUTED_TEXT = "#a6adc8"
ACCENT_BLUE = "#89b4fa"
ACCENT_GREEN = "#a6e3a1"
ACCENT_RED = "#f38ba8"
ACCENT_YELLOW = "#f9e2af"
BUTTON_HOVER = "#45475a"

class NexoraLauncherGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nexora Systems - Enterprise RAG Control Panel")
        self.geometry("780x620")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        # Ensure window icon or clean style
        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        self._create_header()
        self._create_status_panel()
        self._create_controls_panel()
        self._create_credentials_card()
        self._create_footer()

        # Start port monitor thread
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_services_loop, daemon=True)
        self.monitor_thread.start()

    def _create_header(self):
        header_frame = tk.Frame(self, bg=PANEL_COLOR, height=75)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="⚡ NEXORA SYSTEMS — ENTERPRISE KNOWLEDGE AGENT",
            font=("Segoe UI", 15, "bold"),
            bg=PANEL_COLOR,
            fg=ACCENT_BLUE
        )
        title_label.pack(pady=(12, 2))

        sub_label = tk.Label(
            header_frame,
            text="3-Tier RAG Architecture • Role-Based Access Control (RBAC) • Full-Stack Control Panel",
            font=("Segoe UI", 9),
            bg=PANEL_COLOR,
            fg=MUTED_TEXT
        )
        sub_label.pack()

    def _create_status_panel(self):
        panel = tk.LabelFrame(
            self,
            text="  Live Service Status  ",
            font=("Segoe UI", 10, "bold"),
            bg=BG_COLOR,
            fg=ACCENT_BLUE,
            bd=1,
            relief=tk.GROOVE,
            padx=15,
            pady=10
        )
        panel.pack(fill=tk.X, padx=20, pady=15)

        self.status_indicators = {}
        services = [
            ("MySQL Database", 3306, "Database storage for users & RBAC"),
            ("AI Knowledge Service", 8000, "Python FastAPI + LangChain + ChromaDB"),
            ("Backend API Gateway", 5000, "Node.js Express + Auth Middleware"),
            ("React Frontend UI", 5173, "Vite Responsive Web Dashboard")
        ]

        for idx, (name, port, desc) in enumerate(services):
            row_frame = tk.Frame(panel, bg=BG_COLOR)
            row_frame.pack(fill=tk.X, pady=4)

            name_lbl = tk.Label(
                row_frame,
                text=f"{name} (Port {port})",
                font=("Segoe UI", 10, "bold"),
                bg=BG_COLOR,
                fg=TEXT_COLOR,
                width=28,
                anchor="w"
            )
            name_lbl.pack(side=tk.LEFT)

            desc_lbl = tk.Label(
                row_frame,
                text=desc,
                font=("Segoe UI", 9),
                bg=BG_COLOR,
                fg=MUTED_TEXT,
                width=35,
                anchor="w"
            )
            desc_lbl.pack(side=tk.LEFT)

            status_lbl = tk.Label(
                row_frame,
                text="● CHECKING...",
                font=("Segoe UI", 9, "bold"),
                bg=BG_COLOR,
                fg=ACCENT_YELLOW,
                width=15,
                anchor="e"
            )
            status_lbl.pack(side=tk.RIGHT)
            self.status_indicators[port] = status_lbl

    def _create_controls_panel(self):
        panel = tk.Frame(self, bg=BG_COLOR)
        panel.pack(fill=tk.X, padx=20, pady=5)

        # Button row 1: Main actions
        btn_frame1 = tk.Frame(panel, bg=BG_COLOR)
        btn_frame1.pack(fill=tk.X, pady=5)

        start_btn = tk.Button(
            btn_frame1,
            text="▶  START ALL SERVICES (1-CLICK)",
            font=("Segoe UI", 10, "bold"),
            bg="#2e4c2b",
            fg="#ffffff",
            activebackground=ACCENT_GREEN,
            activeforeground="#000000",
            relief=tk.FLAT,
            cursor="hand2",
            height=2,
            command=self.start_all_services
        )
        start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        stop_btn = tk.Button(
            btn_frame1,
            text="■  STOP ALL SERVICES",
            font=("Segoe UI", 10, "bold"),
            bg="#5e2735",
            fg="#ffffff",
            activebackground=ACCENT_RED,
            activeforeground="#000000",
            relief=tk.FLAT,
            cursor="hand2",
            height=2,
            command=self.stop_all_services
        )
        stop_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(8, 0))

        # Button row 2: Quick Links
        btn_frame2 = tk.Frame(panel, bg=BG_COLOR)
        btn_frame2.pack(fill=tk.X, pady=10)

        web_btn = tk.Button(
            btn_frame2,
            text="🌐 Open Frontend App",
            font=("Segoe UI", 9, "bold"),
            bg=CARD_COLOR,
            fg=ACCENT_BLUE,
            relief=tk.FLAT,
            cursor="hand2",
            pady=5,
            command=lambda: webbrowser.open("http://localhost:5173")
        )
        web_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        swagger_btn = tk.Button(
            btn_frame2,
            text="📜 Backend Swagger UI",
            font=("Segoe UI", 9, "bold"),
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            relief=tk.FLAT,
            cursor="hand2",
            pady=5,
            command=lambda: webbrowser.open("http://localhost:5000/api-docs")
        )
        swagger_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ai_docs_btn = tk.Button(
            btn_frame2,
            text="🤖 AI Service API Docs",
            font=("Segoe UI", 9, "bold"),
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            relief=tk.FLAT,
            cursor="hand2",
            pady=5,
            command=lambda: webbrowser.open("http://localhost:8000/docs")
        )
        ai_docs_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

    def _create_credentials_card(self):
        card = tk.LabelFrame(
            self,
            text="  Demo User Accounts (Role-Based Access)  ",
            font=("Segoe UI", 10, "bold"),
            bg=CARD_COLOR,
            fg=ACCENT_BLUE,
            bd=1,
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        card.pack(fill=tk.X, padx=20, pady=10)

        columns = ("Role", "Email", "Password", "Access Level")
        tree = ttk.Treeview(card, columns=columns, show="headings", height=4)
        
        # Style treeview
        self.style.configure("Treeview", background=CARD_COLOR, foreground=TEXT_COLOR, fieldbackground=CARD_COLOR, font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading", background=PANEL_COLOR, foreground=ACCENT_BLUE, font=("Segoe UI", 9, "bold"))
        self.style.map("Treeview", background=[('selected', ACCENT_BLUE)])

        tree.heading("Role", text="Role")
        tree.heading("Email", text="Email")
        tree.heading("Password", text="Password")
        tree.heading("Access Level", text="Access Privileges")

        tree.column("Role", width=90, anchor="center")
        tree.column("Email", width=220, anchor="w")
        tree.column("Password", width=90, anchor="center")
        tree.column("Access Level", width=290, anchor="w")

        users = [
            ("CEO", "arvind.rajan@nexorasystems.com", "password", "Unrestricted access to all data, financials & salaries"),
            ("HR", "divya.iyer@nexorasystems.com", "password", "Employee records, HR policies, compensation bands"),
            ("Employee", "anjali.ramesh@nexorasystems.com", "password", "Standard company policies, leave handbook, current projects"),
            ("Intern", "deepa.narayan@nexorasystems.com", "password", "Public company profile, general handbook only")
        ]

        for user in users:
            tree.insert("", tk.END, values=user)

        tree.pack(fill=tk.X)

    def _create_footer(self):
        footer_frame = tk.Frame(self, bg=PANEL_COLOR, height=35)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        footer_frame.pack_propagate(False)

        footer_label = tk.Label(
            footer_frame,
            text="Tip: Double-click START_PROJECT.bat in Windows for an instant Command Prompt 1-Click launcher.",
            font=("Segoe UI", 8),
            bg=PANEL_COLOR,
            fg=MUTED_TEXT
        )
        footer_label.pack(pady=8)

    def _check_port(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(('127.0.0.1', port)) == 0

    def _monitor_services_loop(self):
        while self.running:
            for port, label in self.status_indicators.items():
                is_active = self._check_port(port)
                if is_active:
                    label.config(text="● ONLINE", fg=ACCENT_GREEN)
                else:
                    label.config(text="● OFFLINE", fg=ACCENT_RED)
            time.sleep(2)

    def start_all_services(self):
        try:
            # 1. Start AI service
            if not self._check_port(8000):
                cmd_ai = f'start "Nexora AI Service" /D "{AI_SERVICE_DIR}" cmd /k ".\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"'
                subprocess.Popen(cmd_ai, shell=True)
            
            # 2. Start Backend
            if not self._check_port(5000):
                cmd_backend = f'start "Nexora Backend API" /D "{BACKEND_DIR}" cmd /k "npm start"'
                subprocess.Popen(cmd_backend, shell=True)
            
            # 3. Start Frontend
            if not self._check_port(5173):
                cmd_frontend = f'start "Nexora React Frontend" /D "{FRONTEND_DIR}" cmd /k "npm run dev -- --open"'
                subprocess.Popen(cmd_frontend, shell=True)

            messagebox.showinfo(
                "Services Launched",
                "All 3 services (AI Service, Backend API, Frontend Dashboard) have been launched in dedicated terminal windows!\n\n"
                "The dashboard will open automatically at http://localhost:5173 once Vite starts."
            )
        except Exception as e:
            messagebox.showerror("Error Launching Services", f"An error occurred: {str(e)}")

    def stop_all_services(self):
        try:
            subprocess.Popen('taskkill /F /IM node.exe /T 2>nul', shell=True)
            subprocess.Popen('for /f "tokens=5" %a in (\'netstat -aon ^| findstr :8000 ^| findstr LISTENING\') do taskkill /f /pid %a 2>nul', shell=True)
            subprocess.Popen('for /f "tokens=5" %a in (\'netstat -aon ^| findstr :5000 ^| findstr LISTENING\') do taskkill /f /pid %a 2>nul', shell=True)
            subprocess.Popen('for /f "tokens=5" %a in (\'netstat -aon ^| findstr :5173 ^| findstr LISTENING\') do taskkill /f /pid %a 2>nul', shell=True)
            messagebox.showinfo("Services Stopped", "Shutdown commands executed. All running services on ports 8000, 5000, and 5173 have been terminated.")
        except Exception as e:
            messagebox.showerror("Error Stopping Services", f"An error occurred: {str(e)}")

    def on_closing(self):
        self.running = False
        self.destroy()

if __name__ == "__main__":
    app = NexoraLauncherGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
