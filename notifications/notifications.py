import customtkinter as ctk # type: ignore

from tkinter import ttk, messagebox
from database import get_connection
from datetime import datetime, date, timedelta

# ------------------------------------------------------------
# Design tokens: (light, dark) pairs so the page follows the theme
# ------------------------------------------------------------
EXPIRY_WARNING_DAYS = 30

COLOR_CRITICAL = ("#C62828", "#EF5350")   # expired / out of stock
COLOR_WARNING = ("#E65100", "#FFA726")    # expiring soon
COLOR_INFO = ("#1565C0", "#64B5F6")       # low stock
COLOR_OK = ("#2E7D32", "#66BB6A")

# Row tints for the table (light, dark)
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

        self.create_ui()
        self.load_notifications()

    # ============================================================
    # UI
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

        ctk.CTkButton(
            header,
            text="🔄 Refresh",
            width=120,
            height=36,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "gray90"),
            command=self.load_notifications
        ).pack(side="right", padx=8)

        # ---------------- Summary cards ----------------
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=17, pady=(20, 5))

        for column in range(3):
            cards.grid_columnconfigure(column, weight=1, uniform="cards")

        self.low_stock_card = self.create_card(
            cards, "📦 Low stock", "At or below minimum", COLOR_INFO
        )
        self.expired_card = self.create_card(
            cards, "🔴 Expired", "Remove from shelves", COLOR_CRITICAL
        )
        self.expiring_card = self.create_card(
            cards, f"⚠️ Expiring soon", f"Within {EXPIRY_WARNING_DAYS} days", COLOR_WARNING
        )

        self.low_stock_card.grid(row=0, column=0, padx=8, sticky="nsew")
        self.expired_card.grid(row=0, column=1, padx=8, sticky="nsew")
        self.expiring_card.grid(row=0, column=2, padx=8, sticky="nsew")

        # ---------------- Table panel ----------------
        panel = ctk.CTkFrame(self, corner_radius=12)
        panel.pack(fill="both", expand=True, padx=25, pady=(15, 20))

        toolbar = ctk.CTkFrame(panel, fg_color="transparent")
        toolbar.pack(fill="x", padx=15, pady=(15, 10))

        self.filter_var = ctk.StringVar(value="All")
        self.filter_buttons = ctk.CTkSegmentedButton(
            toolbar,
            values=FILTERS,
            variable=self.filter_var,
            command=lambda _value: self.render_rows()
        )
        self.filter_buttons.pack(side="left")

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.render_rows())

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
        self.result_label.pack(fill="x", padx=17, pady=(0, 6))

        # Container that swaps between the table and the empty state
        self.body = ctk.CTkFrame(panel, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.create_table(self.body)
        self.create_empty_state(self.body)

    # ------------------------------------------------------------

    def create_table(self, parent):

        self.tree_wrap = ctk.CTkFrame(parent, fg_color="transparent")
        self.tree_wrap.pack(fill="both", expand=True)

        columns = ("medicine", "batch", "quantity", "min_stock", "expiry", "days", "status")

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

        for key, (text, width, anchor) in headings.items():
            self.notification_tree.heading(key, text=text, anchor=anchor)
            self.notification_tree.column(
                key,
                width=width,
                anchor=anchor,
                stretch=(key in ("medicine", "status"))
            )

        scrollbar = ctk.CTkScrollbar(
            self.tree_wrap,
            orientation="vertical",
            command=self.notification_tree.yview
        )
        self.notification_tree.configure(yscrollcommand=scrollbar.set)

        self.notification_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y", padx=(6, 0))

    def create_empty_state(self, parent):

        self.empty_frame = ctk.CTkFrame(parent, fg_color="transparent")

        self.empty_icon = ctk.CTkLabel(
            self.empty_frame, text="✅", font=ctk.CTkFont(size=48)
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

    # ------------------------------------------------------------

    def create_card(self, parent, title, caption, accent):

        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid_columnconfigure(1, weight=1)

        # Colored accent bar on the left
        ctk.CTkFrame(
            card,
            width=6,
            corner_radius=3,
            fg_color=accent
        ).grid(row=0, column=0, sticky="ns", padx=(10, 0), pady=12)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.grid(row=0, column=1, sticky="nsew", padx=14, pady=12)

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
        """Match the ttk table to the current light/dark appearance."""

        dark = ctk.get_appearance_mode() == "Dark"

        bg = "#2b2b2b" if dark else "#ffffff"
        fg = "#e6e6e6" if dark else "#1a1a1a"
        head_bg = "#3a3a3a" if dark else "#eceff1"
        selected = "#1f6aa5"

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Alerts.Treeview",
            background=bg,
            fieldbackground=bg,
            foreground=fg,
            rowheight=36,
            borderwidth=0,
            font=("Segoe UI", 11)
        )
        style.configure(
            "Alerts.Treeview.Heading",
            background=head_bg,
            foreground=fg,
            relief="flat",
            padding=(8, 8),
            font=("Segoe UI", 11, "bold")
        )
        style.map(
            "Alerts.Treeview",
            background=[("selected", selected)],
            foreground=[("selected", "#ffffff")]
        )
        style.map(
            "Alerts.Treeview.Heading",
            background=[("active", head_bg)]
        )

        index = 1 if dark else 0
        for tag, tint in ROW_TINTS.items():
            light_bg, dark_bg, light_fg, dark_fg = tint
            self.notification_tree.tag_configure(
                tag,
                background=dark_bg if dark else light_bg,
                foreground=dark_fg if dark else light_fg
            )

    # ============================================================
    # DATA
    # ============================================================

    @staticmethod
    def parse_date(value):
        for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(str(value), fmt).date()
            except ValueError:
                continue
        return None

    def load_notifications(self):

        try:
            connection = get_connection()
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
            connection.close()

            today = date.today()
            expiry_limit = today + timedelta(days=EXPIRY_WARNING_DAYS)

            rows = []
            low_stock_count = 0
            expired_count = 0
            expiring_count = 0

            for medicine in medicines:

                quantity = medicine["quantity"] or 0
                min_stock = medicine["min_stock"] or 0
                expiry_text = medicine["expiry_date"]
                expiry_date = self.parse_date(expiry_text)

                statuses = []
                categories = set()
                severity = 99
                days_text = "-"

                # Stock
                if quantity <= min_stock:
                    low_stock_count += 1
                    categories.add("Low stock")
                    if quantity == 0:
                        statuses.append("Out of stock")
                        severity = min(severity, 0)
                    else:
                        statuses.append("Low stock")
                        severity = min(severity, 3)

                # Expiry
                if expiry_date is not None:
                    days_left = (expiry_date - today).days

                    if days_left < 0:
                        expired_count += 1
                        categories.add("Expired")
                        statuses.append("Expired")
                        severity = min(severity, 0)
                        days_text = f"{abs(days_left)} days ago"

                    elif days_left == 0:
                        expired_count += 1
                        categories.add("Expired")
                        statuses.append("Expires today")
                        severity = min(severity, 1)
                        days_text = "Today"

                    elif expiry_date <= expiry_limit:
                        expiring_count += 1
                        categories.add("Expiring soon")
                        statuses.append("Expiring soon")
                        severity = min(severity, 2)
                        days_text = f"{days_left} days"

                    else:
                        days_text = f"{days_left} days"

                if not statuses:
                    continue

                if severity <= 0:
                    tag = "critical"
                elif "Expiring soon" in statuses or "Expires today" in statuses:
                    tag = "expiring"
                else:
                    tag = "low_stock"

                rows.append({
                    "name": medicine["name"],
                    "batch": medicine["batch_no"],
                    "quantity": quantity,
                    "min_stock": min_stock,
                    "expiry": expiry_text,
                    "days": days_text,
                    "status": "  •  ".join(statuses),
                    "categories": categories,
                    "severity": severity,
                    "sort_date": expiry_date or date.max,
                    "tag": tag,
                })

            # Most urgent first, then soonest expiry
            rows.sort(key=lambda row: (row["severity"], row["sort_date"]))
            self.all_rows = rows

            self.low_stock_card.value_label.configure(text=str(low_stock_count))
            self.expired_card.value_label.configure(text=str(expired_count))
            self.expiring_card.value_label.configure(text=str(expiring_count))

            self.render_rows()

        except Exception as error:

            messagebox.showerror(
                "Notifications Error",
                f"Unable to load notifications.\n\n{error}"
            )
            print("Notifications error:", error)

    # ============================================================
    # RENDER
    # ============================================================

    def render_rows(self):

        self.apply_tree_style()

        for item in self.notification_tree.get_children():
            self.notification_tree.delete(item)

        selected_filter = self.filter_var.get()
        search = self.search_var.get().strip().lower()

        visible = []
        for row in self.all_rows:

            if selected_filter != "All" and selected_filter not in row["categories"]:
                continue

            if search and search not in str(row["name"]).lower() \
                    and search not in str(row["batch"]).lower():
                continue

            visible.append(row)

        for row in visible:
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
                    row["status"],
                ),
                tags=(row["tag"],)
            )

        total = len(self.all_rows)
        if total:
            self.result_label.configure(
                text=f"Showing {len(visible)} of {total} alerts  •  "
                     f"Updated {datetime.now():%d %b %Y, %I:%M %p}"
            )
        else:
            self.result_label.configure(
                text=f"Updated {datetime.now():%d %b %Y, %I:%M %p}"
            )

        self.show_body(has_rows=bool(visible), has_alerts=bool(total))

    def show_body(self, has_rows, has_alerts):

        if has_rows:
            self.empty_frame.pack_forget()
            self.tree_wrap.pack(fill="both", expand=True)
            return

        self.tree_wrap.pack_forget()

        if has_alerts:
            self.empty_icon.configure(text="🔎")
            self.empty_title.configure(text="No matching alerts")
            self.empty_text.configure(text="Try a different filter or search term.")
        else:
            self.empty_icon.configure(text="✅")
            self.empty_title.configure(text="Nothing needs attention")
            self.empty_text.configure(
                text="Stock levels and expiry dates are all in good shape."
            )

        self.empty_frame.pack(fill="both", expand=True)