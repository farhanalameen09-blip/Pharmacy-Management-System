import customtkinter as ctk # type: ignore
from ui_kit import styled_treeview
from tkinter import ttk, messagebox
from datetime import datetime
import os

from database import get_connection


class BillingPage(ctk.CTkFrame):

    def __init__(self, parent, back_to_dashboard, user_id=None):

        super().__init__(parent, fg_color="transparent")

        self.back_to_dashboard = back_to_dashboard
        self.user_id = user_id

        self.cart = []
        self.selected_medicine = None
        self.customer_map = {}

        self.build_ui()
        self.load_customers()
        self.load_medicines()
        self.generate_invoice_number()

    # =========================================================
    # MAIN UI
    # =========================================================

    def build_ui(self):

        # -----------------------------------------------------
        # HEADER
        # -----------------------------------------------------

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=25,
            pady=(20, 10)
        )

        ctk.CTkLabel(
            header,
            text="🛒 Sales / Billing",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="← Back to Dashboard",
            width=170,
            command=self.back_to_dashboard
        ).pack(side="right")

        # -----------------------------------------------------
        # CUSTOMER SECTION
        # -----------------------------------------------------

        customer_frame = ctk.CTkFrame(self)

        customer_frame.pack(
            fill="x",
            padx=25,
            pady=10
        )

        ctk.CTkLabel(
            customer_frame,
            text="Customer Information",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        ).grid(
            row=0,
            column=0,
            columnspan=6,
            padx=15,
            pady=12,
            sticky="w"
        )

        ctk.CTkLabel(
            customer_frame,
            text="Customer"
        ).grid(
            row=1,
            column=0,
            padx=10,
            pady=10
        )

        self.customer_combo = ctk.CTkComboBox(
            customer_frame,
            width=250,
            values=["Walk-in Customer"],
            command=self.customer_selected
        )

        self.customer_combo.set("Walk-in Customer")

        self.customer_combo.grid(
            row=1,
            column=1,
            padx=10,
            pady=10
        )

        ctk.CTkLabel(
            customer_frame,
            text="Phone"
        ).grid(
            row=1,
            column=2,
            padx=10,
            pady=10
        )

        self.customer_phone_entry = ctk.CTkEntry(
            customer_frame,
            width=180,
            placeholder_text="Phone number"
        )

        self.customer_phone_entry.grid(
            row=1,
            column=3,
            padx=10,
            pady=10
        )

        ctk.CTkLabel(
            customer_frame,
            text="Invoice No."
        ).grid(
            row=1,
            column=4,
            padx=10,
            pady=10
        )

        self.invoice_label = ctk.CTkLabel(
            customer_frame,
            text="",
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            )
        )

        self.invoice_label.grid(
            row=1,
            column=5,
            padx=10,
            pady=10
        )

        # -----------------------------------------------------
        # MEDICINE SECTION
        # -----------------------------------------------------

        medicine_frame = ctk.CTkFrame(self)

        medicine_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10
        )

        ctk.CTkLabel(
            medicine_frame,
            text="Select Medicine",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 5)
        )

        # -----------------------------------------------------
        # SEARCH
        # -----------------------------------------------------

        search_frame = ctk.CTkFrame(
            medicine_frame,
            fg_color="transparent"
        )

        search_frame.pack(
            fill="x",
            padx=15,
            pady=5
        )

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=350,
            placeholder_text="Search medicine or batch number..."
        )

        self.search_entry.pack(
            side="left",
            padx=(0, 10)
        )

        self.search_entry.bind(
            "<KeyRelease>",
            lambda event: self.search_medicines()
        )

        ctk.CTkButton(
            search_frame,
            text="🔍 Search",
            width=100,
            command=self.search_medicines
        ).pack(side="left")

        ctk.CTkButton(
            search_frame,
            text="🔄 Refresh",
            width=100,
            command=self.load_medicines
        ).pack(
            side="left",
            padx=10
        )

        # -----------------------------------------------------
        # MEDICINE TABLE
        # -----------------------------------------------------

        table_frame = ctk.CTkFrame(
            medicine_frame,
            fg_color="transparent"
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        columns = (
            "id",
            "name",
            "batch",
            "price",
            "stock"
        )

        self.medicine_tree = styled_treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": "ID",
            "name": "Medicine",
            "batch": "Batch",
            "price": "Selling Price",
            "stock": "Stock"
        }

        widths = {
            "id": 60,
            "name": 250,
            "batch": 140,
            "price": 130,
            "stock": 100
        }

        for column in columns:

            self.medicine_tree.heading(
                column,
                text=headings[column]
            )

            self.medicine_tree.column(
                column,
                width=widths[column],
                anchor="center"
            )

        self.medicine_tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.medicine_tree.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.medicine_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.medicine_tree.bind(
            "<<TreeviewSelect>>",
            self.select_medicine
        )

        # -----------------------------------------------------
        # QUANTITY
        # -----------------------------------------------------

        add_frame = ctk.CTkFrame(
            medicine_frame,
            fg_color="transparent"
        )

        add_frame.pack(
            fill="x",
            padx=15,
            pady=10
        )

        ctk.CTkLabel(
            add_frame,
            text="Quantity:"
        ).pack(
            side="left",
            padx=(0, 8)
        )

        self.quantity_entry = ctk.CTkEntry(
            add_frame,
            width=100,
            placeholder_text="1"
        )

        self.quantity_entry.pack(
            side="left"
        )

        self.selected_label = ctk.CTkLabel(
            add_frame,
            text="No medicine selected"
        )

        self.selected_label.pack(
            side="left",
            padx=20
        )

        ctk.CTkButton(
            add_frame,
            text="＋ Add to Bill",
            width=150,
            command=self.add_to_bill
        ).pack(
            side="right"
        )

        # -----------------------------------------------------
        # CURRENT BILL
        # -----------------------------------------------------

        bill_frame = ctk.CTkFrame(self)

        bill_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10
        )

        ctk.CTkLabel(
            bill_frame,
            text="Current Bill",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=15,
            pady=10
        )

        bill_table_frame = ctk.CTkFrame(
            bill_frame,
            fg_color="transparent"
        )

        bill_table_frame.pack(
            fill="both",
            expand=True,
            padx=15
        )

        bill_columns = (
            "medicine",
            "quantity",
            "price",
            "total"
        )

        self.bill_tree = styled_treeview(
            bill_table_frame,
            columns=bill_columns,
            show="headings"
        )

        self.bill_tree.heading(
            "medicine",
            text="Medicine"
        )

        self.bill_tree.heading(
            "quantity",
            text="Quantity"
        )

        self.bill_tree.heading(
            "price",
            text="Unit Price"
        )

        self.bill_tree.heading(
            "total",
            text="Total"
        )

        self.bill_tree.column(
            "medicine",
            width=300
        )

        self.bill_tree.column(
            "quantity",
            width=100,
            anchor="center"
        )

        self.bill_tree.column(
            "price",
            width=120,
            anchor="center"
        )

        self.bill_tree.column(
            "total",
            width=120,
            anchor="center"
        )

        self.bill_tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        bill_scrollbar = ttk.Scrollbar(
            bill_table_frame,
            orient="vertical",
            command=self.bill_tree.yview
        )

        bill_scrollbar.pack(
            side="right",
            fill="y"
        )

        self.bill_tree.configure(
            yscrollcommand=bill_scrollbar.set
        )

        # -----------------------------------------------------
        # BILL BUTTONS
        # -----------------------------------------------------

        control_frame = ctk.CTkFrame(
            bill_frame,
            fg_color="transparent"
        )

        control_frame.pack(
            fill="x",
            padx=15,
            pady=10
        )

        ctk.CTkButton(
            control_frame,
            text="Remove Selected",
            width=150,
            command=self.remove_selected_item
        ).pack(side="left")

        ctk.CTkButton(
            control_frame,
            text="Clear Bill",
            width=120,
            command=self.clear_bill
        ).pack(
            side="left",
            padx=10
        )

        # -----------------------------------------------------
        # TOTALS
        # -----------------------------------------------------

        totals_frame = ctk.CTkFrame(self)

        totals_frame.pack(
            fill="x",
            padx=25,
            pady=(5, 20)
        )

        self.subtotal_label = ctk.CTkLabel(
            totals_frame,
            text="Subtotal: ₹0.00",
            font=ctk.CTkFont(size=16)
        )

        self.subtotal_label.grid(
            row=0,
            column=0,
            padx=15,
            pady=8
        )

        ctk.CTkLabel(
            totals_frame,
            text="Discount:"
        ).grid(
            row=0,
            column=1,
            padx=5
        )

        self.discount_entry = ctk.CTkEntry(
            totals_frame,
            width=90,
            placeholder_text="0"
        )

        self.discount_entry.grid(
            row=0,
            column=2,
            padx=5
        )

        self.discount_entry.bind(
            "<KeyRelease>",
            lambda event: self.update_totals()
        )

        ctk.CTkLabel(
            totals_frame,
            text="Tax:"
        ).grid(
            row=0,
            column=3,
            padx=5
        )

        self.tax_entry = ctk.CTkEntry(
            totals_frame,
            width=90,
            placeholder_text="0"
        )

        self.tax_entry.grid(
            row=0,
            column=4,
            padx=5
        )

        self.tax_entry.bind(
            "<KeyRelease>",
            lambda event: self.update_totals()
        )

        self.total_label = ctk.CTkLabel(
            totals_frame,
            text="Grand Total: ₹0.00",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        )

        self.total_label.grid(
            row=0,
            column=5,
            padx=25
        )

        ctk.CTkLabel(
            totals_frame,
            text="Payment:"
        ).grid(
            row=1,
            column=0,
            padx=10,
            pady=8
        )

        self.payment_combo = ctk.CTkComboBox(
            totals_frame,
            values=[
                "Cash",
                "Card",
                "UPI",
                "Other"
            ],
            width=130
        )

        self.payment_combo.set("Cash")

        self.payment_combo.grid(
            row=1,
            column=1,
            padx=10,
            pady=8
        )

        ctk.CTkButton(
            totals_frame,
            text="✓ COMPLETE SALE",
            width=200,
            height=40,
            command=self.complete_sale
        ).grid(
            row=1,
            column=5,
            padx=15,
            pady=8
        )

    # =========================================================
    # CUSTOMERS
    # =========================================================

    def load_customers(self):

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    customer_id,
                    name,
                    phone
                FROM customers
                ORDER BY name
                """
            )

            customers = cursor.fetchall()

            connection.close()

            self.customer_map = {
                "Walk-in Customer": None
            }

            values = [
                "Walk-in Customer"
            ]

            for customer in customers:

                customer_id = customer[0]
                name = customer[1] or "Unnamed Customer"
                phone = customer[2] or ""

                display = f"{customer_id} - {name}"

                self.customer_map[display] = {
                    "id": customer_id,
                    "phone": phone
                }

                values.append(display)

            self.customer_combo.configure(
                values=values
            )

        except Exception as error:

            print(
                "Customer loading error:",
                error
            )

    # =========================================================
    # CUSTOMER SELECTED
    # =========================================================

    def customer_selected(self, value):

        customer = self.customer_map.get(value)

        self.customer_phone_entry.delete(
            0,
            "end"
        )

        if customer:

            self.customer_phone_entry.insert(
                0,
                customer["phone"]
            )

    # =========================================================
    # LOAD MEDICINES
    # =========================================================

    def load_medicines(self):

        for item in self.medicine_tree.get_children():

            self.medicine_tree.delete(item)

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    medicine_id,
                    name,
                    batch_no,
                    selling_price,
                    quantity
                FROM medicines
                WHERE quantity > 0
                ORDER BY name ASC
                """
            )

            medicines = cursor.fetchall()

            connection.close()

            for medicine in medicines:

                medicine_id = medicine[0]
                name = medicine[1] or ""
                batch = medicine[2] or ""
                price = float(
                    medicine[3] or 0
                )
                stock = int(
                    medicine[4] or 0
                )

                self.medicine_tree.insert(
                    "",
                    "end",
                    values=(
                        medicine_id,
                        name,
                        batch,
                        f"₹{price:.2f}",
                        stock
                    )
                )

        except Exception as error:

            print(
                "Medicine loading error:",
                error
            )

            messagebox.showerror(
                "Sales / Billing Error",
                f"Unable to load medicines.\n\n{error}"
            )

    # =========================================================
    # SEARCH MEDICINES
    # =========================================================

    def search_medicines(self):

        search_text = (
            self.search_entry.get()
            .strip()
            .lower()
        )

        for item in self.medicine_tree.get_children():

            values = self.medicine_tree.item(
                item
            )["values"]

            name = str(
                values[1]
            ).lower()

            batch = str(
                values[2]
            ).lower()

            if (
                not search_text
                or search_text in name
                or search_text in batch
            ):

                self.medicine_tree.reattach(
                    item,
                    "",
                    "end"
                )

            else:

                self.medicine_tree.detach(
                    item
                )

    # =========================================================
    # STOCK DISPLAY HELPERS
    # =========================================================

    def get_cart_quantity(self, medicine_id):
        return sum(
            int(item["quantity"])
            for item in self.cart
            if int(item["medicine_id"]) == int(medicine_id)
        )

    def update_stock_display(self, medicine_id=None):
        """Show database stock minus quantities currently in this bill."""
        for row in self.medicine_tree.get_children():
            values = self.medicine_tree.item(row).get("values", [])
            if not values:
                continue
            row_medicine_id = int(values[0])
            if medicine_id is not None and row_medicine_id != int(medicine_id):
                continue

            connection = get_connection()
            try:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT quantity FROM medicines WHERE medicine_id = ?",
                    (row_medicine_id,)
                )
                result = cursor.fetchone()
            finally:
                connection.close()

            if result:
                actual_stock = int(result[0] or 0)
                available = max(0, actual_stock - self.get_cart_quantity(row_medicine_id))
                self.medicine_tree.set(row, "stock", available)

        if self.selected_medicine:
            mid = int(self.selected_medicine["id"])
            if medicine_id is None or mid == int(medicine_id):
                connection = get_connection()
                try:
                    cursor = connection.cursor()
                    cursor.execute(
                        "SELECT quantity FROM medicines WHERE medicine_id = ?",
                        (mid,)
                    )
                    result = cursor.fetchone()
                finally:
                    connection.close()
                if result:
                    available = max(0, int(result[0] or 0) - self.get_cart_quantity(mid))
                    self.selected_label.configure(
                        text=f"Selected: {self.selected_medicine['name']} | Available: {available}"
                    )

    # =========================================================
    # SELECT MEDICINE
    # =========================================================

    def select_medicine(self, event=None):
        selected = self.medicine_tree.selection()
        if not selected:
            return

        values = self.medicine_tree.item(selected[0])["values"]
        medicine_id = int(values[0])

        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT medicine_id, name, batch_no, selling_price, quantity "
                "FROM medicines WHERE medicine_id = ?",
                (medicine_id,)
            )
            medicine = cursor.fetchone()
        finally:
            connection.close()

        if not medicine:
            messagebox.showerror("Medicine Error", "Medicine not found.")
            return

        actual_stock = int(medicine[4] or 0)
        available_stock = max(0, actual_stock - self.get_cart_quantity(medicine_id))
        self.selected_medicine = {
            "id": int(medicine[0]),
            "name": medicine[1] or "",
            "batch": medicine[2] or "",
            "price": float(medicine[3] or 0),
            "stock": actual_stock
        }

        self.selected_label.configure(
            text=f"Selected: {self.selected_medicine['name']} | Available: {available_stock}"
        )
        self.quantity_entry.delete(0, "end")
        self.quantity_entry.insert(0, "1")
        self.update_stock_display(medicine_id)

    # =========================================================
    # ADD TO BILL - VALIDATE STOCK AND UPDATE DISPLAY
    # =========================================================

    def add_to_bill(self):
        if not self.selected_medicine:
            messagebox.showwarning("Select Medicine", "Please select a medicine first.")
            return

        try:
            quantity = int(self.quantity_entry.get().strip())
        except (ValueError, AttributeError):
            messagebox.showwarning("Invalid Quantity", "Please enter a valid whole number.")
            return

        if quantity <= 0:
            messagebox.showwarning("Invalid Quantity", "Quantity must be greater than zero.")
            return

        medicine_id = int(self.selected_medicine["id"])
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT name, selling_price, quantity FROM medicines WHERE medicine_id = ?",
                (medicine_id,)
            )
            result = cursor.fetchone()
        finally:
            connection.close()

        if not result:
            messagebox.showerror("Medicine Error", "Medicine not found in database.")
            return

        actual_stock = int(result[2] or 0)
        already_added = self.get_cart_quantity(medicine_id)
        available_stock = actual_stock - already_added

        if quantity > available_stock:
            messagebox.showwarning(
                "Insufficient Stock",
                f"Medicine: {result[0]}\n\nAvailable stock: {available_stock}\n"
                f"Requested quantity: {quantity}\n\nPlease enter a lower quantity."
            )
            # Keep the table and label showing the correct available amount.
            self.update_stock_display(medicine_id)
            return

        unit_price = float(result[1] or 0)
        existing_item = next(
            (item for item in self.cart if int(item["medicine_id"]) == medicine_id),
            None
        )

        if existing_item:
            existing_item["quantity"] += quantity
            existing_item["total"] = existing_item["quantity"] * existing_item["price"]
        else:
            self.cart.append({
                "medicine_id": medicine_id,
                "medicine_name": result[0] or self.selected_medicine["name"],
                "quantity": quantity,
                "price": unit_price,
                "total": quantity * unit_price
            })

        self.selected_medicine["stock"] = actual_stock
        self.refresh_bill()
        self.update_stock_display(medicine_id)

    # =========================================================
    # REFRESH BILL
    # =========================================================

    def refresh_bill(self):

        for item in self.bill_tree.get_children():

            self.bill_tree.delete(item)

        for item in self.cart:

            self.bill_tree.insert(
                "",
                "end",
                values=(
                    item["medicine_name"],
                    item["quantity"],
                    f"₹{item['price']:.2f}",
                    f"₹{item['total']:.2f}"
                )
            )

        self.update_totals()

    # =========================================================
    # REMOVE ITEM
    # =========================================================

    def remove_selected_item(self):

        selected = self.bill_tree.selection()

        if not selected:

            messagebox.showwarning(
                "Remove Item",
                "Please select an item from the bill."
            )

            return

        index = self.bill_tree.index(
            selected[0]
        )

        if 0 <= index < len(self.cart):
            self.cart.pop(index)

        self.refresh_bill()
        self.load_medicines()
        self.selected_medicine = None
        self.selected_label.configure(text="No medicine selected")

    # =========================================================
    # TOTALS
    # =========================================================

    def update_totals(self):

        subtotal = sum(
            item["total"]
            for item in self.cart
        )

        try:

            discount = float(
                self.discount_entry.get() or 0
            )

        except ValueError:

            discount = 0

        try:

            tax = float(
                self.tax_entry.get() or 0
            )

        except ValueError:

            tax = 0

        if discount < 0:
            discount = 0

        if tax < 0:
            tax = 0

        total = (
            subtotal -
            discount +
            tax
        )

        if total < 0:
            total = 0

        self.subtotal_label.configure(
            text=f"Subtotal: ₹{subtotal:.2f}"
        )

        self.total_label.configure(
            text=f"Grand Total: ₹{total:.2f}"
        )

    # =========================================================
    # GENERATE INVOICE
    # =========================================================

    def generate_invoice_number(self):

        timestamp = datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )

        self.invoice_number = (
            f"INV-{timestamp}"
        )

        self.invoice_label.configure(
            text=self.invoice_number
        )

    # =========================================================
    # COMPLETE SALE
    # =========================================================

    def complete_sale(self):

        if not self.cart:

            messagebox.showwarning(
                "Empty Bill",
                "Please add at least one medicine."
            )

            return

        # -----------------------------------------------------
        # CUSTOMER
        # -----------------------------------------------------

        selected_customer = (
            self.customer_combo.get()
            .strip()
        )

        customer_data = self.customer_map.get(
            selected_customer
        )

        customer_id = None

        if customer_data:

            customer_id = customer_data["id"]

        customer_phone = (
            self.customer_phone_entry.get()
            .strip()
        )

        # -----------------------------------------------------
        # DISCOUNT
        # -----------------------------------------------------

        try:

            discount = float(
                self.discount_entry.get() or 0
            )

        except ValueError:

            messagebox.showwarning(
                "Invalid Discount",
                "Please enter a valid discount."
            )

            return

        # -----------------------------------------------------
        # TAX
        # -----------------------------------------------------

        try:

            tax = float(
                self.tax_entry.get() or 0
            )

        except ValueError:

            messagebox.showwarning(
                "Invalid Tax",
                "Please enter a valid tax amount."
            )

            return

        if discount < 0 or tax < 0:

            messagebox.showwarning(
                "Invalid Amount",
                "Discount and tax cannot be negative."
            )

            return

        # -----------------------------------------------------
        # TOTAL
        # -----------------------------------------------------

        subtotal = sum(
            item["total"]
            for item in self.cart
        )

        grand_total = (
            subtotal -
            discount +
            tax
        )

        if grand_total < 0:
            grand_total = 0

        payment_method = (
            self.payment_combo.get()
            or "Cash"
        )

        connection = None

        try:

            connection = get_connection()
            cursor = connection.cursor()

            # -------------------------------------------------
            # CHECK STOCK AGAIN
            # -------------------------------------------------

            for item in self.cart:

                cursor.execute(
                    """
                    SELECT
                        quantity,
                        name
                    FROM medicines
                    WHERE medicine_id = ?
                    """,
                    (
                        item["medicine_id"],
                    )
                )

                result = cursor.fetchone()

                if not result:

                    raise Exception(
                        f"Medicine not found:\n"
                        f"{item['medicine_name']}"
                    )

                current_stock = int(
                    result[0] or 0
                )

                if item["quantity"] > current_stock:

                    raise Exception(
                        f"Not enough stock for "
                        f"{item['medicine_name']}.\n\n"
                        f"Available: {current_stock}\n"
                        f"Required: {item['quantity']}"
                    )

            # -------------------------------------------------
            # SALE DATE
            # -------------------------------------------------

            sale_date = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # -------------------------------------------------
            # SAVE SALE
            # -------------------------------------------------

            cursor.execute(
                """
                INSERT INTO sales
                (
                    invoice_no,
                    customer_id,
                    user_id,
                    sale_date,
                    subtotal,
                    discount,
                    tax,
                    total
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.invoice_number,
                    customer_id,
                    self.user_id,
                    sale_date,
                    subtotal,
                    discount,
                    tax,
                    grand_total
                )
            )

            sale_id = cursor.lastrowid

            # -------------------------------------------------
            # SAVE ITEMS + UPDATE STOCK
            # -------------------------------------------------

            for item in self.cart:

                cursor.execute(
                    """
                    INSERT INTO sale_items
                    (
                        sale_id,
                        medicine_id,
                        quantity,
                        price,
                        total
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        sale_id,
                        item["medicine_id"],
                        item["quantity"],
                        item["price"],
                        item["total"]
                    )
                )

                cursor.execute(
                    """
                    UPDATE medicines
                    SET quantity = quantity - ?
                    WHERE medicine_id = ?
                    """,
                    (
                        item["quantity"],
                        item["medicine_id"]
                    )
                )

            connection.commit()

            # -------------------------------------------------
            # SAVE INVOICE FILE
            # -------------------------------------------------

            invoice_path = self.save_invoice(
                selected_customer,
                customer_phone,
                subtotal,
                discount,
                tax,
                grand_total,
                payment_method
            )

            messagebox.showinfo(
                "Sale Completed",
                f"Sale completed successfully!\n\n"
                f"Invoice: {self.invoice_number}\n"
                f"Total: ₹{grand_total:.2f}\n\n"
                f"Invoice saved at:\n{invoice_path}"
            )

            self.clear_bill()

            self.load_medicines()

            self.generate_invoice_number()

        except Exception as error:

            if connection:

                connection.rollback()

            print(
                "Complete sale error:",
                error
            )

            messagebox.showerror(
                "Sale Error",
                f"Unable to complete sale.\n\n{error}"
            )

        finally:

            if connection:
                connection.close()

    # =========================================================
    # SAVE INVOICE
    # =========================================================

    def save_invoice(
        self,
        customer_name,
        customer_phone,
        subtotal,
        discount,
        tax,
        grand_total,
        payment_method
    ):

        project_folder = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        invoice_folder = os.path.join(
            project_folder,
            "invoices"
        )

        os.makedirs(
            invoice_folder,
            exist_ok=True
        )

        file_path = os.path.join(
            invoice_folder,
            f"{self.invoice_number}.txt"
        )

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "========================================\n"
            )

            file.write(
                "       PHARMACY MANAGEMENT SYSTEM\n"
            )

            file.write(
                "========================================\n\n"
            )

            file.write(
                f"Invoice No : {self.invoice_number}\n"
            )

            file.write(
                "Date       : "
                f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
            )

            file.write(
                f"Customer   : {customer_name}\n"
            )

            file.write(
                f"Phone      : {customer_phone}\n"
            )

            file.write(
                "----------------------------------------\n"
            )

            file.write(
                "Medicine           Qty   Price   Total\n"
            )

            file.write(
                "----------------------------------------\n"
            )

            for item in self.cart:

                medicine_name = str(
                    item["medicine_name"]
                )[:18]

                file.write(
                    f"{medicine_name:18} "
                    f"{item['quantity']:3} "
                    f"{item['price']:7.2f} "
                    f"{item['total']:8.2f}\n"
                )

            file.write(
                "----------------------------------------\n"
            )

            file.write(
                f"Subtotal : ₹{subtotal:.2f}\n"
            )

            file.write(
                f"Discount : ₹{discount:.2f}\n"
            )

            file.write(
                f"Tax      : ₹{tax:.2f}\n"
            )

            file.write(
                f"TOTAL    : ₹{grand_total:.2f}\n"
            )

            file.write(
                f"Payment  : {payment_method}\n"
            )

            file.write(
                "\nThank you for visiting!\n"
            )

        return file_path

    # =========================================================
    # CLEAR BILL
    # =========================================================

    def clear_bill(self):

        self.cart = []

        self.selected_medicine = None

        # Clear bill table

        for item in self.bill_tree.get_children():

            self.bill_tree.delete(item)

        # Customer

        self.customer_combo.set(
            "Walk-in Customer"
        )

        self.customer_phone_entry.delete(
            0,
            "end"
        )

        # Discount / tax

        self.discount_entry.delete(
            0,
            "end"
        )

        self.tax_entry.delete(
            0,
            "end"
        )

        # Quantity

        self.quantity_entry.delete(
            0,
            "end"
        )

        self.selected_label.configure(
            text="No medicine selected"
        )

        self.load_medicines()  # Restore actual database stock in the table.
        self.update_totals()