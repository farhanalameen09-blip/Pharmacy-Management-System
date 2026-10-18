import customtkinter as ctk # type: ignore
import os
import subprocess

from tkinter import messagebox
from datetime import datetime

from database import create_tables, create_default_admin, get_connection
from config import Colors, Shape, window_title, center_window
from ui_kit import apply_theme, StatCard

from login.login import LoginFrame
from medicines.medicines import MedicinePage
from inventory.inventory import InventoryPage
from billing.sales_billing import BillingPage
from customers.customers import CustomerPage
from suppliers.suppliers import SupplierPage
from reports.reports import ReportsPage
from notifications.notifications import NotificationsPage
from settings.settings import SettingsPage


# ============================================================
# APPLICATION SETTINGS
# ============================================================

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")
apply_theme()


class PharmacyApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title(window_title())
        center_window(self, 1400, 850)
        self.configure(fg_color=Colors.BACKGROUND)
        self.minsize(1100, 700)

        # User information
        self.current_user = None
        self.current_user_id = None
        self.current_role = None
        self.touch_mode = False
        self._touch_original_sizes = {}

        # Initialize database
        try:
            create_tables()
            create_default_admin()
        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Unable to initialize database.\n\n{error}"
            )

        self.show_login()

        # Keyboard shortcuts
        self.setup_shortcuts()

    # ========================================================
    # CLEAR WINDOW
    # ========================================================

    def clear_window(self):

        for widget in self.winfo_children():
            widget.destroy()

    # ========================================================
    # LOGIN
    # ========================================================

    def show_login(self):

        self.clear_window()

        self.login_frame = LoginFrame(
            self,
            self.login_success
        )

        self.login_frame.pack(
            fill="both",
            expand=True
        )

    # ========================================================
    # LOGIN SUCCESS
    # ========================================================

    def login_success(self, user_data, role=None):

        try:

            if isinstance(user_data, dict):

                self.current_user_id = user_data.get("user_id")
                self.current_user = user_data.get("username")
                self.current_role = (
                    user_data.get("role")
                    or "Admin"
                )

            else:

                self.current_user = user_data
                self.current_user_id = None
                self.current_role = role or "Admin"

            print(
                f"Login successful: "
                f"{self.current_user} | "
                f"{self.current_role}"
            )

            self.apply_saved_theme()

            self.show_dashboard()

        except Exception as error:

            print(
                "Login success error:",
                error
            )

            messagebox.showerror(
                "Login Error",
                f"Unable to open dashboard.\n\n{error}"
            )

    # ========================================================
    # APPLY SAVED THEME
    # ========================================================

    def apply_saved_theme(self):

        if not self.current_user_id:
            return

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT theme
                FROM user_settings
                WHERE user_id = ?
                """,
                (self.current_user_id,)
            )

            result = cursor.fetchone()

            conn.close()

            if result and result[0]:

                theme = result[0].lower()

                if theme == "dark":
                    ctk.set_appearance_mode("dark")

                elif theme == "system":
                    ctk.set_appearance_mode("system")

                else:
                    ctk.set_appearance_mode("light")

        except Exception as error:

            print(
                "Theme loading error:",
                error
            )

    # ========================================================
    # MAIN APPLICATION LAYOUT
    # ========================================================

    def show_dashboard(self):
        self.clear_window()

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # Narrow left strip: logo at top and logout at bottom.
        self.create_sidebar()

        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(side="left", fill="both", expand=True)

        # Top header remains visible on every module page.
        self.create_top_header()
        self.page_host = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.page_host.pack(fill="both", expand=True)

        # Existing navigation methods use content_frame, so point it to the page host.
        self.content_frame = self.page_host
        self.show_dashboard_page()

    def create_top_header(self):
        header = ctk.CTkFrame(
            self.content_frame,
            height=76,
            corner_radius=0,
            fg_color=("white", "#17263B"),
            border_width=1,
            border_color=("gray85", "#263A55")
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Pharmacy Management System",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#173B63", "#F2F7FF")
        ).pack(side="left", padx=26)

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right", padx=20)

        # Theme control stays in the top header on every module page.
        self.theme_button = ctk.CTkButton(
            actions,
            text=self.get_theme_button_text(),
            width=105,
            height=40,
            corner_radius=12,
            fg_color=("#E7F0FA", "#2B405C"),
            text_color=("#173B63", "#FFFFFF"),
            hover_color=("#D5E5F6", "#385574"),
            command=self.toggle_theme
        )
        self.theme_button.pack(side="left", padx=6)

        ctk.CTkButton(
            actions, text="🔔  Notifications", width=145, height=40,
            corner_radius=12, command=self.show_notifications
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            actions, text="👤  Profile  ▾", width=125, height=40,
            corner_radius=12, fg_color=("gray88", "#2B405C"),
            text_color=("#173B63", "#FFFFFF"),
            hover_color=("gray80", "#385574"),
            command=self.show_profile
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            actions, text="⚙  Settings", width=120, height=40,
            corner_radius=12, fg_color=("gray88", "#2B405C"),
            text_color=("#173B63", "#FFFFFF"),
            hover_color=("gray80", "#385574"),
            command=self.show_settings
        ).pack(side="left", padx=6)

        self.touch_mode_button = ctk.CTkButton(
            actions,
            text="👆 Touch Mode: Off",
            width=150,
            height=40,
            corner_radius=12,
            command=self.toggle_touch_mode
        )
        self.touch_mode_button.pack(side="left", padx=6)

        ctk.CTkButton(
            actions,
            text="⌨ Keyboard",
            width=115,
            height=40,
            corner_radius=12,
            command=self.open_on_screen_keyboard
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            actions,
            text="🖱 Touchpad Help",
            width=145,
            height=40,
            corner_radius=12,
            command=self.show_touchpad_help
        ).pack(side="left", padx=6)

    def toggle_touch_mode(self):
        """Toggle larger, easier-to-tap controls throughout the current page."""
        self.touch_mode = not self.touch_mode
        self.apply_touch_mode_to_widgets(self)

        if hasattr(self, "touch_mode_button") and self.touch_mode_button.winfo_exists():
            self.touch_mode_button.configure(
                text="👆 Touch Mode: On" if self.touch_mode else "👆 Touch Mode: Off"
            )

    def apply_touch_mode_to_widgets(self, parent):
        """Apply touch-friendly sizing safely to supported CustomTkinter widgets."""
        for widget in parent.winfo_children():
            try:
                widget_class = widget.__class__.__name__

                if widget_class in {
                    "CTkButton", "CTkEntry", "CTkComboBox", "CTkOptionMenu",
                    "CTkCheckBox", "CTkSwitch", "CTkRadioButton"
                }:
                    if widget not in self._touch_original_sizes:
                        self._touch_original_sizes[widget] = {
                            "height": widget.cget("height") if "height" in widget.keys() else None,
                            "font": widget.cget("font") if "font" in widget.keys() else None,
                        }

                    original = self._touch_original_sizes[widget]
                    if self.touch_mode:
                        changes = {}
                        if "height" in widget.keys():
                            changes["height"] = max(46, int(original["height"] or 0))
                        if "font" in widget.keys() and original["font"] is not None:
                            try:
                                font = original["font"]
                                size = font.cget("size") if hasattr(font, "cget") else 12
                                family = font.cget("family") if hasattr(font, "cget") else "Arial"
                                weight = font.cget("weight") if hasattr(font, "cget") else "normal"
                                changes["font"] = ctk.CTkFont(
                                    family=family, size=max(14, abs(int(size))), weight=weight
                                )
                            except Exception:
                                pass
                        if changes:
                            widget.configure(**changes)
                    else:
                        changes = {}
                        if original["height"] is not None:
                            changes["height"] = original["height"]
                        if original["font"] is not None:
                            changes["font"] = original["font"]
                        if changes:
                            widget.configure(**changes)
            except Exception:
                # Some third-party or custom widgets don't support these options.
                pass

            try:
                self.apply_touch_mode_to_widgets(widget)
            except Exception:
                pass

    def open_on_screen_keyboard(self):
        """Open Windows' built-in on-screen keyboard."""
        try:
            subprocess.Popen(["osk.exe"], shell=False)
        except Exception:
            try:
                os.startfile(os.path.join(os.environ.get("WINDIR", r"C:\\Windows"), "System32", "osk.exe"))
            except Exception as error:
                messagebox.showerror(
                    "On-Screen Keyboard",
                    "Windows could not open the on-screen keyboard. "
                    "You can open it manually from Windows Settings > Accessibility > Keyboard.\\n\\n"
                    f"Details: {error}",
                    parent=self
                )

    def show_touchpad_help(self):
        """Explain common touchpad actions; actual gestures are handled by Windows."""
        popup = ctk.CTkToplevel(self)
        popup.title("Touchpad & Touchscreen Help")
        popup.geometry("500x430")
        popup.minsize(440, 380)
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(
            popup,
            text="Touchpad & Touchscreen Help",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=22, pady=(22, 12))

        tips = (
            "• Single tap or click: select a button or field\\n\\n"
            "• Two-finger swipe: scroll lists and pages (if enabled in Windows)\\n\\n"
            "• Pinch to zoom: supported only where Windows and the device/app allow it\\n\\n"
            "• Touch Mode: makes supported controls larger and easier to tap\\n\\n"
            "• Keyboard: opens the Windows on-screen keyboard\\n\\n"
            "Note: touchpad gestures are controlled by Windows and your device driver."
        )
        ctk.CTkLabel(
            popup,
            text=tips,
            justify="left",
            anchor="w",
            wraplength=445,
            font=ctk.CTkFont(size=14)
        ).pack(fill="both", expand=True, padx=22, pady=8)

        ctk.CTkButton(
            popup, text="Close", height=44, command=popup.destroy
        ).pack(pady=(8, 20))

    def get_theme_button_text(self):
        """Return a label describing the theme that can be switched to."""
        current_mode = ctk.get_appearance_mode().lower()
        return "☀ Light Mode" if current_mode == "dark" else "🌙 Dark Mode"

    def toggle_theme(self):
        """Switch between light and dark appearance from the top header."""
        current_mode = ctk.get_appearance_mode().lower()
        new_mode = "light" if current_mode == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)

        if hasattr(self, "theme_button") and self.theme_button.winfo_exists():
            self.theme_button.configure(text=self.get_theme_button_text())

    def show_profile(self):
        popup = ctk.CTkToplevel(self)
        popup.title("My Profile")
        popup.geometry("360x260")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(
            popup, text="👤  My Profile",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(22, 18))

        profile_box = ctk.CTkFrame(popup, corner_radius=14)
        profile_box.pack(fill="x", padx=22, pady=5)

        ctk.CTkLabel(
            profile_box, text=f"Username: {self.current_user or 'User'}",
            font=ctk.CTkFont(size=15)
        ).pack(anchor="w", padx=18, pady=(15, 5))

        ctk.CTkLabel(
            profile_box, text=f"Role: {self.current_role or 'User'}",
            font=ctk.CTkFont(size=15)
        ).pack(anchor="w", padx=18, pady=(5, 15))

        ctk.CTkButton(
            popup, text="Close", width=110, command=popup.destroy
        ).pack(pady=15)


        # ========================================================
        # SIDEBAR
        # ========================================================

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self.main_container,
            width=82,
            corner_radius=0,
            fg_color=("#173B63", "#10243B")
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar, text="💊",
            font=ctk.CTkFont(size=35)
        ).pack(pady=(24, 12))

        ctk.CTkFrame(
            self.sidebar, height=2,
            fg_color=("#4B82B8", "#2B4B6C")
        ).pack(fill="x", padx=15, pady=(0, 10))

        # Flexible empty area pushes Logout into the bottom-left corner.
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)

        ctk.CTkButton(
            self.sidebar,
            text="↪\nLogout",
            width=66,
            height=58,
            corner_radius=12,
            fg_color=("#E83F5B", "#D93652"),
            hover_color=("#C92E49", "#B8243D"),
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.logout
        ).pack(side="bottom", padx=8, pady=18)

        # Card buttons, rather than sidebar menu items, are the main navigation.
        self.menu_buttons = {}


        # ========================================================
        # ACTIVE MENU
        # ========================================================


    def set_active_menu(self, menu_name):
        # Navigation is now handled by dashboard feature cards and the top header.
        # Keep this method for compatibility with the existing module methods.
        return

    # ========================================================
    # CLEAR CONTENT
    # ========================================================

    def clear_content(self):

        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # ========================================================
    # DASHBOARD
    # ========================================================

    def show_dashboard_page(self):
        self.clear_content()

        dashboard = ctk.CTkScrollableFrame(
            self.content_frame, fg_color="transparent"
        )
        dashboard.pack(fill="both", expand=True)

        # Welcome banner
        welcome = ctk.CTkFrame(
            dashboard,
            corner_radius=22,
            fg_color=("#EAF4FF", "#1C3550"),
            border_width=1,
            border_color=("#D4E8FF", "#294968")
        )
        welcome.pack(fill="x", padx=28, pady=(24, 22))

        welcome_left = ctk.CTkFrame(welcome, fg_color="transparent")
        welcome_left.pack(side="left", fill="both", expand=True, padx=26, pady=24)

        ctk.CTkLabel(
            welcome_left,
            text=f"Welcome back, {self.current_user or 'User'}! 👋",
            font=ctk.CTkFont(size=27, weight="bold"),
            text_color=("#173B63", "#F2F7FF")
        ).pack(anchor="w")

        ctk.CTkLabel(
            welcome_left,
            text="Manage your pharmacy with ease and efficiency.",
            font=ctk.CTkFont(size=15),
            text_color=("#426487", "#C4D6EA")
        ).pack(anchor="w", pady=(8, 0))

        ctk.CTkLabel(
            welcome,
            text="🏥\n💊",
            font=ctk.CTkFont(size=43),
            width=145
        ).pack(side="right", padx=25, pady=12)

        ctk.CTkLabel(
            dashboard,
            text="Pharmacy Features",
            font=ctk.CTkFont(size=23, weight="bold"),
            text_color=("#173B63", "#F2F7FF")
        ).pack(anchor="w", padx=30, pady=(0, 4))

        ctk.CTkLabel(
            dashboard,
            text="Choose a section to get started",
            font=ctk.CTkFont(size=13),
            text_color=("gray45", "gray70")
        ).pack(anchor="w", padx=30, pady=(0, 16))

        features = [
            ("💊", "Medicines", "Manage medicines and product details", self.show_medicines, "#3478F6"),
            ("📦", "Inventory", "Track stock and update quantities", self.show_inventory, "#2EAD65"),
            ("🧾", "Sales / Billing", "Create bills and manage sales", self.show_sales, "#F39A28"),
            ("👥", "Customers", "Manage customer details and history", self.show_customers, "#8754E8"),
            ("🚚", "Suppliers", "Manage supplier information and orders", self.show_suppliers, "#1CA6B7"),
            ("📊", "Reports", "View reports and sales analytics", self.show_reports, "#E84D55"),
        ]

        cards_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
        cards_frame.pack(fill="both", expand=True, padx=22, pady=(0, 28))

        for col in range(3):
            cards_frame.grid_columnconfigure(col, weight=1, uniform="feature")
        for row in range(2):
            cards_frame.grid_rowconfigure(row, weight=1, uniform="feature")

        self.menu_buttons = {}
        for index, (icon, title, description, command, accent) in enumerate(features):
            row, col = divmod(index, 3)
            card = ctk.CTkFrame(
                cards_frame,
                corner_radius=18,
                fg_color=("white", "#1B2D44"),
                border_width=1,
                border_color=(accent, "#334B68")
            )
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)

            icon_badge = ctk.CTkFrame(
                card, width=72, height=72, corner_radius=36,
                fg_color=accent
            )
            icon_badge.pack(side="left", padx=(18, 14), pady=20)
            icon_badge.pack_propagate(False)

            ctk.CTkLabel(
                icon_badge, text=icon,
                font=ctk.CTkFont(size=31),
                text_color="#FFFFFF"
            ).pack(expand=True)

            text_area = ctk.CTkFrame(card, fg_color="transparent")
            text_area.pack(side="left", fill="both", expand=True, pady=20, padx=(0, 8))

            ctk.CTkLabel(
                text_area, text=title,
                font=ctk.CTkFont(size=17, weight="bold"),
                anchor="w",
                text_color=("#173B63", "#F2F7FF")
            ).pack(anchor="w", pady=(4, 5))

            ctk.CTkLabel(
                text_area, text=description,
                font=ctk.CTkFont(size=12),
                wraplength=175,
                justify="left",
                anchor="w",
                text_color=("gray40", "gray75")
            ).pack(anchor="w", pady=(0, 9))

            ctk.CTkButton(
                text_area,
                text="Open section  →",
                height=32,
                width=130,
                corner_radius=10,
                fg_color=accent,
                hover_color=accent,
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=12, weight="bold"),
                command=command
            ).pack(anchor="w")

            self.menu_buttons[title] = card

        footer = ctk.CTkLabel(
            dashboard,
            text=f"Signed in as {self.current_user or 'User'}  •  {self.current_role or 'User'}",
            font=ctk.CTkFont(size=12),
            text_color=("gray45", "gray70")
        )
        footer.pack(anchor="e", padx=32, pady=(0, 16))


        # ========================================================
        # DATABASE STATISTICS
        # ========================================================

    def get_total_medicines(self):

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) FROM medicines"
            )

            result = cursor.fetchone()[0]

            conn.close()

            return result

        except Exception:
            return 0

    # --------------------------------------------------------

    def get_total_customers(self):

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) FROM customers"
            )

            result = cursor.fetchone()[0]

            conn.close()

            return result

        except Exception:
            return 0

    # --------------------------------------------------------

    def get_total_suppliers(self):

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) FROM suppliers"
            )

            result = cursor.fetchone()[0]

            conn.close()

            return result

        except Exception:
            return 0

    # --------------------------------------------------------

    def get_low_stock_count(self):

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM medicines
                WHERE quantity <= min_stock
                AND quantity > 0
                """
            )

            result = cursor.fetchone()[0]

            conn.close()

            return result

        except Exception:
            return 0

    # --------------------------------------------------------

    def get_expired_count(self):

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM medicines
                WHERE expiry_date IS NOT NULL
                AND expiry_date != ''
                AND date(expiry_date) < date('now')
                """
            )

            result = cursor.fetchone()[0]

            conn.close()

            return result

        except Exception:
            return 0

    # --------------------------------------------------------

    def get_expiring_soon_count(self):

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM medicines
                WHERE expiry_date IS NOT NULL
                AND expiry_date != ''
                AND date(expiry_date)
                    BETWEEN date('now')
                    AND date('now', '+30 days')
                """
            )

            result = cursor.fetchone()[0]

            conn.close()

            return result

        except Exception:
            return 0

    # --------------------------------------------------------

    def get_today_revenue(self):

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT COALESCE(SUM(total), 0)
                FROM sales
                WHERE date(sale_date) = date('now')
                """
            )

            result = cursor.fetchone()[0] or 0

            conn.close()

            return float(result)

        except Exception:
            return 0.0

    # --------------------------------------------------------

    def get_total_revenue(self):

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT COALESCE(SUM(total), 0)
                FROM sales
                """
            )

            result = cursor.fetchone()[0] or 0

            conn.close()

            return float(result)

        except Exception:
            return 0.0

    # --------------------------------------------------------

    def get_total_bills(self):

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) FROM sales"
            )

            result = cursor.fetchone()[0]

            conn.close()

            return result

        except Exception:
            return 0

    # --------------------------------------------------------

    def get_recent_sales(self):

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    s.invoice_no,
                    COALESCE(c.name, 'Walk-in Customer'),
                    s.sale_date,
                    s.total
                FROM sales s
                LEFT JOIN customers c
                    ON s.customer_id = c.customer_id
                ORDER BY s.sale_id DESC
                LIMIT 5
                """
            )

            result = cursor.fetchall()

            conn.close()

            return result

        except Exception as error:

            print(
                "Recent sales error:",
                error
            )

            return []

    # ========================================================
    # MODULE NAVIGATION
    # ========================================================

    def show_medicines(self):

        self.clear_content()

        self.set_active_menu("Medicines")

        page = MedicinePage(
            self.content_frame,
            self.show_dashboard_page
        )

        page.pack(
            fill="both",
            expand=True
        )

    # --------------------------------------------------------

    def show_inventory(self):

        self.clear_content()

        self.set_active_menu("Inventory")

        page = InventoryPage(
            self.content_frame,
            self.show_dashboard_page
        )

        page.pack(
            fill="both",
            expand=True
        )

    # --------------------------------------------------------

    def show_sales(self):

        self.clear_content()

        self.set_active_menu("Sales / Billing")

        page = BillingPage(
            self.content_frame,
            self.show_dashboard_page,
            self.current_user_id
        )

        page.pack(
            fill="both",
            expand=True
        )

    # --------------------------------------------------------

    def show_customers(self):

        self.clear_content()

        self.set_active_menu("Customers")

        page = CustomerPage(
            self.content_frame,
            self.show_dashboard_page
        )

        page.pack(
            fill="both",
            expand=True
        )

    # --------------------------------------------------------

    def show_suppliers(self):

        self.clear_content()

        self.set_active_menu("Suppliers")

        page = SupplierPage(
            self.content_frame,
            self.show_dashboard_page
        )

        page.pack(
            fill="both",
            expand=True
        )

    # --------------------------------------------------------

    def show_reports(self):

        self.clear_content()

        self.set_active_menu("Reports")

        page = ReportsPage(
            self.content_frame,
            self.show_dashboard_page
        )

        page.pack(
            fill="both",
            expand=True
        )

    # --------------------------------------------------------

    def show_notifications(self):

        self.clear_content()

        self.set_active_menu("Notifications")

        page = NotificationsPage(
            self.content_frame,
            self.show_dashboard_page
        )

        page.pack(
            fill="both",
            expand=True
        )

    # --------------------------------------------------------

    def show_settings(self):

        self.clear_content()

        self.set_active_menu("Settings")

        page = SettingsPage(
            self.content_frame,
            self.show_dashboard_page,
            self.current_user_id,
            self.current_user or "",
            self.current_role or "User",
            self.logout
        )

        page.pack(
            fill="both",
            expand=True
        )

    # ========================================================
    # LOGOUT
    # ========================================================

    def logout(self):

        confirm = messagebox.askyesno(
            "Logout",
            "Are you sure you want to logout?"
        )

        if not confirm:
            return

        self.current_user = None
        self.current_user_id = None
        self.current_role = None

        self.show_login()

    # ========================================================
    # KEYBOARD SHORTCUTS
    # ========================================================

    def setup_shortcuts(self):

        self.bind_all(
            "<Control-h>",
            lambda event: self.shortcut_dashboard()
        )

        self.bind_all(
            "<Control-m>",
            lambda event: self.shortcut_medicines()
        )

        self.bind_all(
            "<Control-i>",
            lambda event: self.shortcut_inventory()
        )

        self.bind_all(
            "<Control-s>",
            lambda event: self.shortcut_sales()
        )

        self.bind_all(
            "<Control-r>",
            lambda event: self.shortcut_reports()
        )

        self.bind_all(
            "<Control-n>",
            lambda event: self.shortcut_notifications()
        )

        self.bind_all(
            "<Control-comma>",
            lambda event: self.shortcut_settings()
        )

        self.bind_all(
            "<Control-l>",
            lambda event: self.shortcut_logout()
        )

    # ========================================================
    # SHORTCUT FUNCTIONS
    # ========================================================

    def shortcut_dashboard(self):

        if self.current_user:
            self.show_dashboard_page()

    # --------------------------------------------------------

    def shortcut_medicines(self):

        if self.current_user:
            self.show_medicines()

    # --------------------------------------------------------

    def shortcut_inventory(self):

        if self.current_user:
            self.show_inventory()

    # --------------------------------------------------------

    def shortcut_sales(self):

        if self.current_user:
            self.show_sales()

    # --------------------------------------------------------

    def shortcut_reports(self):

        if self.current_user:
            self.show_reports()

    # --------------------------------------------------------

    def shortcut_notifications(self):

        if self.current_user:
            self.show_notifications()

    # --------------------------------------------------------

    def shortcut_settings(self):

        if self.current_user:
            self.show_settings()

    # --------------------------------------------------------

    def shortcut_logout(self):

        if self.current_user:
            self.logout()


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    app = PharmacyApp()

    app.mainloop()