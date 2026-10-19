import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from datetime import date, datetime, timedelta

import customtkinter as ctk

from database import (
    create_tables,
    create_default_admin,
    get_connection,
)

from config import (
    Colors,
    Shape,
    window_title,
    center_window,
)

from ui_kit import apply_theme

from login.login import LoginFrame
from medicines.medicines import MedicinePage
from inventory.inventory import InventoryPage
from billing.sales_billing import BillingPage
from customers.customers import CustomerPage
from suppliers.suppliers import SupplierPage
from reports.reports import ReportsPage
from notifications.notifications import NotificationsPage
from settings.settings import SettingsPage


class PharmacyApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # --------------------------------------------------
        # APPLICATION CONFIGURATION
        # --------------------------------------------------
        self.title("Pharmacy Management System")
        self.geometry("1400x850")
        self.minsize(1100, 700)

        try:
            center_window(self, 1400, 850)
        except Exception:
            pass

        try:
            ctk.set_appearance_mode("light")
            ctk.set_default_color_theme("blue")
        except Exception:
            pass

        self.current_user = None
        self.current_user_id = None
        self.current_role = None

        self.current_page = None
        self.content_frame = None
        self.sidebar_frame = None
        self.header_frame = None

        self.touch_mode = False
        self._original_widget_settings = {}

        self.theme_mode = "light"

        # --------------------------------------------------
        # DATABASE INITIALIZATION
        # --------------------------------------------------
        try:
            create_tables()
            create_default_admin()
        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not initialize the database.\n\n{error}",
                parent=self,
            )
            self.destroy()
            return

        # --------------------------------------------------
        # WINDOW EVENTS AND KEYBOARD SHORTCUTS
        # --------------------------------------------------
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.bind_all(
            "<Control-h>",
            lambda event: self.run_shortcut(self.show_dashboard_page),
        )
        self.bind_all(
            "<Control-m>",
            lambda event: self.run_shortcut(self.show_medicines),
        )
        self.bind_all(
            "<Control-i>",
            lambda event: self.run_shortcut(self.show_inventory),
        )
        self.bind_all(
            "<Control-b>",
            lambda event: self.run_shortcut(self.show_billing),
        )
        self.bind_all(
            "<Control-c>",
            lambda event: self.run_shortcut(self.show_customers),
        )
        self.bind_all(
            "<Control-s>",
            lambda event: self.run_shortcut(self.show_suppliers),
        )
        self.bind_all(
            "<Control-r>",
            lambda event: self.run_shortcut(self.show_reports),
        )
        self.bind_all(
            "<Control-n>",
            lambda event: self.run_shortcut(self.show_notifications),
        )
        self.bind_all(
            "<Control-comma>",
            lambda event: self.run_shortcut(self.show_settings),
        )
        self.bind_all(
            "<Control-l>",
            lambda event: self.run_shortcut(self.logout),
        )

        # Start at the login screen.
        self.show_login()

    # ======================================================
    # DATABASE HELPERS
    # ======================================================

    def fetch_one(self, query, parameters=()):
        """Execute a SELECT query and return one row."""
        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(query, parameters)
                return cursor.fetchone()
        except Exception as error:
            print(f"Database query error: {error}")
            return None

    def fetch_all(self, query, parameters=()):
        """Execute a SELECT query and return all rows."""
        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(query, parameters)
                return cursor.fetchall()
        except Exception as error:
            print(f"Database query error: {error}")
            return []

    # ======================================================
    # LOGIN
    # ======================================================

    def show_login(self):
        self.clear_window()

        self.current_user = None
        self.current_user_id = None
        self.current_role = None

        self.login_frame = LoginFrame(
            self,
            self.login_success,
        )

        self.login_frame.pack(
            fill="both",
            expand=True,
        )

    def login_success(self, user_data, role=None):
        """
        Receive the logged-in user's information.

        Supports either a dictionary or a username plus role,
        depending on the login module's callback format.
        """

        if isinstance(user_data, dict):
            self.current_user_id = (
                user_data.get("user_id")
                or user_data.get("id")
            )

            self.current_user = (
                user_data.get("username")
                or user_data.get("name")
                or ""
            )

            self.current_role = (
                user_data.get("role")
                or role
                or "User"
            )

        else:
            self.current_user = str(user_data or "")
            self.current_role = role or "User"

            # Try to resolve the user ID from the username.
            row = self.fetch_one(
                """
                SELECT user_id
                FROM users
                WHERE username = ?
                """,
                (self.current_user,),
            )

            if row:
                self.current_user_id = row[0]

        self.apply_saved_theme()
        self.show_dashboard_page()

    # ======================================================
    # THEME MANAGEMENT
    # ======================================================

    def apply_saved_theme(self):
        """Load the logged-in user's saved appearance setting."""

        if self.current_user_id is None:
            self.theme_mode = "light"
            return

        row = self.fetch_one(
            """
            SELECT theme
            FROM user_settings
            WHERE user_id = ?
            """,
            (self.current_user_id,),
        )

        if row and row[0] in ("light", "dark"):
            self.theme_mode = row[0]
        else:
            self.theme_mode = "light"

        self.apply_current_theme()

    def apply_current_theme(self):
        """Apply the selected appearance mode."""

        try:
            ctk.set_appearance_mode(self.theme_mode)

            try:
                apply_theme(self.theme_mode)
            except TypeError:
                # Some UI kits accept no theme argument.
                pass
            except Exception:
                pass

        except Exception as error:
            print(f"Theme error: {error}")

    def toggle_theme(self):
        """Switch between light and dark appearance."""

        self.theme_mode = (
            "dark"
            if self.theme_mode == "light"
            else "light"
        )

        self.apply_current_theme()
        self.save_theme_preference()

        # Rebuild the current page to refresh its appearance.
        self.show_dashboard_page()

    def save_theme_preference(self):
        """Save the theme for the current user."""

        if self.current_user_id is None:
            return

        try:
            with get_connection() as connection:
                cursor = connection.cursor()

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_settings (
                        user_id INTEGER PRIMARY KEY,
                        theme TEXT DEFAULT 'light'
                    )
                    """
                )

                cursor.execute(
                    """
                    INSERT INTO user_settings (user_id, theme)
                    VALUES (?, ?)
                    ON CONFLICT(user_id)
                    DO UPDATE SET theme = excluded.theme
                    """,
                    (
                        self.current_user_id,
                        self.theme_mode,
                    ),
                )

        except Exception as error:
            print(f"Could not save theme preference: {error}")

    # ======================================================
    # GENERAL WINDOW HELPERS
    # ======================================================

    def clear_window(self):
        """Remove all widgets currently attached to the window."""

        for widget in self.winfo_children():
            try:
                widget.destroy()
            except Exception:
                pass

        self.content_frame = None
        self.sidebar_frame = None
        self.header_frame = None
        self.current_page = None

    def clear_content(self):
        """Remove the current page from the content area."""

        if self.content_frame is None:
            return

        for widget in self.content_frame.winfo_children():
            try:
                widget.destroy()
            except Exception:
                pass

        self.current_page = None

    def run_shortcut(self, callback):
        """Prevent application shortcuts from running on the login screen."""

        if not self.current_user:
            return "break"

        try:
            callback()
        except Exception as error:
            print(f"Shortcut error: {error}")

        return "break"

    # ======================================================
    # DASHBOARD LAYOUT
    # ======================================================

    def show_dashboard_page(self):
        """Display the main dashboard."""

        if not self.current_user:
            self.show_login()
            return

        self.clear_window()

        self.main_container = ctk.CTkFrame(
            self,
            corner_radius=0,
        )
        self.main_container.pack(
            fill="both",
            expand=True,
        )

        self.main_container.grid_rowconfigure(
            0,
            weight=1,
        )
        self.main_container.grid_columnconfigure(
            1,
            weight=1,
        )

        # Sidebar
        self.build_sidebar()

        # Right side
        self.right_container = ctk.CTkFrame(
            self.main_container,
            corner_radius=0,
        )
        self.right_container.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        self.right_container.grid_rowconfigure(
            1,
            weight=1,
        )
        self.right_container.grid_columnconfigure(
            0,
            weight=1,
        )

        self.build_header()

        self.content_frame = ctk.CTkFrame(
            self.right_container,
            corner_radius=0,
        )
        self.content_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=15,
            pady=(0, 15),
        )

        self.show_dashboard_home()

        if self.touch_mode:
            self.apply_touch_mode()

    # ======================================================
    # SIDEBAR
    # ======================================================

    def build_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(
            self.main_container,
            width=230,
            corner_radius=0,
        )
        self.sidebar_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        self.sidebar_frame.grid_propagate(False)

        self.sidebar_frame.grid_rowconfigure(
            20,
            weight=1,
        )

        title = ctk.CTkLabel(
            self.sidebar_frame,
            text="💊 Pharmacy\nManagement",
            font=("Arial", 21, "bold"),
            justify="left",
        )
        title.pack(
            padx=18,
            pady=(25, 30),
            anchor="w",
        )

        navigation = [
            ("🏠  Dashboard", self.show_dashboard_page),
            ("💊  Medicines", self.show_medicines),
            ("📦  Inventory", self.show_inventory),
            ("🧾  Billing", self.show_billing),
            ("👥  Customers", self.show_customers),
            ("🏭  Suppliers", self.show_suppliers),
            ("📊  Reports", self.show_reports),
            ("🔔  Notifications", self.show_notifications),
            ("⚙️  Settings", self.show_settings),
        ]

        for label, callback in navigation:
            button = ctk.CTkButton(
                self.sidebar_frame,
                text=label,
                anchor="w",
                height=42,
                corner_radius=8,
                command=callback,
            )
            button.pack(
                fill="x",
                padx=12,
                pady=4,
            )

        self.sidebar_user_label = ctk.CTkLabel(
            self.sidebar_frame,
            text=(
                f"Logged in as:\n"
                f"{self.current_user}\n"
                f"Role: {self.current_role}"
            ),
            justify="left",
            wraplength=190,
        )
        self.sidebar_user_label.pack(
            side="bottom",
            padx=15,
            pady=(10, 5),
            anchor="w",
        )

        logout_button = ctk.CTkButton(
            self.sidebar_frame,
            text="🚪  Logout",
            height=42,
            fg_color="#B42318",
            hover_color="#8E1B13",
            command=self.logout,
        )
        logout_button.pack(
            side="bottom",
            fill="x",
            padx=12,
            pady=(5, 18),
        )

    # ======================================================
    # HEADER
    # ======================================================

    def build_header(self):
        self.header_frame = ctk.CTkFrame(
            self.right_container,
            height=75,
            corner_radius=0,
        )
        self.header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=15,
            pady=(15, 12),
        )
        self.header_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        heading = ctk.CTkLabel(
            self.header_frame,
            text="Pharmacy Management System",
            font=("Arial", 23, "bold"),
        )
        heading.grid(
            row=0,
            column=0,
            padx=15,
            pady=15,
            sticky="w",
        )

        button_frame = ctk.CTkFrame(
            self.header_frame,
            fg_color="transparent",
        )
        button_frame.grid(
            row=0,
            column=1,
            padx=10,
            pady=10,
            sticky="e",
        )

        ctk.CTkButton(
            button_frame,
            text="🌙 / ☀️",
            width=75,
            command=self.toggle_theme,
        ).pack(
            side="left",
            padx=3,
        )

        ctk.CTkButton(
            button_frame,
            text="🔔",
            width=45,
            command=self.show_notifications,
        ).pack(
            side="left",
            padx=3,
        )

        ctk.CTkButton(
            button_frame,
            text="👤 Profile",
            width=85,
            command=self.show_profile,
        ).pack(
            side="left",
            padx=3,
        )

        ctk.CTkButton(
            button_frame,
            text="⚙ Settings",
            width=90,
            command=self.show_settings,
        ).pack(
            side="left",
            padx=3,
        )

        ctk.CTkButton(
            button_frame,
            text="Touch",
            width=65,
            command=self.toggle_touch_mode,
        ).pack(
            side="left",
            padx=3,
        )

        ctk.CTkButton(
            button_frame,
            text="Keyboard",
            width=85,
            command=self.open_on_screen_keyboard,
        ).pack(
            side="left",
            padx=3,
        )

    # ======================================================
    # DASHBOARD HOME
    # ======================================================

    def show_dashboard_home(self):
        if self.content_frame is None:
            return

        self.clear_content()

        page = ctk.CTkScrollableFrame(
            self.content_frame,
            corner_radius=0,
        )
        page.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        title = ctk.CTkLabel(
            page,
            text="Dashboard Overview",
            font=("Arial", 25, "bold"),
        )
        title.pack(
            anchor="w",
            padx=10,
            pady=(10, 5),
        )

        welcome = ctk.CTkLabel(
            page,
            text=(
                f"Welcome, {self.current_user}! "
                f"Here is your pharmacy overview."
            ),
            font=("Arial", 14),
        )
        welcome.pack(
            anchor="w",
            padx=10,
            pady=(0, 20),
        )

        # Statistics
        stats_frame = ctk.CTkFrame(
            page,
            fg_color="transparent",
        )
        stats_frame.pack(
            fill="x",
            padx=5,
            pady=5,
        )

        statistics = [
            (
                "Total Medicines",
                self.get_total_medicines(),
                "#2563EB",
            ),
            (
                "Customers",
                self.get_total_customers(),
                "#0F766E",
            ),
            (
                "Suppliers",
                self.get_total_suppliers(),
                "#7C3AED",
            ),
            (
                "Low Stock",
                self.get_low_stock_count(),
                "#D97706",
            ),
            (
                "Expired",
                self.get_expired_count(),
                "#B42318",
            ),
            (
                "Today's Revenue",
                f"₹{self.get_today_revenue():,.2f}",
                "#15803D",
            ),
        ]

        for index, (label, value, color) in enumerate(statistics):
            stats_frame.grid_columnconfigure(
                index % 3,
                weight=1,
            )

            card = ctk.CTkFrame(
                stats_frame,
                border_width=1,
                border_color=color,
                corner_radius=12,
            )

            card.grid(
                row=index // 3,
                column=index % 3,
                sticky="nsew",
                padx=7,
                pady=7,
            )

            ctk.CTkLabel(
                card,
                text=label,
                font=("Arial", 13),
                text_color=color,
            ).pack(
                anchor="w",
                padx=15,
                pady=(15, 5),
            )

            ctk.CTkLabel(
                card,
                text=str(value),
                font=("Arial", 23, "bold"),
            ).pack(
                anchor="w",
                padx=15,
                pady=(0, 15),
            )

        # Quick actions
        quick_title = ctk.CTkLabel(
            page,
            text="Quick Actions",
            font=("Arial", 21, "bold"),
        )
        quick_title.pack(
            anchor="w",
            padx=10,
            pady=(25, 10),
        )

        quick_frame = ctk.CTkFrame(
            page,
            fg_color="transparent",
        )
        quick_frame.pack(
            fill="x",
            padx=5,
            pady=5,
        )

        quick_actions = [
            ("💊 Medicines", self.show_medicines),
            ("📦 Inventory", self.show_inventory),
            ("🧾 New Billing", self.show_billing),
            ("👥 Customers", self.show_customers),
            ("🏭 Suppliers", self.show_suppliers),
            ("📊 Reports", self.show_reports),
        ]

        for index, (label, callback) in enumerate(quick_actions):
            quick_frame.grid_columnconfigure(
                index % 3,
                weight=1,
            )

            ctk.CTkButton(
                quick_frame,
                text=label,
                height=65,
                corner_radius=10,
                command=callback,
            ).grid(
                row=index // 3,
                column=index % 3,
                sticky="ew",
                padx=7,
                pady=7,
            )

        # Recent sales
        recent_title = ctk.CTkLabel(
            page,
            text="Recent Sales",
            font=("Arial", 21, "bold"),
        )
        recent_title.pack(
            anchor="w",
            padx=10,
            pady=(25, 10),
        )

        recent_sales = self.get_recent_sales()

        if not recent_sales:
            ctk.CTkLabel(
                page,
                text="No sales records available yet.",
                font=("Arial", 13),
            ).pack(
                anchor="w",
                padx=12,
                pady=10,
            )
        else:
            for sale in recent_sales:
                invoice_no = sale[0] or "N/A"
                customer_name = sale[1] or "Walk-in Customer"
                total = sale[2] or 0

                sale_card = ctk.CTkFrame(
                    page,
                    corner_radius=8,
                )
                sale_card.pack(
                    fill="x",
                    padx=10,
                    pady=4,
                )

                ctk.CTkLabel(
                    sale_card,
                    text=(
                        f"Invoice: {invoice_no}   |   "
                        f"Customer: {customer_name}   |   "
                        f"Total: ₹{float(total):,.2f}"
                    ),
                    anchor="w",
                ).pack(
                    fill="x",
                    padx=12,
                    pady=12,
                )

        self.current_page = page

    # ======================================================
    # DASHBOARD STATISTICS
    # ======================================================

    def get_total_medicines(self):
        row = self.fetch_one(
            "SELECT COUNT(*) FROM medicines"
        )
        return row[0] if row else 0

    def get_total_customers(self):
        row = self.fetch_one(
            "SELECT COUNT(*) FROM customers"
        )
        return row[0] if row else 0

    def get_total_suppliers(self):
        row = self.fetch_one(
            "SELECT COUNT(*) FROM suppliers"
        )
        return row[0] if row else 0

    def get_low_stock_count(self):
        row = self.fetch_one(
            """
            SELECT COUNT(*)
            FROM medicines
            WHERE COALESCE(quantity, 0)
                  <= COALESCE(min_stock, 0)
            """
        )
        return row[0] if row else 0

    def get_expired_count(self):
        today = date.today().isoformat()

        row = self.fetch_one(
            """
            SELECT COUNT(*)
            FROM medicines
            WHERE expiry_date IS NOT NULL
              AND TRIM(expiry_date) != ''
              AND date(expiry_date) < date(?)
            """,
            (today,),
        )

        return row[0] if row else 0

    def get_expiring_soon_count(self):
        today = date.today()
        end_date = today + timedelta(days=30)

        row = self.fetch_one(
            """
            SELECT COUNT(*)
            FROM medicines
            WHERE expiry_date IS NOT NULL
              AND TRIM(expiry_date) != ''
              AND date(expiry_date) >= date(?)
              AND date(expiry_date) <= date(?)
            """,
            (
                today.isoformat(),
                end_date.isoformat(),
            ),
        )

        return row[0] if row else 0

    def get_today_revenue(self):
        today = date.today().isoformat()

        row = self.fetch_one(
            """
            SELECT COALESCE(SUM(total), 0)
            FROM sales
            WHERE date(sale_date) = date(?)
            """,
            (today,),
        )

        return float(row[0] or 0) if row else 0.0

    def get_total_revenue(self):
        row = self.fetch_one(
            """
            SELECT COALESCE(SUM(total), 0)
            FROM sales
            """
        )

        return float(row[0] or 0) if row else 0.0

    def get_total_bills(self):
        row = self.fetch_one(
            "SELECT COUNT(*) FROM sales"
        )
        return row[0] if row else 0

    def get_recent_sales(self):
        return self.fetch_all(
            """
            SELECT
                s.invoice_no,
                COALESCE(c.name, 'Walk-in Customer'),
                s.total
            FROM sales AS s
            LEFT JOIN customers AS c
                ON s.customer_id = c.customer_id
            ORDER BY s.sale_id DESC
            LIMIT 5
            """
        )

    # ======================================================
    # PAGE NAVIGATION
    # ======================================================

    def prepare_page(self):
        """Clear the previous page before opening another module."""

        if self.content_frame is None:
            return None

        self.clear_content()
        return self.content_frame

    def show_medicines(self):
        parent = self.prepare_page()

        if parent is None:
            return

        try:
            self.current_page = MedicinePage(
                parent,
                self.show_dashboard_page,
            )
            self.current_page.pack(
                fill="both",
                expand=True,
            )
        except Exception as error:
            messagebox.showerror(
                "Medicines Error",
                f"Could not open Medicines.\n\n{error}",
                parent=self,
            )

    def show_inventory(self):
        parent = self.prepare_page()

        if parent is None:
            return

        try:
            self.current_page = InventoryPage(
                parent,
                self.show_medicines,
            )
            self.current_page.pack(
                fill="both",
                expand=True,
            )
        except Exception as error:
            messagebox.showerror(
                "Inventory Error",
                f"Could not open Inventory.\n\n{error}",
                parent=self,
            )

    def show_billing(self):
        parent = self.prepare_page()

        if parent is None:
            return

        try:
            self.current_page = BillingPage(
                parent,
                self.show_dashboard_page,
                self.current_user_id,
            )
            self.current_page.pack(
                fill="both",
                expand=True,
            )
        except Exception as error:
            messagebox.showerror(
                "Billing Error",
                f"Could not open Billing.\n\n{error}",
                parent=self,
            )

    def show_customers(self):
        parent = self.prepare_page()

        if parent is None:
            return

        try:
            self.current_page = CustomerPage(
                parent,
                self.show_dashboard_page,
            )
            self.current_page.pack(
                fill="both",
                expand=True,
            )
        except Exception as error:
            messagebox.showerror(
                "Customers Error",
                f"Could not open Customers.\n\n{error}",
                parent=self,
            )

    def show_suppliers(self):
        parent = self.prepare_page()

        if parent is None:
            return

        try:
            self.current_page = SupplierPage(
                parent,
                self.show_dashboard_page,
            )
            self.current_page.pack(
                fill="both",
                expand=True,
            )
        except Exception as error:
            messagebox.showerror(
                "Suppliers Error",
                f"Could not open Suppliers.\n\n{error}",
                parent=self,
            )

    def show_reports(self):
        parent = self.prepare_page()

        if parent is None:
            return

        try:
            self.current_page = ReportsPage(
                parent,
                self.show_dashboard_page,
            )
            self.current_page.pack(
                fill="both",
                expand=True,
            )
        except Exception as error:
            messagebox.showerror(
                "Reports Error",
                f"Could not open Reports.\n\n{error}",
                parent=self,
            )

    def show_notifications(self):
        parent = self.prepare_page()

        if parent is None:
            return

        try:
            self.current_page = NotificationsPage(
                parent,
                self.show_dashboard_page,
            )
            self.current_page.pack(
                fill="both",
                expand=True,
            )
        except Exception as error:
            messagebox.showerror(
                "Notifications Error",
                f"Could not open Notifications.\n\n{error}",
                parent=self,
            )

    def show_settings(self):
        parent = self.prepare_page()

        if parent is None:
            return

        try:
            self.current_page = SettingsPage(
                parent,
                self.show_dashboard_page,
                self.current_user_id,
                self.current_user or "",
                self.current_role or "User",
                self.logout,
            )
            self.current_page.pack(
                fill="both",
                expand=True,
            )
        except Exception as error:
            messagebox.showerror(
                "Settings Error",
                f"Could not open Settings.\n\n{error}",
                parent=self,
            )

    # ======================================================
    # PROFILE
    # ======================================================

    def show_profile(self):
        if not self.current_user:
            return

        profile_window = ctk.CTkToplevel(self)
        profile_window.title("User Profile")
        profile_window.geometry("380x300")
        profile_window.resizable(False, False)

        profile_window.transient(self)
        profile_window.grab_set()

        ctk.CTkLabel(
            profile_window,
            text="User Profile",
            font=("Arial", 23, "bold"),
        ).pack(
            padx=20,
            pady=(25, 20),
        )

        ctk.CTkLabel(
            profile_window,
            text=f"Username: {self.current_user}",
            font=("Arial", 15),
        ).pack(
            anchor="w",
            padx=30,
            pady=8,
        )

        ctk.CTkLabel(
            profile_window,
            text=f"Role: {self.current_role}",
            font=("Arial", 15),
        ).pack(
            anchor="w",
            padx=30,
            pady=8,
        )

        ctk.CTkLabel(
            profile_window,
            text=f"User ID: {self.current_user_id}",
            font=("Arial", 15),
        ).pack(
            anchor="w",
            padx=30,
            pady=8,
        )

        ctk.CTkButton(
            profile_window,
            text="Close",
            command=profile_window.destroy,
        ).pack(
            padx=25,
            pady=20,
        )

    # ======================================================
    # TOUCH MODE
    # ======================================================

    def toggle_touch_mode(self):
        self.touch_mode = not self.touch_mode

        if self.touch_mode:
            self.apply_touch_mode()
            messagebox.showinfo(
                "Touch Mode",
                "Touch mode enabled.\n"
                "Controls will use larger fonts and spacing.",
                parent=self,
            )
        else:
            self.restore_widget_settings()
            self.show_dashboard_page()

    def apply_touch_mode(self):
        """Increase supported widget dimensions for touch use."""

        if not self.touch_mode:
            return

        self._original_widget_settings = {}

        def resize_widget(widget):
            try:
                settings = {}

                for option in ("width", "height", "font"):
                    try:
                        settings[option] = widget.cget(option)
                    except Exception:
                        pass

                self._original_widget_settings[widget] = settings

                if isinstance(widget, (ctk.CTkButton, ctk.CTkEntry)):
                    try:
                        old_height = int(widget.cget("height"))
                        widget.configure(
                            height=max(old_height, 45)
                        )
                    except Exception:
                        pass

                try:
                    old_font = widget.cget("font")

                    if isinstance(old_font, (tuple, list)):
                        if len(old_font) >= 2:
                            font_name = old_font[0]
                            font_size = old_font[1]
                            extra = tuple(old_font[2:])

                            widget.configure(
                                font=(
                                    font_name,
                                    max(14, int(font_size)),
                                    *extra,
                                )
                            )
                except Exception:
                    pass

            except Exception:
                pass

            try:
                for child in widget.winfo_children():
                    resize_widget(child)
            except Exception:
                pass

        resize_widget(self)

    def restore_widget_settings(self):
        """Restore the original widget dimensions and fonts."""

        for widget, settings in list(
            self._original_widget_settings.items()
        ):
            try:
                if not widget.winfo_exists():
                    continue

                for option, value in settings.items():
                    try:
                        widget.configure(**{option: value})
                    except Exception:
                        pass
            except Exception:
                pass

        self._original_widget_settings.clear()

    # ======================================================
    # ON-SCREEN KEYBOARD
    # ======================================================

    def open_on_screen_keyboard(self):
        """Open the Windows on-screen keyboard."""

        try:
            subprocess.Popen(
                ["osk.exe"],
                shell=False,
            )
        except Exception:
            try:
                os.startfile(
                    os.path.join(
                        os.environ.get("WINDIR", r"C:\Windows"),
                        "System32",
                        "osk.exe",
                    )
                )
            except Exception as error:
                messagebox.showwarning(
                    "Keyboard",
                    f"Could not open the on-screen keyboard.\n\n{error}",
                    parent=self,
                )

    # ======================================================
    # LOGOUT AND CLOSE
    # ======================================================

    def logout(self):
        if not self.current_user:
            self.show_login()
            return

        confirm = messagebox.askyesno(
            "Logout",
            "Are you sure you want to log out?",
            parent=self,
        )

        if not confirm:
            return

        self.current_user = None
        self.current_user_id = None
        self.current_role = None

        self.show_login()

    def on_close(self):
        if self.current_user:
            confirm = messagebox.askyesno(
                "Exit Application",
                "Are you sure you want to close the application?",
                parent=self,
            )

            if not confirm:
                return

        self.destroy()


# ==========================================================
# APPLICATION ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    app = PharmacyApp()
    app.mainloop()