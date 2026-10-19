import customtkinter as ctk  # type: ignore

import sqlite3
from tkinter import ttk, messagebox
from database import get_connection
from datetime import datetime, date, timedelta


# ============================================================
# CONFIGURATION
# ============================================================

EXPIRY_WARNING_DAYS = 30

COLOR_CRITICAL = ("#C62828", "#EF5350")
COLOR_WARNING = ("#E65100", "#FFA726")
COLOR_INFO = ("#1565C0", "#64B5F6")
COLOR_OK = ("#2E7D32", "#66BB6A")

ROW_TINTS = {
    "critical": ("#FDECEA", "#3B2224", "#B71C1C", "#FF8A80"),
    "expiring": ("#FFF3E0", "#3A2F1E", "#BF360C", "#FFCC80"),
    "low_stock": ("#E8F1FB", "#1F2D3D", "#0D47A1", "#90CAF9"),
}

FILTERS = ["All", "Low stock", "Expired", "Expiring soon"]


class NotificationsPage(ctk.CTkFrame):

    def __init__(self, parent, back_callback):
        super().__init__(parent, fg_color="transparent")

        self.back_callback = back_callback
        self.all_rows = []
        self.loading = False

        self.create_ui()
        self.load_notifications()

    # ============================================================
    # USER INTERFACE
    # ============================================================

    def create_ui(self):

        # ---------------- Header ----------------
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(25, 0))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="🔔 Notifications",
            font=ctk.CTkFont(size=30, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Low stock, expired and soon-to-expire medicines",
            font=ctk.CTkFont(size=14),
            text_color=("gray35", "gray65")
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkButton(
            header,
            text="🏠 Dashboard",
            width=130,
            height=36,
            command=self.back_callback
        ).pack(side="right", padx=(8, 0))

        self.refresh_button = ctk.CTkButton(
            header,
            text="🔄 Refresh",
            width=120,
            height=36,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "gray90"),
            command=self.load_notifications
        )
        self.refresh_button.pack(side="right", padx=8)

        # ---------------- Summary Cards ----------------
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=17, pady=(20, 5))

        for column in range(3):
            cards.grid_columnconfigure(column, weight=1, uniform="cards")

        self.low_stock_card = self.create_card(
            cards,
            "📦 Low stock",
            "At or below minimum",
            COLOR_INFO
        )

        self.expired_card = self.create_card(
            cards,
            "🔴 Expired",
            "Already expired",
            COLOR_CRITICAL
        )

        self.expiring_card = self.create_card(
            cards,
            "⚠️ Expiring soon",
            f"Within {EXPIRY_WARNING_DAYS} days",
            COLOR_WARNING
        )

        self.low_stock_card.grid(
            row=0, column=0, padx=8, sticky="nsew"
        )

        self.expired_card.grid(
            row=0, column=1, padx=8, sticky="nsew"
        )

        self.expiring_card.grid(
            row=0, column=2, padx=8, sticky="nsew"
        )

        # ---------------- Main Panel ----------------
        panel = ctk.CTkFrame(self, corner_radius=12)
        panel.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(15, 20)
        )

        toolbar = ctk.CTkFrame(
            panel,
            fg_color="transparent"
        )
        toolbar.pack(
            fill="x",
            padx=15,
            pady=(15, 10)
        )

        self.filter_var = ctk.StringVar(value="All")

        self.filter_buttons = ctk.CTkSegmentedButton(
            toolbar,
            values=FILTERS,
            variable=self.filter_var,
            command=lambda _value: self.render_rows()
        )
        self.filter_buttons.pack(side="left")

        self.search_var = ctk.StringVar()

        self.search_var.trace_add(
            "write",
            lambda *_: self.render_rows()
        )

        ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            placeholder_text="🔍 Search medicine or batch",
            width=260,
            height=32
        ).pack(side="right")

        self.result_label = ctk.CTkLabel(
            panel,
            text="",
            anchor="w",
            font=ctk.CTkFont(size=13),
            text_color=("gray35", "gray65")
        )

        self.result_label.pack(
            fill="x",
            padx=17,
            pady=(0, 6)
        )

        # ---------------- Content Area ----------------
        self.body = ctk.CTkFrame(
            panel,
            fg_color="transparent"
        )

        self.body.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.create_table(self.body)
        self.create_empty_state(self.body)

    # ============================================================
    # TABLE
    # ============================================================

    def create_table(self, parent):

        self.tree_wrap = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        columns = (
            "medicine",
            "batch",
            "quantity",
            "min_stock",
            "expiry",
            "days",
            "status"
        )

        self.notification_tree = ttk.Treeview(
            self.tree_wrap,
            columns=columns,
            show="headings",
            style="Alerts.Treeview",
            selectmode="browse"
        )

        headings = {
            "medicine": ("Medicine", 210, "w"),
            "batch": ("Batch No.", 120, "w"),
            "quantity": ("Qty", 70, "center"),
            "min_stock": ("Min stock", 90, "center"),
            "expiry": ("Expiry date", 110, "center"),
            "days": ("Time left", 110, "center"),
            "status": ("Status", 200, "w"),
        }

        for key, (heading, width, anchor) in headings.items():

            self.notification_tree.heading(
                key,
                text=heading,
                anchor=anchor
            )

            self.notification_tree.column(
                key,
                width=width,
                anchor=anchor,
                stretch=key in ("medicine", "status")
            )

        scrollbar = ctk.CTkScrollbar(
            self.tree_wrap,
            orientation="vertical",
            command=self.notification_tree.yview
        )

        self.notification_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.notification_tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y",
            padx=(6, 0)
        )

    # ============================================================
    # EMPTY STATE
    # ============================================================

    def create_empty_state(self, parent):

        self.empty_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        self.empty_icon = ctk.CTkLabel(
            self.empty_frame,
            text="✅",
            font=ctk.CTkFont(size=48)
        )

        self.empty_icon.pack(pady=(60, 8))

        self.empty_title = ctk.CTkLabel(
            self.empty_frame,
            text="Nothing needs attention",
            font=ctk.CTkFont(size=20, weight="bold")
        )

        self.empty_title.pack()

        self.empty_text = ctk.CTkLabel(
            self.empty_frame,
            text="Stock levels and expiry dates are all in good shape.",
            font=ctk.CTkFont(size=14),
            text_color=("gray35", "gray65")
        )

        self.empty_text.pack(pady=(4, 0))

    # ============================================================
    # SUMMARY CARDS
    # ============================================================

    def create_card(self, parent, title, caption, accent):

        card = ctk.CTkFrame(
            parent,
            corner_radius=12
        )

        card.grid_columnconfigure(1, weight=1)

        ctk.CTkFrame(
            card,
            width=6,
            corner_radius=3,
            fg_color=accent
        ).grid(
            row=0,
            column=0,
            sticky="ns",
            padx=(10, 0),
            pady=12
        )

        content = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        content.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=14,
            pady=12
        )

        ctk.CTkLabel(
            content,
            text=title,
            anchor="w",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(fill="x")

        value_label = ctk.CTkLabel(
            content,
            text="0",
            anchor="w",
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color=accent
        )

        value_label.pack(fill="x")

        ctk.CTkLabel(
            content,
            text=caption,
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=("gray35", "gray65")
        ).pack(fill="x")

        card.value_label = value_label

        return card

    # ============================================================
    # TABLE THEME
    # ============================================================

    def apply_tree_style(self):

        dark = ctk.get_appearance_mode() == "Dark"

        background = "#2b2b2b" if dark else "#ffffff"
        foreground = "#e6e6e6" if dark else "#1a1a1a"
        heading_background = "#3a3a3a" if dark else "#eceff1"
        selected_background = "#1f6aa5"

        style = ttk.Style()

        style.theme_use("clam")

        style.configure(
            "Alerts.Treeview",
            background=background,
            fieldbackground=background,
            foreground=foreground,
            rowheight=36,
            borderwidth=0,
            font=("Segoe UI", 11)
        )

        style.configure(
            "Alerts.Treeview.Heading",
            background=heading_background,
            foreground=foreground,
            relief="flat",
            padding=(8, 8),
            font=("Segoe UI", 11, "bold")
        )

        style.map(
            "Alerts.Treeview",
            background=[
                ("selected", selected_background)
            ],
            foreground=[
                ("selected", "#ffffff")
            ]
        )

        style.map(
            "Alerts.Treeview.Heading",
            background=[
                ("active", heading_background)
            ]
        )

        for tag, tint in ROW_TINTS.items():

            light_background, dark_background, light_foreground, dark_foreground = tint

            self.notification_tree.tag_configure(
                tag,
                background=dark_background if dark else light_background,
                foreground=dark_foreground if dark else light_foreground
            )

    # ============================================================
    # DATE PARSING
    # ============================================================

    @staticmethod
    def parse_date(value):

        if value is None:
            return None

        value = str(value).strip()

        if not value:
            return None

        formats = (
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%d/%m/%Y",
            "%Y-%m-%d %H:%M:%S"
        )

        for date_format in formats:

            try:
                return datetime.strptime(
                    value,
                    date_format
                ).date()

            except ValueError:
                continue

        return None

    # ============================================================
    # LOAD NOTIFICATIONS
    # ============================================================

    def load_notifications(self):

        if self.loading:
            return

        self.loading = True
        self.refresh_button.configure(state="disabled")

        try:

            # Use the project's managed connection pattern.
            with get_connection() as connection:

                cursor = connection.cursor()

                cursor.execute("""
                    SELECT
                        medicine_id,
                        name,
                        batch_no,
                        quantity,
                        min_stock,
                        expiry_date
                    FROM medicines
                    ORDER BY expiry_date ASC
                """)

                medicines = cursor.fetchall()

            today = date.today()

            expiry_limit = today + timedelta(
                days=EXPIRY_WARNING_DAYS
            )

            rows = []

            low_stock_count = 0
            expired_count = 0
            expiring_count = 0

            for medicine in medicines:

                quantity = int(
                    medicine["quantity"] or 0
                )

                min_stock = int(
                    medicine["min_stock"] or 0
                )

                expiry_text = medicine["expiry_date"]

                expiry_date = self.parse_date(
                    expiry_text
                )

                statuses = []
                categories = set()

                severity = 99
                days_text = "-"

                # ---------------- Stock Alerts ----------------
                if quantity <= min_stock:

                    low_stock_count += 1

                    categories.add("Low stock")

                    if quantity <= 0:

                        statuses.append("Out of stock")
                        severity = min(severity, 0)

                    else:

                        statuses.append("Low stock")
                        severity = min(severity, 3)

                # ---------------- Expiry Alerts ----------------
                if expiry_date is not None:

                    days_left = (
                        expiry_date - today
                    ).days

                    if days_left < 0:

                        expired_count += 1

                        categories.add("Expired")

                        statuses.append("Expired")

                        severity = min(
                            severity,
                            0
                        )

                        days_text = (
                            f"{abs(days_left)} days ago"
                        )

                    elif days_left == 0:

                        # Expiring today is NOT already expired.
                        expiring_count += 1

                        categories.add("Expiring soon")

                        statuses.append("Expires today")

                        severity = min(
                            severity,
                            1
                        )

                        days_text = "Today"

                    elif days_left <= EXPIRY_WARNING_DAYS:

                        expiring_count += 1

                        categories.add("Expiring soon")

                        statuses.append("Expiring soon")

                        severity = min(
                            severity,
                            2
                        )

                        days_text = f"{days_left} days"

                    else:

                        days_text = f"{days_left} days"

                # No alert is needed for this medicine.
                if not statuses:
                    continue

                # ---------------- Row Severity ----------------
                if severity <= 0:

                    tag = "critical"

                elif (
                    "Expiring soon" in statuses
                    or "Expires today" in statuses
                ):

                    tag = "expiring"

                else:

                    tag = "low_stock"

                rows.append({
                    "medicine_id": medicine["medicine_id"],
                    "name": medicine["name"] or "",
                    "batch": medicine["batch_no"] or "",
                    "quantity": quantity,
                    "min_stock": min_stock,
                    "expiry": expiry_text or "-",
                    "days": days_text,
                    "status": "  •  ".join(statuses),
                    "categories": categories,
                    "severity": severity,
                    "sort_date": expiry_date or date.max,
                    "tag": tag
                })

            # Critical alerts first, followed by expiry date.
            rows.sort(
                key=lambda row: (
                    row["severity"],
                    row["sort_date"],
                    row["name"].lower()
                )
            )

            self.all_rows = rows

            # Update the summary cards.
            self.low_stock_card.value_label.configure(
                text=str(low_stock_count)
            )

            self.expired_card.value_label.configure(
                text=str(expired_count)
            )

            self.expiring_card.value_label.configure(
                text=str(expiring_count)
            )

            self.render_rows()

        except (sqlite3.Error, KeyError, TypeError, ValueError) as error:

            messagebox.showerror(
                "Notifications Error",
                "Unable to load medicine notifications.\n\n"
                f"Details: {error}",
                parent=self.winfo_toplevel()
            )

            print(
                "Notifications database/data error:",
                error
            )

        except Exception as error:

            messagebox.showerror(
                "Notifications Error",
                "An unexpected error occurred while loading notifications.\n\n"
                f"Details: {error}",
                parent=self.winfo_toplevel()
            )

            print(
                "Unexpected notifications error:",
                error
            )

        finally:

            self.loading = False

            try:
                self.refresh_button.configure(
                    state="normal"
                )
            except Exception:
                pass

    # ============================================================
    # RENDER TABLE
    # ============================================================

    def render_rows(self):

        if not hasattr(self, "notification_tree"):
            return

        self.apply_tree_style()

        # Clear the existing table.
        for item in self.notification_tree.get_children():
            self.notification_tree.delete(item)

        selected_filter = self.filter_var.get()

        search_text = (
            self.search_var.get()
            .strip()
            .lower()
        )

        visible_rows = []

        for row in self.all_rows:

            # Apply category filter.
            if (
                selected_filter != "All"
                and selected_filter not in row["categories"]
            ):
                continue

            # Apply medicine/batch search.
            medicine_name = str(
                row["name"]
            ).lower()

            batch_number = str(
                row["batch"]
            ).lower()

            if search_text:

                if (
                    search_text not in medicine_name
                    and search_text not in batch_number
                ):
                    continue

            visible_rows.append(row)

        # Insert matching alerts.
        for row in visible_rows:

            self.notification_tree.insert(
                "",
                "end",
                values=(
                    row["name"],
                    row["batch"],
                    row["quantity"],
                    row["min_stock"],
                    row["expiry"],
                    row["days"],
                    row["status"]
                ),
                tags=(row["tag"],)
            )

        total_alerts = len(self.all_rows)
        visible_count = len(visible_rows)

        updated_at = datetime.now().strftime(
            "%d %b %Y, %I:%M %p"
        )

        if total_alerts:

            self.result_label.configure(
                text=(
                    f"Showing {visible_count} of "
                    f"{total_alerts} alerts  •  "
                    f"Updated {updated_at}"
                )
            )

        else:

            self.result_label.configure(
                text=f"Updated {updated_at}"
            )

        self.show_body(
            has_rows=bool(visible_rows),
            has_alerts=bool(total_alerts)
        )

    # ============================================================
    # SHOW TABLE OR EMPTY STATE
    # ============================================================

    def show_body(self, has_rows, has_alerts):

        if has_rows:

            self.empty_frame.pack_forget()

            self.tree_wrap.pack(
                fill="both",
                expand=True
            )

            return

        self.tree_wrap.pack_forget()

        if has_alerts:

            self.empty_icon.configure(
                text="🔎"
            )

            self.empty_title.configure(
                text="No matching alerts"
            )

            self.empty_text.configure(
                text="Try a different filter or search term."
            )

        else:

            self.empty_icon.configure(
                text="✅"
            )

            self.empty_title.configure(
                text="Nothing needs attention"
            )

            self.empty_text.configure(
                text=(
                    "Stock levels and expiry dates "
                    "are all in good shape."
                )
            )

        self.empty_frame.pack(
            fill="both",
            expand=True
        )