import os
from datetime import datetime

import customtkinter as ctk
from tkinter import ttk, messagebox

from database import get_connection


class BillingPage(ctk.CTkFrame):
    """Sales and billing page with safe database transactions."""

    def __init__(self, parent, back_to_dashboard, user_id=None):
        super().__init__(parent)

        self.back_to_dashboard = back_to_dashboard
        self.user_id = user_id
        self.cart = []
        self.selected_medicine = None
        self.customer_map = {}

        self.build_ui()
        self.load_customers()
        self.load_medicines()
        self.generate_invoice_number()

    # =====================================================
    # USER INTERFACE
    # =====================================================

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 8))

        ctk.CTkLabel(
            header,
            text="🛒 Sales / Billing",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="← Back to Dashboard",
            command=self.back_to_dashboard,
            width=170,
        ).pack(side="right")

        # Customer information
        customer = ctk.CTkFrame(self)
        customer.pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(
            customer,
            text="Customer Information",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(
            row=0, column=0, columnspan=6,
            sticky="w", padx=12, pady=8
        )

        ctk.CTkLabel(
            customer, text="Customer"
        ).grid(row=1, column=0, padx=8, pady=8)

        self.customer_combo = ctk.CTkComboBox(
            customer,
            width=230,
            values=["Walk-in Customer"],
            command=self.customer_selected,
        )
        self.customer_combo.set("Walk-in Customer")
        self.customer_combo.grid(
            row=1, column=1, padx=8, pady=8
        )

        ctk.CTkLabel(
            customer, text="Phone"
        ).grid(row=1, column=2, padx=8, pady=8)

        self.customer_phone_entry = ctk.CTkEntry(
            customer,
            width=160,
            placeholder_text="Phone number",
        )
        self.customer_phone_entry.grid(
            row=1, column=3, padx=8, pady=8
        )

        ctk.CTkLabel(
            customer, text="Invoice No."
        ).grid(row=1, column=4, padx=8, pady=8)

        self.invoice_label = ctk.CTkLabel(
            customer,
            text="",
            font=ctk.CTkFont(weight="bold"),
        )
        self.invoice_label.grid(
            row=1, column=5, padx=8, pady=8
        )

        # Medicine selection
        medicines = ctk.CTkFrame(self)
        medicines.pack(
            fill="both", expand=True,
            padx=20, pady=8
        )

        ctk.CTkLabel(
            medicines,
            text="Select Medicine",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(8, 4))

        search = ctk.CTkFrame(
            medicines, fg_color="transparent"
        )
        search.pack(fill="x", padx=12, pady=4)

        self.search_entry = ctk.CTkEntry(
            search,
            width=300,
            placeholder_text="Search medicine or batch number...",
        )
        self.search_entry.pack(side="left", padx=(0, 8))
        self.search_entry.bind(
            "<KeyRelease>",
            lambda event: self.search_medicines(),
        )

        ctk.CTkButton(
            search,
            text="Search",
            width=90,
            command=self.search_medicines,
        ).pack(side="left")

        ctk.CTkButton(
            search,
            text="Refresh",
            width=90,
            command=self.load_medicines,
        ).pack(side="left", padx=8)

        table = ctk.CTkFrame(
            medicines, fg_color="transparent"
        )
        table.pack(
            fill="both", expand=True,
            padx=12, pady=6
        )

        self.medicine_tree = ttk.Treeview(
            table,
            columns=("id", "name", "batch", "price", "stock"),
            show="headings",
            height=5,
        )

        columns = [
            ("id", "ID", 55),
            ("name", "Medicine", 240),
            ("batch", "Batch", 120),
            ("price", "Selling Price", 110),
            ("stock", "Stock", 80),
        ]

        for column, title, width in columns:
            self.medicine_tree.heading(column, text=title)
            self.medicine_tree.column(
                column, width=width, anchor="center"
            )

        self.medicine_tree.pack(
            side="left", fill="both", expand=True
        )

        scroll = ttk.Scrollbar(
            table,
            orient="vertical",
            command=self.medicine_tree.yview,
        )
        scroll.pack(side="right", fill="y")

        self.medicine_tree.configure(
            yscrollcommand=scroll.set
        )
        self.medicine_tree.bind(
            "<<TreeviewSelect>>", self.select_medicine
        )

        add = ctk.CTkFrame(
            medicines, fg_color="transparent"
        )
        add.pack(fill="x", padx=12, pady=6)

        ctk.CTkLabel(
            add, text="Quantity:"
        ).pack(side="left", padx=(0, 6))

        self.quantity_entry = ctk.CTkEntry(
            add, width=80, placeholder_text="1"
        )
        self.quantity_entry.pack(side="left")

        self.selected_label = ctk.CTkLabel(
            add, text="No medicine selected"
        )
        self.selected_label.pack(side="left", padx=15)

        ctk.CTkButton(
            add,
            text="＋ Add to Bill",
            command=self.add_to_bill,
            width=140,
        ).pack(side="right")

        # Current bill
        bill = ctk.CTkFrame(self)
        bill.pack(
            fill="both", expand=True,
            padx=20, pady=8
        )

        ctk.CTkLabel(
            bill,
            text="Current Bill",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(anchor="w", padx=12, pady=7)

        bill_table = ctk.CTkFrame(
            bill, fg_color="transparent"
        )
        bill_table.pack(
            fill="both", expand=True, padx=12
        )

        self.bill_tree = ttk.Treeview(
            bill_table,
            columns=("medicine", "quantity", "price", "total"),
            show="headings",
            height=4,
        )

        bill_columns = [
            ("medicine", "Medicine", 280),
            ("quantity", "Quantity", 90),
            ("price", "Unit Price", 110),
            ("total", "Total", 110),
        ]

        for column, title, width in bill_columns:
            self.bill_tree.heading(column, text=title)
            self.bill_tree.column(
                column, width=width, anchor="center"
            )

        self.bill_tree.pack(
            side="left", fill="both", expand=True
        )

        bill_scroll = ttk.Scrollbar(
            bill_table,
            orient="vertical",
            command=self.bill_tree.yview,
        )
        bill_scroll.pack(side="right", fill="y")

        self.bill_tree.configure(
            yscrollcommand=bill_scroll.set
        )

        controls = ctk.CTkFrame(
            bill, fg_color="transparent"
        )
        controls.pack(fill="x", padx=12, pady=6)

        ctk.CTkButton(
            controls,
            text="Remove Selected",
            command=self.remove_selected_item,
        ).pack(side="left")

        ctk.CTkButton(
            controls,
            text="Clear Bill",
            command=self.clear_bill,
        ).pack(side="left", padx=8)

        # Totals and payment
        totals = ctk.CTkFrame(self)
        totals.pack(
            fill="x", padx=20, pady=(4, 15)
        )

        self.subtotal_label = ctk.CTkLabel(
            totals, text="Subtotal: ₹0.00"
        )
        self.subtotal_label.grid(
            row=0, column=0, padx=10, pady=8
        )

        ctk.CTkLabel(
            totals, text="Discount (₹):"
        ).grid(row=0, column=1, padx=4)

        self.discount_entry = ctk.CTkEntry(
            totals, width=80, placeholder_text="0"
        )
        self.discount_entry.grid(
            row=0, column=2, padx=4
        )
        self.discount_entry.bind(
            "<KeyRelease>", lambda event: self.update_totals()
        )

        ctk.CTkLabel(
            totals, text="Tax (₹):"
        ).grid(row=0, column=3, padx=4)

        self.tax_entry = ctk.CTkEntry(
            totals, width=80, placeholder_text="0"
        )
        self.tax_entry.grid(
            row=0, column=4, padx=4
        )
        self.tax_entry.bind(
            "<KeyRelease>", lambda event: self.update_totals()
        )

        self.total_label = ctk.CTkLabel(
            totals,
            text="Grand Total: ₹0.00",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.total_label.grid(
            row=0, column=5, padx=12
        )

        ctk.CTkLabel(
            totals, text="Payment:"
        ).grid(row=1, column=0, padx=8, pady=6)

        self.payment_combo = ctk.CTkComboBox(
            totals,
            values=["Cash", "Card", "UPI", "Other"],
            width=120,
        )
        self.payment_combo.set("Cash")
        self.payment_combo.grid(
            row=1, column=1, padx=8, pady=6
        )

        ctk.CTkButton(
            totals,
            text="✓ COMPLETE SALE",
            command=self.complete_sale,
            width=190,
            height=38,
        ).grid(
            row=1, column=5, padx=12, pady=6
        )

    # =====================================================
    # CUSTOMERS
    # =====================================================

    def load_customers(self):
        try:
            with get_connection() as connection:
                rows = connection.execute(
                    """
                    SELECT customer_id, name, phone
                    FROM customers
                    ORDER BY name
                    """
                ).fetchall()

            self.customer_map = {
                "Walk-in Customer": None
            }
            values = ["Walk-in Customer"]

            for row in rows:
                customer_id = row["customer_id"]
                name = row["name"] or "Unnamed Customer"
                phone = row["phone"] or ""

                display = f"{customer_id} - {name}"

                self.customer_map[display] = {
                    "id": customer_id,
                    "phone": phone,
                }
                values.append(display)

            self.customer_combo.configure(values=values)

        except Exception as error:
            print("Customer loading error:", repr(error))
            messagebox.showerror(
                "Customer Error",
                f"Unable to load customers.\n\n{error}",
                parent=self.winfo_toplevel(),
            )

    def customer_selected(self, value):
        customer = self.customer_map.get(value)

        self.customer_phone_entry.delete(0, "end")

        if customer:
            self.customer_phone_entry.insert(
                0, customer["phone"]
            )

    # =====================================================
    # MEDICINES
    # =====================================================

    def load_medicines(self):
        for item in self.medicine_tree.get_children():
            self.medicine_tree.delete(item)

        self.selected_medicine = None
        self.selected_label.configure(
            text="No medicine selected"
        )

        try:
            # FIX: get_connection() must be entered using with.
            with get_connection() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        medicine_id,
                        name,
                        batch_no,
                        selling_price,
                        quantity
                    FROM medicines
                    WHERE COALESCE(quantity, 0) > 0
                    ORDER BY name
                    """
                ).fetchall()

            for row in rows:
                self.medicine_tree.insert(
                    "",
                    "end",
                    values=(
                        row["medicine_id"],
                        row["name"] or "",
                        row["batch_no"] or "",
                        f"₹{float(row['selling_price'] or 0):.2f}",
                        int(row["quantity"] or 0),
                    ),
                )

        except Exception as error:
            print("Medicine loading error:", repr(error))
            messagebox.showerror(
                "Billing Error",
                f"Unable to load medicines.\n\n{error}",
                parent=self.winfo_toplevel(),
            )

    def search_medicines(self):
        query = self.search_entry.get().strip().lower()

        for row_id in self.medicine_tree.get_children(""):
            values = self.medicine_tree.item(row_id)["values"]

            name = str(values[1]).lower()
            batch = str(values[2]).lower()

            if not query or query in name or query in batch:
                self.medicine_tree.reattach(
                    row_id, "", "end"
                )
            else:
                self.medicine_tree.detach(row_id)

    def select_medicine(self, event=None):
        selected = self.medicine_tree.selection()

        if not selected:
            return

        values = self.medicine_tree.item(
            selected[0], "values"
        )

        self.selected_medicine = {
            "id": int(values[0]),
            "name": values[1],
            "batch": values[2],
            "price": float(
                str(values[3]).replace("₹", "")
            ),
            "stock": int(values[4]),
        }

        self.selected_label.configure(
            text=(
                f"Selected: {values[1]} | "
                f"Stock: {values[4]}"
            )
        )

        self.quantity_entry.delete(0, "end")
        self.quantity_entry.insert(0, "1")

    # =====================================================
    # CART
    # =====================================================

    def add_to_bill(self):
        if not self.selected_medicine:
            messagebox.showwarning(
                "Select Medicine",
                "Please select a medicine first.",
                parent=self.winfo_toplevel(),
            )
            return

        try:
            quantity = int(
                self.quantity_entry.get().strip()
            )
        except ValueError:
            messagebox.showwarning(
                "Invalid Quantity",
                "Enter a whole-number quantity.",
                parent=self.winfo_toplevel(),
            )
            return

        if quantity <= 0:
            messagebox.showwarning(
                "Invalid Quantity",
                "Quantity must be greater than zero.",
                parent=self.winfo_toplevel(),
            )
            return

        medicine = self.selected_medicine

        already = sum(
            item["quantity"]
            for item in self.cart
            if item["medicine_id"] == medicine["id"]
        )

        if already + quantity > medicine["stock"]:
            messagebox.showwarning(
                "Insufficient Stock",
                f"Available: {medicine['stock']}\n"
                f"Already in bill: {already}",
                parent=self.winfo_toplevel(),
            )
            return

        existing = next(
            (
                item for item in self.cart
                if item["medicine_id"] == medicine["id"]
            ),
            None,
        )

        if existing:
            existing["quantity"] += quantity
            existing["total"] = (
                existing["quantity"] * existing["price"]
            )
        else:
            self.cart.append(
                {
                    "medicine_id": medicine["id"],
                    "medicine_name": medicine["name"],
                    "quantity": quantity,
                    "price": medicine["price"],
                    "total": quantity * medicine["price"],
                }
            )

        self.refresh_bill()

    def refresh_bill(self):
        for row in self.bill_tree.get_children():
            self.bill_tree.delete(row)

        for item in self.cart:
            self.bill_tree.insert(
                "",
                "end",
                values=(
                    item["medicine_name"],
                    item["quantity"],
                    f"₹{item['price']:.2f}",
                    f"₹{item['total']:.2f}",
                ),
            )

        self.update_totals()

    def remove_selected_item(self):
        selected = self.bill_tree.selection()

        if not selected:
            messagebox.showwarning(
                "Remove Item",
                "Select an item in the bill first.",
                parent=self.winfo_toplevel(),
            )
            return

        index = self.bill_tree.index(selected[0])

        if 0 <= index < len(self.cart):
            self.cart.pop(index)

        self.refresh_bill()

    def update_totals(self):
        subtotal = sum(
            float(item["total"]) for item in self.cart
        )

        try:
            discount = float(
                self.discount_entry.get().strip() or 0
            )
        except ValueError:
            discount = 0

        try:
            tax = float(
                self.tax_entry.get().strip() or 0
            )
        except ValueError:
            tax = 0

        total = max(
            0,
            subtotal - max(0, discount) + max(0, tax),
        )

        self.subtotal_label.configure(
            text=f"Subtotal: ₹{subtotal:.2f}"
        )
        self.total_label.configure(
            text=f"Grand Total: ₹{total:.2f}"
        )

    # =====================================================
    # INVOICE
    # =====================================================

    def generate_invoice_number(self):
        self.invoice_number = (
            "INV-" + datetime.now().strftime("%Y%m%d%H%M%S%f")
        )
        self.invoice_label.configure(
            text=self.invoice_number
        )

    def save_invoice(
        self,
        customer_name,
        customer_phone,
        subtotal,
        discount,
        tax,
        grand_total,
        payment_method,
    ):
        project_folder = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        invoice_folder = os.path.join(
            project_folder, "invoices"
        )
        os.makedirs(invoice_folder, exist_ok=True)

        file_path = os.path.join(
            invoice_folder,
            f"{self.invoice_number}.txt",
        )

        with open(
            file_path, "w", encoding="utf-8"
        ) as file:
            file.write(
                "=" * 45
                + "\n       PHARMACY MANAGEMENT SYSTEM\n"
                + "=" * 45
                + "\n\n"
            )

            file.write(
                f"Invoice No : {self.invoice_number}\n"
            )
            file.write(
                f"Date       : "
                f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
            )
            file.write(f"Customer   : {customer_name}\n")
            file.write(f"Phone      : {customer_phone}\n")
            file.write("-" * 45 + "\n")
            file.write(
                f"{'Medicine':20} {'Qty':>4} "
                f"{'Price':>8} {'Total':>9}\n"
            )
            file.write("-" * 45 + "\n")

            for item in self.cart:
                name = str(item["medicine_name"])[:20]

                file.write(
                    f"{name:20} "
                    f"{item['quantity']:4d} "
                    f"{item['price']:8.2f} "
                    f"{item['total']:9.2f}\n"
                )

            file.write("-" * 45 + "\n")
            file.write(f"Subtotal : ₹{subtotal:.2f}\n")
            file.write(f"Discount : ₹{discount:.2f}\n")
            file.write(f"Tax      : ₹{tax:.2f}\n")
            file.write(f"TOTAL    : ₹{grand_total:.2f}\n")
            file.write(f"Payment  : {payment_method}\n\n")
            file.write("Thank you for visiting!\n")

        return file_path

    # =====================================================
    # COMPLETE SALE
    # =====================================================

    def complete_sale(self):
        if not self.cart:
            messagebox.showwarning(
                "Empty Bill",
                "Please add at least one medicine.",
                parent=self.winfo_toplevel(),
            )
            return

        selected_customer = (
            self.customer_combo.get().strip()
        )
        customer_data = self.customer_map.get(
            selected_customer
        )

        # Do not silently assign an unknown customer.
        if (
            selected_customer != "Walk-in Customer"
            and customer_data is None
        ):
            messagebox.showwarning(
                "Invalid Customer",
                "Please select a valid customer or Walk-in Customer.",
                parent=self.winfo_toplevel(),
            )
            return

        customer_id = (
            customer_data["id"]
            if customer_data
            else None
        )
        customer_phone = (
            self.customer_phone_entry.get().strip()
        )

        try:
            discount = float(
                self.discount_entry.get().strip() or 0
            )
            tax = float(
                self.tax_entry.get().strip() or 0
            )
        except ValueError:
            messagebox.showwarning(
                "Invalid Amount",
                "Discount and tax must be numbers.",
                parent=self.winfo_toplevel(),
            )
            return

        if discount < 0 or tax < 0:
            messagebox.showwarning(
                "Invalid Amount",
                "Discount and tax cannot be negative.",
                parent=self.winfo_toplevel(),
            )
            return

        subtotal = sum(
            float(item["total"]) for item in self.cart
        )

        if discount > subtotal:
            messagebox.showwarning(
                "Invalid Discount",
                "Discount cannot exceed the subtotal.",
                parent=self.winfo_toplevel(),
            )
            return

        grand_total = subtotal - discount + tax
        payment_method = (
            self.payment_combo.get().strip() or "Cash"
        )

        # Save the current cart before the database transaction.
        invoice_items = [item.copy() for item in self.cart]
        invoice_number = self.invoice_number

        try:
            # FIX: enter the context manager before using connection.
            with get_connection() as connection:
                cursor = connection.cursor()

                # Start an explicit transaction.
                cursor.execute("BEGIN")

                # Check the current stock inside the transaction.
                for item in invoice_items:
                    cursor.execute(
                        """
                        SELECT name, quantity
                        FROM medicines
                        WHERE medicine_id = ?
                        """,
                        (item["medicine_id"],),
                    )

                    row = cursor.fetchone()

                    if row is None:
                        raise RuntimeError(
                            f"Medicine not found: "
                            f"{item['medicine_name']}"
                        )

                    available = int(row["quantity"] or 0)
                    required = int(item["quantity"])

                    if required <= 0 or required > available:
                        raise RuntimeError(
                            f"Insufficient stock for "
                            f"{item['medicine_name']}.\n"
                            f"Available: {available}; "
                            f"required: {required}"
                        )

                sale_date = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                cursor.execute(
                    """
                    INSERT INTO sales (
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
                        invoice_number,
                        customer_id,
                        self.user_id,
                        sale_date,
                        subtotal,
                        discount,
                        tax,
                        grand_total,
                    ),
                )

                sale_id = cursor.lastrowid

                # Record each item and reduce the stock.
                for item in invoice_items:
                    medicine_id = int(
                        item["medicine_id"]
                    )
                    quantity_sold = int(
                        item["quantity"]
                    )

                    cursor.execute(
                        """
                        INSERT INTO sale_items (
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
                            medicine_id,
                            quantity_sold,
                            item["price"],
                            item["total"],
                        ),
                    )

                    cursor.execute(
                        """
                        UPDATE medicines
                        SET quantity = quantity - ?
                        WHERE medicine_id = ?
                          AND quantity >= ?
                        """,
                        (
                            quantity_sold,
                            medicine_id,
                            quantity_sold,
                        ),
                    )

                    if cursor.rowcount != 1:
                        raise RuntimeError(
                            f"Stock update failed for "
                            f"{item['medicine_name']}."
                        )

                # Commit the complete sale.
                connection.commit()

            # Save invoice after the sale has committed.
            self.cart = invoice_items
            self.invoice_number = invoice_number

            try:
                invoice_path = self.save_invoice(
                    selected_customer,
                    customer_phone,
                    subtotal,
                    discount,
                    tax,
                    grand_total,
                    payment_method,
                )
            except Exception as invoice_error:
                messagebox.showwarning(
                    "Invoice File Warning",
                    "The sale was saved successfully, but the "
                    "invoice text file could not be created.\n\n"
                    f"{invoice_error}",
                    parent=self.winfo_toplevel(),
                )
                invoice_path = None

            if invoice_path:
                messagebox.showinfo(
                    "Sale Completed",
                    "Sale completed successfully!\n\n"
                    f"Invoice: {invoice_number}\n"
                    f"Total: ₹{grand_total:.2f}\n\n"
                    f"Invoice saved at:\n{invoice_path}",
                    parent=self.winfo_toplevel(),
                )
            else:
                messagebox.showinfo(
                    "Sale Completed",
                    "Sale completed successfully!\n\n"
                    f"Invoice: {invoice_number}\n"
                    f"Total: ₹{grand_total:.2f}",
                    parent=self.winfo_toplevel(),
                )

            self.clear_bill()
            self.load_medicines()
            self.generate_invoice_number()

        except Exception as error:
            print("Complete sale error:", repr(error))

            messagebox.showerror(
                "Sale Error",
                "Unable to complete the sale.\n\n"
                f"{error}",
                parent=self.winfo_toplevel(),
            )

    # =====================================================
    # CLEAR BILL
    # =====================================================

    def clear_bill(self):
        self.cart = []
        self.selected_medicine = None

        for row in self.bill_tree.get_children():
            self.bill_tree.delete(row)

        self.customer_combo.set("Walk-in Customer")
        self.customer_phone_entry.delete(0, "end")
        self.discount_entry.delete(0, "end")
        self.tax_entry.delete(0, "end")
        self.quantity_entry.delete(0, "end")

        self.selected_label.configure(
            text="No medicine selected"
        )

        self.update_totals()