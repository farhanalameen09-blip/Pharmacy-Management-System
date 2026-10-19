import customtkinter as ctk  # type: ignore
from tkinter import ttk, messagebox
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path
import os

from ui_kit import styled_treeview
from database import get_connection


class BillingPage(ctk.CTkFrame):

    def __init__(self, parent, back_to_dashboard, user_id=None):
        super().__init__(parent, fg_color="transparent")

        self.back_to_dashboard = back_to_dashboard
        self.user_id = user_id

        self.cart = []
        self.selected_medicine = None
        self.customer_map = {}
        self.invoice_number = ""

        self.build_ui()
        self.load_customers()
        self.load_medicines()
        self.generate_invoice_number()

    # =========================================================
    # UI
    # =========================================================

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            header,
            text="🛒 Sales / Billing",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="← Back to Dashboard",
            width=170,
            command=self.back_to_dashboard
        ).pack(side="right")

        # Customer section
        customer_frame = ctk.CTkFrame(self)
        customer_frame.pack(fill="x", padx=20, pady=6)

        ctk.CTkLabel(
            customer_frame,
            text="Customer Information",
            font=ctk.CTkFont(size=17, weight="bold")
        ).grid(row=0, column=0, columnspan=6, padx=12, pady=8, sticky="w")

        ctk.CTkLabel(
            customer_frame, text="Customer"
        ).grid(row=1, column=0, padx=8, pady=8)

        self.customer_combo = ctk.CTkComboBox(
            customer_frame,
            width=230,
            values=["Walk-in Customer"],
            command=self.customer_selected
        )
        self.customer_combo.set("Walk-in Customer")
        self.customer_combo.grid(row=1, column=1, padx=8, pady=8)

        ctk.CTkLabel(
            customer_frame, text="Phone"
        ).grid(row=1, column=2, padx=8, pady=8)

        self.customer_phone_entry = ctk.CTkEntry(
            customer_frame,
            width=150,
            placeholder_text="Phone number"
        )
        self.customer_phone_entry.grid(row=1, column=3, padx=8, pady=8)

        ctk.CTkLabel(
            customer_frame, text="Invoice No."
        ).grid(row=1, column=4, padx=8, pady=8)

        self.invoice_label = ctk.CTkLabel(
            customer_frame,
            text="",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.invoice_label.grid(row=1, column=5, padx=8, pady=8)

        # Medicine section
        medicine_frame = ctk.CTkFrame(self)
        medicine_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=6
        )

        ctk.CTkLabel(
            medicine_frame,
            text="Select Medicine",
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(anchor="w", padx=12, pady=(10, 4))

        search_frame = ctk.CTkFrame(
            medicine_frame,
            fg_color="transparent"
        )
        search_frame.pack(fill="x", padx=12, pady=5)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            placeholder_text="Search medicine or batch number..."
        )
        self.search_entry.pack(side="left", padx=(0, 8))
        self.search_entry.bind(
            "<KeyRelease>",
            lambda event: self.search_medicines()
        )

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=85,
            command=self.search_medicines
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            search_frame,
            text="Refresh",
            width=85,
            command=self.load_medicines
        ).pack(side="left", padx=3)

        # Medicine table
        table_frame = ctk.CTkFrame(
            medicine_frame,
            fg_color="transparent"
        )
        table_frame.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=5
        )

        columns = ("id", "name", "batch", "price", "stock")

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
            "id": 55,
            "name": 250,
            "batch": 130,
            "price": 120,
            "stock": 90
        }

        for column in columns:
            self.medicine_tree.heading(
                column, text=headings[column]
            )
            self.medicine_tree.column(
                column,
                width=widths[column],
                anchor="center"
            )

        self.medicine_tree.pack(
            side="left", fill="both", expand=True
        )

        medicine_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.medicine_tree.yview
        )
        medicine_scrollbar.pack(side="right", fill="y")

        self.medicine_tree.configure(
            yscrollcommand=medicine_scrollbar.set
        )

        self.medicine_tree.bind(
            "<<TreeviewSelect>>",
            self.select_medicine
        )

        # Quantity and add button
        add_frame = ctk.CTkFrame(
            medicine_frame,
            fg_color="transparent"
        )
        add_frame.pack(fill="x", padx=12, pady=(5, 10))

        ctk.CTkLabel(
            add_frame, text="Quantity:"
        ).pack(side="left", padx=(0, 8))

        self.quantity_entry = ctk.CTkEntry(
            add_frame,
            width=90,
            placeholder_text="1"
        )
        self.quantity_entry.pack(side="left")

        self.selected_label = ctk.CTkLabel(
            add_frame,
            text="No medicine selected"
        )
        self.selected_label.pack(side="left", padx=15)

        ctk.CTkButton(
            add_frame,
            text="＋ Add to Bill",
            width=140,
            command=self.add_to_bill
        ).pack(side="right")

        # Current bill
        bill_frame = ctk.CTkFrame(self)
        bill_frame.pack(fill="both", expand=True, padx=20, pady=6)

        ctk.CTkLabel(
            bill_frame,
            text="Current Bill",
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(anchor="w", padx=12, pady=8)

        bill_table_frame = ctk.CTkFrame(
            bill_frame,
            fg_color="transparent"
        )
        bill_table_frame.pack(
            fill="both", expand=True, padx=12
        )

        bill_columns = ("medicine", "quantity", "price", "total")

        self.bill_tree = styled_treeview(
            bill_table_frame,
            columns=bill_columns,
            show="headings"
        )

        bill_headings = {
            "medicine": "Medicine",
            "quantity": "Quantity",
            "price": "Unit Price",
            "total": "Total"
        }

        bill_widths = {
            "medicine": 280,
            "quantity": 100,
            "price": 120,
            "total": 120
        }

        for column in bill_columns:
            self.bill_tree.heading(
                column, text=bill_headings[column]
            )
            self.bill_tree.column(
                column,
                width=bill_widths[column],
                anchor="center"
            )

        self.bill_tree.pack(
            side="left", fill="both", expand=True
        )

        bill_scrollbar = ttk.Scrollbar(
            bill_table_frame,
            orient="vertical",
            command=self.bill_tree.yview
        )
        bill_scrollbar.pack(side="right", fill="y")

        self.bill_tree.configure(
            yscrollcommand=bill_scrollbar.set
        )

        controls = ctk.CTkFrame(
            bill_frame,
            fg_color="transparent"
        )
        controls.pack(fill="x", padx=12, pady=8)

        ctk.CTkButton(
            controls,
            text="Remove Selected",
            width=140,
            command=self.remove_selected_item
        ).pack(side="left")

        ctk.CTkButton(
            controls,
            text="Clear Bill",
            width=110,
            command=self.clear_bill
        ).pack(side="left", padx=8)

        # Totals and payment
        totals_frame = ctk.CTkFrame(self)
        totals_frame.pack(fill="x", padx=20, pady=(5, 15))

        self.subtotal_label = ctk.CTkLabel(
            totals_frame,
            text="Subtotal: ₹0.00",
            font=ctk.CTkFont(size=15)
        )
        self.subtotal_label.grid(
            row=0, column=0, padx=10, pady=8
        )

        ctk.CTkLabel(
            totals_frame, text="Discount (₹):"
        ).grid(row=0, column=1, padx=4)

        self.discount_entry = ctk.CTkEntry(
            totals_frame, width=85, placeholder_text="0"
        )
        self.discount_entry.grid(
            row=0, column=2, padx=4
        )
        self.discount_entry.bind(
            "<KeyRelease>", lambda event: self.update_totals()
        )

        ctk.CTkLabel(
            totals_frame, text="Tax (₹):"
        ).grid(row=0, column=3, padx=4)

        self.tax_entry = ctk.CTkEntry(
            totals_frame, width=85, placeholder_text="0"
        )
        self.tax_entry.grid(row=0, column=4, padx=4)
        self.tax_entry.bind(
            "<KeyRelease>", lambda event: self.update_totals()
        )

        self.total_label = ctk.CTkLabel(
            totals_frame,
            text="Grand Total: ₹0.00",
            font=ctk.CTkFont(size=19, weight="bold")
        )
        self.total_label.grid(
            row=0, column=5, padx=15
        )

        ctk.CTkLabel(
            totals_frame, text="Payment:"
        ).grid(row=1, column=0, padx=10, pady=8)

        self.payment_combo = ctk.CTkComboBox(
            totals_frame,
            values=["Cash", "Card", "UPI", "Other"],
            width=120
        )
        self.payment_combo.set("Cash")
        self.payment_combo.grid(
            row=1, column=1, padx=10, pady=8
        )

        ctk.CTkButton(
            totals_frame,
            text="✓ COMPLETE SALE",
            width=190,
            height=38,
            command=self.complete_sale
        ).grid(row=1, column=5, padx=15, pady=8)

    # =========================================================
    # DATABASE CONNECTION HELPER
    # =========================================================

    @contextmanager
    def database_transaction(self):
        """
        Uses the project's get_connection context manager.
        The connection is committed on success and rolled back
        if an exception occurs.
        """
        with get_connection() as connection:
            try:
                yield connection
            except Exception:
                connection.rollback()
                raise

    # =========================================================
    # CUSTOMERS
    # =========================================================

    def load_customers(self):
        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    SELECT customer_id, name, phone
                    FROM customers
                    ORDER BY name
                    """
                )
                customers = cursor.fetchall()

            self.customer_map = {"Walk-in Customer": None}
            values = ["Walk-in Customer"]

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

            self.customer_combo.configure(values=values)

        except Exception as error:
            print("Customer loading error:", error)

    def customer_selected(self, value):
        customer = self.customer_map.get(value)

        self.customer_phone_entry.delete(0, "end")

        if customer:
            self.customer_phone_entry.insert(
                0, customer.get("phone", "")
            )

    # =========================================================
    # MEDICINES
    # =========================================================

    def load_medicines(self):
        self.search_entry.delete(0, "end")
        self.selected_medicine = None
        self.selected_label.configure(text="No medicine selected")

        for row in self.medicine_tree.get_children():
            self.medicine_tree.delete(row)

        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    SELECT medicine_id, name, batch_no,
                           selling_price, quantity
                    FROM medicines
                    WHERE quantity > 0
                    ORDER BY name ASC
                    """
                )
                medicines = cursor.fetchall()

            for medicine in medicines:
                medicine_id = medicine[0]
                name = medicine[1] or ""
                batch = medicine[2] or ""
                price = float(medicine[3] or 0)
                stock = int(medicine[4] or 0)

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
            print("Medicine loading error:", error)
            messagebox.showerror(
                "Billing Error",
                f"Unable to load medicines.\n\n{error}"
            )

    def search_medicines(self):
        search_text = self.search_entry.get().strip().lower()

        for row in self.medicine_tree.get_children():
            values = self.medicine_tree.item(row)["values"]

            name = str(values[1]).lower()
            batch = str(values[2]).lower()

            if not search_text or search_text in name or search_text in batch:
                self.medicine_tree.reattach(row, "", "end")
            else:
                self.medicine_tree.detach(row)

    def select_medicine(self, event=None):
        selected = self.medicine_tree.selection()

        if not selected:
            return

        values = self.medicine_tree.item(selected[0])["values"]

        try:
            self.selected_medicine = {
                "id": int(values[0]),
                "name": str(values[1]),
                "batch": str(values[2]),
                "price": float(str(values[3]).replace("₹", "")),
                "stock": int(values[4])
            }
        except (ValueError, TypeError, IndexError):
            self.selected_medicine = None
            return

        self.selected_label.configure(
            text=f"Selected: {values[1]} | Stock: {values[4]}"
        )

        self.quantity_entry.delete(0, "end")
        self.quantity_entry.insert(0, "1")

    # =========================================================
    # CART
    # =========================================================

    def add_to_bill(self):
        if not self.selected_medicine:
            messagebox.showwarning(
                "Select Medicine",
                "Please select a medicine first."
            )
            return

        try:
            quantity_text = self.quantity_entry.get().strip()
            quantity = int(quantity_text)
        except (ValueError, TypeError):
            messagebox.showwarning(
                "Invalid Quantity",
                "Enter a whole-number quantity."
            )
            return

        if quantity <= 0:
            messagebox.showwarning(
                "Invalid Quantity",
                "Quantity must be greater than zero."
            )
            return

        medicine = self.selected_medicine
        medicine_id = medicine["id"]

        try:
            with get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    SELECT quantity, selling_price, name
                    FROM medicines
                    WHERE medicine_id = ?
                    """,
                    (medicine_id,)
                )
                current = cursor.fetchone()

            if not current:
                messagebox.showerror(
                    "Medicine Not Found",
                    "This medicine no longer exists. Refresh the list."
                )
                self.load_medicines()
                return

            stock = int(current[0] or 0)
            price = float(current[1] or 0)
            name = current[2] or medicine["name"]

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Unable to verify medicine stock.\n\n{error}"
            )
            return

        existing_item = next(
            (
                item for item in self.cart
                if item["medicine_id"] == medicine_id
            ),
            None
        )

        requested_quantity = quantity
        if existing_item:
            requested_quantity += existing_item["quantity"]

        if requested_quantity > stock:
            messagebox.showwarning(
                "Insufficient Stock",
                f"Available stock for {name}: {stock}\n"
                f"Quantity already in bill: "
                f"{existing_item['quantity'] if existing_item else 0}\n"
                f"Requested addition: {quantity}"
            )
            return

        if existing_item:
            existing_item["quantity"] = requested_quantity
            existing_item["price"] = price
            existing_item["total"] = round(requested_quantity * price, 2)
        else:
            self.cart.append({
                "medicine_id": medicine_id,
                "medicine_name": name,
                "quantity": quantity,
                "price": price,
                "total": round(quantity * price, 2)
            })

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
                    f"₹{item['total']:.2f}"
                )
            )

        self.update_totals()

    def remove_selected_item(self):
        selected = self.bill_tree.selection()

        if not selected:
            messagebox.showwarning(
                "Remove Item",
                "Select an item from the current bill."
            )
            return

        index = self.bill_tree.index(selected[0])

        if 0 <= index < len(self.cart):
            self.cart.pop(index)

        self.refresh_bill()

    # =========================================================
    # TOTALS AND VALIDATION
    # =========================================================

    def get_amount(self, entry, field_name):
        text = entry.get().strip()

        if not text:
            return 0.0

        try:
            amount = float(text)
        except ValueError:
            raise ValueError(f"{field_name} must be a valid number.")

        if amount < 0:
            raise ValueError(f"{field_name} cannot be negative.")

        if not amount < float("inf"):
            raise ValueError(f"{field_name} must be a finite number.")

        return round(amount, 2)

    def calculate_totals(self):
        subtotal = round(
            sum(item["quantity"] * item["price"] for item in self.cart),
            2
        )
        discount = self.get_amount(self.discount_entry, "Discount")
        tax = self.get_amount(self.tax_entry, "Tax")

        if discount > subtotal:
            raise ValueError("Discount cannot exceed the subtotal.")

        grand_total = round(subtotal - discount + tax, 2)

        return subtotal, discount, tax, grand_total

    def update_totals(self):
        subtotal = round(
            sum(item["quantity"] * item["price"] for item in self.cart),
            2
        )

        try:
            discount = self.get_amount(self.discount_entry, "Discount")
            tax = self.get_amount(self.tax_entry, "Tax")
            discount = min(discount, subtotal)
            grand_total = max(0.0, round(subtotal - discount + tax, 2))
        except ValueError:
            discount = 0.0
            tax = 0.0
            grand_total = subtotal

        self.subtotal_label.configure(
            text=f"Subtotal: ₹{subtotal:.2f}"
        )
        self.total_label.configure(
            text=f"Grand Total: ₹{grand_total:.2f}"
        )

    # =========================================================
    # INVOICE NUMBER
    # =========================================================

    def generate_invoice_number(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.invoice_number = f"INV-{timestamp}"
        self.invoice_label.configure(text=self.invoice_number)

    # =========================================================
    # COMPLETE SALE
    # =========================================================

    def complete_sale(self):
        if not self.cart:
            messagebox.showwarning(
                "Empty Bill",
                "Add at least one medicine before completing the sale."
            )
            return

        selected_customer = self.customer_combo.get().strip()

        if selected_customer not in self.customer_map:
            messagebox.showwarning(
                "Invalid Customer",
                "Select a customer from the list, or choose Walk-in Customer."
            )
            return

        customer_data = self.customer_map.get(selected_customer)
        customer_id = customer_data["id"] if customer_data else None
        customer_phone = self.customer_phone_entry.get().strip()

        try:
            subtotal, discount, tax, grand_total = self.calculate_totals()
        except ValueError as error:
            messagebox.showwarning("Invalid Amount", str(error))
            return

        payment_method = self.payment_combo.get().strip()

        if payment_method not in ("Cash", "Card", "UPI", "Other"):
            messagebox.showwarning(
                "Invalid Payment",
                "Select a valid payment method."
            )
            return

        sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sale_id = None

        try:
            # Everything in this block is one database transaction.
            with self.database_transaction() as connection:
                cursor = connection.cursor()

                # Recheck each medicine and update stock conditionally.
                for item in self.cart:
                    cursor.execute(
                        """
                        SELECT name, quantity, selling_price
                        FROM medicines
                        WHERE medicine_id = ?
                        """,
                        (item["medicine_id"],)
                    )
                    medicine = cursor.fetchone()

                    if not medicine:
                        raise ValueError(
                            f"Medicine not found: {item['medicine_name']}"
                        )

                    current_stock = int(medicine[1] or 0)

                    if item["quantity"] > current_stock:
                        raise ValueError(
                            f"Insufficient stock for {medicine[0]}.\n"
                            f"Available: {current_stock}\n"
                            f"Required: {item['quantity']}"
                        )

                cursor.execute(
                    """
                    INSERT INTO sales
                    (
                        invoice_no, customer_id, user_id, sale_date,
                        subtotal, discount, tax, total
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

                for item in self.cart:
                    cursor.execute(
                        """
                        UPDATE medicines
                        SET quantity = quantity - ?
                        WHERE medicine_id = ?
                          AND quantity >= ?
                        """,
                        (
                            item["quantity"],
                            item["medicine_id"],
                            item["quantity"]
                        )
                    )

                    if cursor.rowcount != 1:
                        raise ValueError(
                            f"Stock changed while selling "
                            f"{item['medicine_name']}. Please try again."
                        )

                    cursor.execute(
                        """
                        INSERT INTO sale_items
                        (
                            sale_id, medicine_id, quantity, price, total
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

            # The database transaction has now committed successfully.
            invoice_path = None
            invoice_error = None

            try:
                invoice_path = self.save_invoice(
                    selected_customer,
                    customer_phone,
                    subtotal,
                    discount,
                    tax,
                    grand_total,
                    payment_method
                )
            except OSError as error:
                # Do not claim that the sale failed after it was committed.
                invoice_error = str(error)

            success_message = (
                "Sale completed successfully!\n\n"
                f"Invoice: {self.invoice_number}\n"
                f"Total: ₹{grand_total:.2f}\n"
                f"Payment: {payment_method}"
            )

            if invoice_path:
                success_message += f"\n\nInvoice saved at:\n{invoice_path}"
            elif invoice_error:
                success_message += (
                    "\n\nWarning: The sale was saved, but the invoice "
                    f"file could not be created:\n{invoice_error}"
                )

            messagebox.showinfo("Sale Completed", success_message)

            self.clear_bill()
            self.load_medicines()
            self.generate_invoice_number()

        except Exception as error:
            print("Complete sale error:", error)
            messagebox.showerror(
                "Sale Error",
                f"Unable to complete sale.\n\n{error}"
            )

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
        project_folder = Path(__file__).resolve().parent.parent
        invoice_folder = project_folder / "invoices"
        invoice_folder.mkdir(parents=True, exist_ok=True)

        file_path = invoice_folder / f"{self.invoice_number}.txt"

        with open(file_path, "w", encoding="utf-8") as file:
            file.write("=" * 52 + "\n")
            file.write("             PHARMACY MANAGEMENT SYSTEM\n")
            file.write("=" * 52 + "\n\n")

            file.write(f"Invoice No : {self.invoice_number}\n")
            file.write(
                f"Date       : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
            )
            file.write(f"Customer   : {customer_name}\n")
            file.write(f"Phone      : {customer_phone or 'N/A'}\n")
            file.write("-" * 52 + "\n")
            file.write(
                f"{'Medicine':24}{'Qty':>5}{'Price':>10}{'Total':>11}\n"
            )
            file.write("-" * 52 + "\n")

            for item in self.cart:
                medicine_name = str(item["medicine_name"])[:24]
                file.write(
                    f"{medicine_name:24}"
                    f"{item['quantity']:>5}"
                    f"{item['price']:>10.2f}"
                    f"{item['total']:>11.2f}\n"
                )

            file.write("-" * 52 + "\n")
            file.write(f"Subtotal : ₹{subtotal:.2f}\n")
            file.write(f"Discount : ₹{discount:.2f}\n")
            file.write(f"Tax      : ₹{tax:.2f}\n")
            file.write(f"GRAND TOTAL: ₹{grand_total:.2f}\n")
            file.write(f"Payment  : {payment_method}\n")
            file.write("\nThank you for visiting!\n")

        return str(file_path)

    # =========================================================
    # CLEAR BILL
    # =========================================================

    def clear_bill(self):
        self.cart.clear()
        self.selected_medicine = None

        for row in self.bill_tree.get_children():
            self.bill_tree.delete(row)

        self.customer_combo.set("Walk-in Customer")
        self.customer_phone_entry.delete(0, "end")
        self.discount_entry.delete(0, "end")
        self.tax_entry.delete(0, "end")
        self.quantity_entry.delete(0, "end")

        self.selected_label.configure(text="No medicine selected")

        self.update_totals()