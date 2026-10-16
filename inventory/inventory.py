import customtkinter as ctk # type: ignore

from ui_kit import styled_treeview
from tkinter import ttk
from datetime import datetime, timedelta

from database import get_connection


class InventoryPage(ctk.CTkFrame):

    def __init__(self, parent, back_to_dashboard):

        super().__init__(parent, fg_color="transparent")

        self.back_to_dashboard = back_to_dashboard

        self.search_var = ctk.StringVar()
        self.filter_var = ctk.StringVar(value="All")

        self.build_ui()
        self.load_inventory()

    # =========================================================
    # MAIN UI
    # =========================================================

    def build_ui(self):

        # ---------------- HEADER ----------------

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=25,
            pady=(20, 10)
        )

        title = ctk.CTkLabel(
            header,
            text="📦 Inventory Management",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        )

        title.pack(side="left")

        back_button = ctk.CTkButton(
            header,
            text="← Back to Dashboard",
            command=self.back_to_dashboard,
            width=160,
            height=38
        )

        back_button.pack(side="right")

        # ---------------- SUMMARY CARDS ----------------

        summary_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        summary_frame.pack(
            fill="x",
            padx=25,
            pady=10
        )

        self.in_stock_label = self.create_summary_card(
            summary_frame,
            "🟢 In Stock",
            0
        )

        self.low_stock_label = self.create_summary_card(
            summary_frame,
            "🟡 Low Stock",
            1
        )

        self.out_stock_label = self.create_summary_card(
            summary_frame,
            "🔴 Out of Stock",
            2
        )

        self.expired_label = self.create_summary_card(
            summary_frame,
            "⚫ Expired",
            3
        )

        self.near_expiry_label = self.create_summary_card(
            summary_frame,
            "🟠 Near Expiry",
            4
        )

        # ---------------- SEARCH / FILTER ----------------

        control_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        control_frame.pack(
            fill="x",
            padx=25,
            pady=(5, 10)
        )

        search_entry = ctk.CTkEntry(
            control_frame,
            textvariable=self.search_var,
            placeholder_text="Search medicine, category, batch or supplier...",
            height=40
        )

        search_entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        search_entry.bind(
            "<KeyRelease>",
            lambda event: self.load_inventory()
        )

        filter_menu = ctk.CTkOptionMenu(
            control_frame,
            variable=self.filter_var,
            values=[
                "All",
                "In Stock",
                "Low Stock",
                "Out of Stock",
                "Expired",
                "Near Expiry"
            ],
            command=lambda value: self.load_inventory(),
            width=150,
            height=40
        )

        filter_menu.pack(
            side="left",
            padx=10
        )

        refresh_button = ctk.CTkButton(
            control_frame,
            text="🔄 Refresh",
            width=110,
            height=40,
            command=self.load_inventory
        )

        refresh_button.pack(side="left")

        # ---------------- TABLE ----------------

        table_container = ctk.CTkFrame(
            self
        )

        table_container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(5, 25)
        )

        columns = (
            "id",
            "name",
            "category",
            "batch",
            "supplier",
            "quantity",
            "min_stock",
            "expiry",
            "status"
        )

        self.tree = styled_treeview(
            table_container,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": "ID",
            "name": "Medicine Name",
            "category": "Category",
            "batch": "Batch Number",
            "supplier": "Supplier",
            "quantity": "Quantity",
            "min_stock": "Min Stock",
            "expiry": "Expiry Date",
            "status": "Status"
        }

        widths = {
            "id": 55,
            "name": 170,
            "category": 110,
            "batch": 120,
            "supplier": 150,
            "quantity": 80,
            "min_stock": 80,
            "expiry": 110,
            "status": 120
        }

        for column in columns:

            self.tree.heading(
                column,
                text=headings[column]
            )

            self.tree.column(
                column,
                width=widths[column],
                anchor="center"
            )

        # ---------------- STATUS COLORS ----------------

        self.tree.tag_configure(
            "in_stock",
            foreground="green"
        )

        self.tree.tag_configure(
            "low_stock",
            foreground="orange"
        )

        self.tree.tag_configure(
            "out_of_stock",
            foreground="red"
        )

        self.tree.tag_configure(
            "expired",
            foreground="red"
        )

        self.tree.tag_configure(
            "near_expiry",
            foreground="darkorange"
        )

        self.tree.tag_configure(
            "unknown",
            foreground="gray"
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        # ---------------- SCROLLBAR ----------------

        scrollbar = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.tree.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        # ---------------- EMPTY MESSAGE ----------------

        self.empty_label = ctk.CTkLabel(
            table_container,
            text="",
            font=ctk.CTkFont(
                size=15
            )
        )

    # =========================================================
    # SUMMARY CARD
    # =========================================================

    def create_summary_card(
        self,
        parent,
        title,
        column
    ):

        parent.grid_columnconfigure(
            column,
            weight=1
        )

        card = ctk.CTkFrame(
            parent,
            corner_radius=10
        )

        card.grid(
            row=0,
            column=column,
            padx=5,
            sticky="ew"
        )

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(
                size=13
            )
        )

        title_label.pack(
            pady=(12, 3)
        )

        value_label = ctk.CTkLabel(
            card,
            text="0",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        value_label.pack(
            pady=(0, 12)
        )

        return value_label

    # =========================================================
    # GET STATUS
    # =========================================================

    def get_status(
        self,
        quantity,
        minimum_stock,
        expiry_date
    ):

        try:

            quantity = int(quantity or 0)
            minimum_stock = int(minimum_stock or 0)

            today = datetime.now().date()

            if not expiry_date:
                expiry = None

            else:

                expiry_text = str(expiry_date).strip()

                try:
                    expiry = datetime.strptime(
                        expiry_text,
                        "%Y-%m-%d"
                    ).date()

                except ValueError:

                    expiry = datetime.strptime(
                        expiry_text,
                        "%d-%m-%Y"
                    ).date()

            # ---------------- EXPIRED ----------------

            if expiry and expiry < today:
                return "Expired"

            # ---------------- OUT OF STOCK ----------------

            if quantity <= 0:
                return "Out of Stock"

            # ---------------- NEAR EXPIRY ----------------

            if expiry:

                if expiry <= today + timedelta(days=30):
                    return "Near Expiry"

            # ---------------- LOW STOCK ----------------

            if quantity <= minimum_stock:
                return "Low Stock"

            # ---------------- NORMAL ----------------

            return "In Stock"

        except Exception:

            return "Unknown"

    # =========================================================
    # LOAD INVENTORY
    # =========================================================

    def load_inventory(self):

        # Clear old rows

        for item in self.tree.get_children():

            self.tree.delete(item)

        try:

            connection = get_connection()

            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    m.medicine_id,
                    m.name,
                    m.category,
                    m.batch_no,
                    COALESCE(s.name, 'Not Assigned') AS supplier_name,
                    m.quantity,
                    m.min_stock,
                    m.expiry_date
                FROM medicines m
                LEFT JOIN suppliers s
                    ON m.supplier_id = s.supplier_id
                ORDER BY m.medicine_id DESC
                """
            )

            medicines = cursor.fetchall()

            connection.close()

            # ---------------- COUNTERS ----------------

            counts = {
                "In Stock": 0,
                "Low Stock": 0,
                "Out of Stock": 0,
                "Expired": 0,
                "Near Expiry": 0
            }

            search_text = (
                self.search_var.get()
                .strip()
                .lower()
            )

            selected_filter = self.filter_var.get()

            visible_rows = 0

            for medicine in medicines:

                # ---------------- READ DATA ----------------

                try:

                    medicine_id = medicine["medicine_id"]
                    name = medicine["name"]
                    category = medicine["category"]
                    batch = medicine["batch_no"]
                    supplier = medicine["supplier_name"]
                    quantity = medicine["quantity"]
                    minimum_stock = medicine["min_stock"]
                    expiry = medicine["expiry_date"]

                except Exception:

                    medicine_id = medicine[0]
                    name = medicine[1]
                    category = medicine[2]
                    batch = medicine[3]
                    supplier = medicine[4]
                    quantity = medicine[5]
                    minimum_stock = medicine[6]
                    expiry = medicine[7]

                # ---------------- CLEAN DATA ----------------

                name = name or ""
                category = category or ""
                batch = batch or ""
                supplier = supplier or "Not Assigned"
                quantity = quantity or 0
                minimum_stock = minimum_stock or 0
                expiry = expiry or ""

                # ---------------- STATUS ----------------

                status = self.get_status(
                    quantity,
                    minimum_stock,
                    expiry
                )

                # Count every medicine before applying filter

                if status in counts:

                    counts[status] += 1

                # ---------------- SEARCH ----------------

                if search_text:

                    search_content = (
                        f"{name} "
                        f"{category} "
                        f"{batch} "
                        f"{supplier}"
                    ).lower()

                    if search_text not in search_content:

                        continue

                # ---------------- FILTER ----------------

                if (
                    selected_filter != "All"
                    and status != selected_filter
                ):

                    continue

                # ---------------- TAG ----------------

                tag = status.lower().replace(
                    " ",
                    "_"
                )

                # ---------------- INSERT ROW ----------------

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        medicine_id,
                        name,
                        category,
                        batch,
                        supplier,
                        quantity,
                        minimum_stock,
                        expiry,
                        status
                    ),
                    tags=(tag,)
                )

                visible_rows += 1

            # ---------------- UPDATE COUNTERS ----------------

            self.in_stock_label.configure(
                text=str(counts["In Stock"])
            )

            self.low_stock_label.configure(
                text=str(counts["Low Stock"])
            )

            self.out_stock_label.configure(
                text=str(counts["Out of Stock"])
            )

            self.expired_label.configure(
                text=str(counts["Expired"])
            )

            self.near_expiry_label.configure(
                text=str(counts["Near Expiry"])
            )

            # ---------------- EMPTY MESSAGE ----------------

            if visible_rows == 0:

                self.empty_label.configure(
                    text="No inventory records found."
                )

                self.empty_label.place(
                    relx=0.5,
                    rely=0.5,
                    anchor="center"
                )

            else:

                self.empty_label.place_forget()

        except Exception as error:

            print(
                "Inventory Error:",
                error
            )

            self.empty_label.configure(
                text="Unable to load inventory."
            )

            self.empty_label.place(
                relx=0.5,
                rely=0.5,
                anchor="center"
            )