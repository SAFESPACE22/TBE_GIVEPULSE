import customtkinter as ctk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv, set_key
import threading
import time
import os

# ── Color Palette ──────────────────────────────────────────────
CRIMSON      = "#841617"
CRIMSON_DARK = "#6B1213"
CREAM        = "#FDF5E6"
BG_DARK      = "#1a1a2e"
BG_CARD      = "#16213e"
BG_INPUT     = "#0f3460"
ACCENT_BLUE  = "#2196F3"
SUCCESS      = "#4CAF50"
ERROR        = "#F44336"
WARNING      = "#FFC107"
TEXT_PRIMARY  = "#e8e8e8"
TEXT_DIM      = "#8899aa"

# ── App Setup ──────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class GivePulseApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GivePulse Export Tool")
        self.geometry("520x760")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)

        self.driver = None
        self.running = False

        self._build_ui()
        self._load_saved_credentials()

    # ── UI Construction ────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=CRIMSON, corner_radius=0, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header, text="⚡ GivePulse Export Tool",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=CREAM
        )
        title_label.pack(pady=22)

        # Main content card
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=16)
        card.pack(fill="both", expand=True, padx=20, pady=(20, 20))

        # ── Credentials Section ────────────────────────────────
        cred_label = ctk.CTkLabel(
            card, text="OU Credentials",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        cred_label.pack(anchor="w", padx=24, pady=(20, 8))

        separator = ctk.CTkFrame(card, fg_color=CRIMSON, height=2, corner_radius=1)
        separator.pack(fill="x", padx=24, pady=(0, 16))

        # Email input
        email_frame = ctk.CTkFrame(card, fg_color="transparent")
        email_frame.pack(fill="x", padx=24, pady=(0, 4))

        ctk.CTkLabel(
            email_frame, text="OU Email or OUNetID",
            font=ctk.CTkFont(size=12), text_color=TEXT_DIM
        ).pack(anchor="w")

        self.email_entry = ctk.CTkEntry(
            email_frame, height=42,
            font=ctk.CTkFont(size=14),
            fg_color=BG_INPUT, border_color=CRIMSON_DARK,
            placeholder_text="youremail@ou.edu",
            corner_radius=10
        )
        self.email_entry.pack(fill="x", pady=(4, 0))

        # Password input
        pw_frame = ctk.CTkFrame(card, fg_color="transparent")
        pw_frame.pack(fill="x", padx=24, pady=(12, 4))

        ctk.CTkLabel(
            pw_frame, text="Password",
            font=ctk.CTkFont(size=12), text_color=TEXT_DIM
        ).pack(anchor="w")

        self.password_entry = ctk.CTkEntry(
            pw_frame, height=42, show="●",
            font=ctk.CTkFont(size=14),
            fg_color=BG_INPUT, border_color=CRIMSON_DARK,
            placeholder_text="••••••••",
            corner_radius=10
        )
        self.password_entry.pack(fill="x", pady=(4, 0))

        # Event URL input
        url_frame = ctk.CTkFrame(card, fg_color="transparent")
        url_frame.pack(fill="x", padx=24, pady=(12, 4))

        ctk.CTkLabel(
            url_frame, text="Event Management URL",
            font=ctk.CTkFont(size=12), text_color=TEXT_DIM
        ).pack(anchor="w")

        self.url_entry = ctk.CTkEntry(
            url_frame, height=42,
            font=ctk.CTkFont(size=14),
            fg_color=BG_INPUT, border_color=CRIMSON_DARK,
            placeholder_text="https://www.givepulse.com/event/manage/.../registrations",
            corner_radius=10
        )
        self.url_entry.pack(fill="x", pady=(4, 0))

        # Save credentials checkbox
        self.save_creds_var = ctk.BooleanVar(value=False)
        self.save_checkbox = ctk.CTkCheckBox(
            card, text="Save inputs for next time",
            variable=self.save_creds_var,
            font=ctk.CTkFont(size=13),
            text_color=TEXT_DIM,
            fg_color=CRIMSON, hover_color=CRIMSON_DARK,
            corner_radius=4
        )
        self.save_checkbox.pack(anchor="w", padx=24, pady=(12, 0))

        # ── Run Button ─────────────────────────────────────────
        self.run_button = ctk.CTkButton(
            card, text="▶  Run Export", height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=CRIMSON, hover_color=CRIMSON_DARK,
            corner_radius=12,
            command=self._on_run_clicked
        )
        self.run_button.pack(fill="x", padx=24, pady=(24, 16))

        # ── Status Log ─────────────────────────────────────────
        log_label = ctk.CTkLabel(
            card, text="Status",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        log_label.pack(anchor="w", padx=24, pady=(4, 4))

        self.status_log = ctk.CTkTextbox(
            card, height=180,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=BG_DARK, corner_radius=10,
            text_color=TEXT_DIM,
            state="disabled"
        )
        self.status_log.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    # ── Credential Persistence ─────────────────────────────────
    def _load_saved_credentials(self):
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
            email = os.getenv("OU_EMAIL", "")
            password = os.getenv("OU_PASSWORD", "")
            event_url = os.getenv("EVENT_URL", "")
            
            if email and email != "your_email@ou.edu":
                self.email_entry.insert(0, email)
                self.password_entry.insert(0, password)
                if event_url:
                    self.url_entry.insert(0, event_url)
                self.save_creds_var.set(True)

    def _save_credentials(self, email, password, event_url):
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        # Create or update .env
        if not os.path.exists(env_path):
            with open(env_path, "w") as f:
                f.write("")
        set_key(env_path, "OU_EMAIL", email)
        set_key(env_path, "OU_PASSWORD", password)
        set_key(env_path, "EVENT_URL", event_url)

    # ── Status Log Helpers ─────────────────────────────────────
    def _log(self, message, level="info"):
        prefix = {"info": "⋯", "success": "✓", "error": "✗", "warn": "⚠"}
        icon = prefix.get(level, "•")
        self.status_log.configure(state="normal")
        self.status_log.insert("end", f"  {icon}  {message}\n")
        self.status_log.see("end")
        self.status_log.configure(state="disabled")

    def _clear_log(self):
        self.status_log.configure(state="normal")
        self.status_log.delete("1.0", "end")
        self.status_log.configure(state="disabled")

    # ── Button Handler ─────────────────────────────────────────
    def _on_run_clicked(self):
        if self.running:
            return

        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        event_url = self.url_entry.get().strip()

        if not email or not password:
            self._log("Please enter both email and password.", "error")
            return
            
        if not event_url or not event_url.startswith("http"):
            self._log("Please enter a valid GivePulse event URL.", "error")
            return

        if self.save_creds_var.get():
            self._save_credentials(email, password, event_url)

        self.running = True
        self.run_button.configure(text="⏳  Running...", state="disabled", fg_color=TEXT_DIM)
        self._clear_log()
        self._log("Starting GivePulse export automation...", "info")

        thread = threading.Thread(
            target=self._run_automation, args=(email, password, event_url), daemon=True
        )
        thread.start()

    # ── Selenium Automation (runs in background thread) ────────
    def _run_automation(self, email, password, event_url):
        try:
            # Launch browser
            self._log("Launching Chrome browser...", "info")
            self.driver = webdriver.Chrome()
            self.driver.get("https://www.givepulse.com/login")
            time.sleep(3)

            # Dismiss cookie popup
            self._log("Dismissing cookie popup...", "info")
            try:
                accept_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.t-acceptAllButton"))
                )
                self.driver.execute_script("arguments[0].click();", accept_btn)
                time.sleep(1)
                self._log("Cookie popup dismissed", "success")
            except:
                self._log("No cookie popup found, continuing", "info")

            # Click SSO button
            self._log("Clicking SSO button...", "info")
            sso_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "showSSO-login"))
            )
            self.driver.execute_script("arguments[0].click();", sso_button)
            time.sleep(2)
            self._log("SSO panel opened", "success")

            # Type login provider
            self._log("Selecting The University of Oklahoma...", "info")
            provider_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search_sso_groups_id_login"))
            )
            provider_input.clear()
            provider_input.send_keys("The University of Oklahoma")
            time.sleep(2)

            # Click typeahead suggestion
            suggestion = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//div[contains(@class, 'tt-suggestion')]//p[contains(text(), 'The University of Oklahoma')]"
                ))
            )
            suggestion.click()
            time.sleep(1)
            self._log("University of Oklahoma selected", "success")

            # Click Login button
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "btn-login-sso-login"))
            )
            self.driver.execute_script("arguments[0].click();", login_button)
            self._log("Redirecting to OU SSO...", "info")

            # Fill OU credentials
            time.sleep(3)
            email_input = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "ou-email"))
            )
            email_input.clear()
            email_input.send_keys(email)

            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ou-password"))
            )
            password_input.clear()
            password_input.send_keys(password)

            sign_in_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input.button--blue"))
            )
            sign_in_button.click()
            self._log("OU credentials submitted", "success")

            # Wait for SSO redirect back to GivePulse
            self._log("Waiting for SSO to complete (2FA if needed)...", "info")
            WebDriverWait(self.driver, 300).until(
                lambda d: "givepulse.com" in d.current_url
            )
            self._log("SSO login complete!", "success")
            time.sleep(2)

            # Navigate to registrations
            self._log("Navigating to event registrations page...", "info")
            self.driver.get(event_url)
            time.sleep(3)
            self._log("Registrations page loaded", "success")

            # Click Actions
            self._log("Clicking Actions dropdown...", "info")
            actions_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Actions')]"))
            )
            actions_button.click()
            time.sleep(1)

            # Click Export
            self._log("Selecting Export...", "info")
            export_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Export"))
            )
            export_option.click()
            time.sleep(2)

            # Select All Data
            self._log("Selecting All Data...", "info")
            all_data = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "(//input[@type='radio'])[1]"))
            )
            all_data.click()
            time.sleep(1)

            # Click Export button in dialog
            self._log("Exporting data...", "info")
            time.sleep(1)
            self.driver.execute_script("""
                var btns = document.querySelectorAll('button.btn-primary');
                for (var btn of btns) {
                    if (btn.offsetParent !== null) {
                        btn.click();
                        break;
                    }
                }
            """)

            self._log("Export complete! ✨", "success")

        except Exception as e:
            self._log(f"Error: {str(e)}", "error")
        finally:
            self.running = False
            self.after(0, lambda: self.run_button.configure(
                text="▶  Run Export", state="normal", fg_color=CRIMSON
            ))

    def on_closing(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self.destroy()


if __name__ == "__main__":
    app = GivePulseApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
