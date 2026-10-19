import customtkinter as ctk  # type: ignore
from tkinter import ttk, messagebox
from datetime import datetime

from ui_kit import styled_treeview
from database import get_connection


class MedicinePage(ctk.CTkFrame):

    def __init__(self, parent, back_to_dashboard):
        super().__init__(parent, fg_color="transparent")

        self.back_to_dashboard = back_to_dashboard
        self.selected_medicine_id = None
        self.supplier_map = {"No Supplier": None}

        # Form variables
        self.name_var = ctk.StringVar()
        self.category_var = ctk.StringVar()
        self.manufacturer_var = ctk.StringVar()
        self.batch_var = ctk.StringVar()
        self.purchase_var = ctk.StringVar()
        self.selling_var = ctk.StringVar()
        self.quantity_var = ctk.StringVar()
        self.min_stock_var = ctk.StringVar(value="10")
        self.expiry_var = ctk.StringVar()
        self.description_var = ctk.StringVar()
        self.supplier_var = ctk.StringVar(value="No Supplier")
        self.search_var = ctk.StringVar()

        self.build_ui()
        self.load_suppliers()
        self.load_medicines()

    # =========================================================
    # USER INTERFACE
    # =========================================================

    def build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # ---------------- HEADER ----------------

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(
            row=0, column=0, sticky="ew",
            padx=20, pady=(15, 5)
        )
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Medicine Management",
            font=ctk.CTkFont(size=26, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header,
            text="← Back to Dashboard",
            command=self.back_to_dashboard,
            width=180
        ).grid(row=0, column=1, sticky="e")

        # ---------------- MEDICINE FORM ----------------

        form = ctk.CTkFrame(self, corner_radius=12)
        form.grid(
            row=1, column=0, sticky="ew",
            padx=20, pady=10
        )

        for col in range(4):
            form.grid_columnconfigure(
                col, weight=1, uniform="medicine_form"
            )

        ctk.CTkLabel(
            form,
            text="Medicine Details",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(
            row=0, column=0, columnspan=4,
            sticky="w", padx=15, pady=(12, 10)
        )

        # Medicine Name and Category
        self.create_entry(
            form, "Medicine Name *",
            self.name_var, 1, 0
        )

        self.create_entry(
            form, "Category",
            self.category_var, 1, 2
        )

        # Manufacturer and Batch Number
        self.create_entry(
            form, "Manufacturer",
            self.manufacturer_var, 3, 0
        )

        self.create_entry(
            form, "Batch Number *",
            self.batch_var, 3, 2
        )

        # Purchase and Selling Price
        self.create_entry(
            form, "Purchase Price",
            self.purchase_var, 5, 0
        )

        self.create_entry(
            form, "Selling Price",
            self.selling_var, 5, 2
        )

        # Quantity and Minimum Stock
        self.create_entry(
            form, "Quantity",
            self.quantity_var, 7, 0
        )

        self.create_entry(
            form, "Minimum Stock",
            self.min_stock_var, 7, 2
        )

        # Expiry Date
        self.create_entry(
            form,
            "Expiry Date (YYYY-MM-DD) *",
            self.expiry_var,
            9,
            0
        )

        # Supplier
        ctk.CTkLabel(
            form,
            text="Supplier"
        ).grid(
            row=9, column=2,
            sticky="w", padx=12, pady=(5, 0)
        )

        self.supplier_combo = ctk.CTkComboBox(
            form,
            variable=self.supplier_var,
            values=["No Supplier"],
            state="readonly"
        )

        self.supplier_combo.grid(
            row=10, column=2, columnspan=2,
            sticky="ew", padx=12, pady=(0, 8)
        )

        # ---------------- DESCRIPTION ----------------
        # Separate rows prevent overlap with price fields.

        ctk.CTkLabel(
            form,
            text="Description"
        ).grid(
            row=11, column=0, columnspan=4,
            sticky="w", padx=12, pady=(8, 3)
        )

        ctk.CTkEntry(
            form,
            textvariable=self.description_var,
            placeholder_text="Enter medicine description (optional)"
        ).grid(
            row=12, column=0, columnspan=4,
            sticky="ew", padx=12, pady=(0, 10)
        )

        # ---------------- ACTION BUTTONS ----------------

        buttons = ctk.CTkFrame(
            form, fg_color="transparent"
        )

        buttons.grid(
            row=13, column=0, columnspan=4,
            sticky="e", padx=12, pady=(0, 12)
        )

        ctk.CTkButton(
            buttons,
            text="Add Medicine",
            command=self.add_medicine,
            width=130
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            buttons,
            text="Update",
            command=self.update_medicine,
            width=95
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            buttons,
            text="Delete",
            command=self.delete_medicine,
            width=95,
            fg_color="#C0392B",
            hover_color="#922B21"
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            buttons,
            text="Clear",
            command=self.clear_form,
            width=80
        ).pack(side="left", padx=4)

        # ---------------- SEARCH SECTION ----------------

        search_frame = ctk.CTkFrame(
            self, fg_color="transparent"
        )

        search_frame.grid(
            row=2, column=0, sticky="ew",
            padx=20, pady=(5, 5)
        )

        search_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            search_frame,
            text="Medicine Inventory",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(
            row=0, column=0,
            sticky="w", pady=(0, 8)
        )

        search_controls = ctk.CTkFrame(
            search_frame, fg_color="transparent"
        )

        search_controls.grid(
            row=1, column=0, sticky="ew"
        )

        self.search_entry = ctk.CTkEntry(
            search_controls,
            textvariable=self.search_var,
            placeholder_text=(
                "Search by name, category, manufacturer or batch..."
            )
        )

        self.search_entry.pack(
            side="left", fill="x", expand=True,
            padx=(0, 8)
        )

        self.search_entry.bind(
            "<Return>",
            lambda event: self.search_medicines()
        )

        ctk.CTkButton(
            search_controls,
            text="Search",
            command=self.search_medicines,
            width=100
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            search_controls,
            text="Refresh",
            command=self.refresh_data,
            width=100
        ).pack(side="left", padx=3)

        # ---------------- MEDICINE TABLE ----------------

        table_frame = ctk.CTkFrame(
            self, corner_radius=10
        )

        table_frame.grid(
            row=3, column=0, sticky="nsew",
            padx=20, pady=(5, 15)
        )

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = (
            "id",
            "name",
            "category",
            "manufacturer",
            "batch",
            "purchase",
            "selling",
            "quantity",
            "min_stock",
            "expiry",
            "supplier"
        )

        self.tree = styled_treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12
        )

        headings = {
            "id": "ID",
            "name": "Medicine Name",
            "category": "Category",
            "manufacturer": "Manufacturer",
            "batch": "Batch No.",
            "purchase": "Purchase Price",
            "selling": "Selling Price",
            "quantity": "Quantity",
            "min_stock": "Min. Stock",
            "expiry": "Expiry Date",
            "supplier": "Supplier"
        }

        widths = {
            "id": 55,
            "name": 160,
            "category": 110,
            "manufacturer": 130,
            "batch": 100,
            "purchase": 110,
            "selling": 110,
            "quantity": 85,
            "min_stock": 85,
            "expiry": 110,
            "supplier": 140
        }

        for column in columns:
            self.tree.heading(
                column,
                text=headings[column]
            )

            self.tree.column(
                column,
                width=widths[column],
                minwidth=50,
                anchor="center"
            )

        self.tree.grid(
            row=0, column=0, sticky="nsew",
            padx=(8, 0), pady=8
        )

        scrollbar_y = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        scrollbar_y.grid(
            row=0, column=1,
            sticky="ns", pady=8
        )

        scrollbar_x = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview
        )

        scrollbar_x.grid(
            row=1, column=0,
            sticky="ew", padx=(8, 0), pady=(0, 8)
        )

        self.tree.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )

        self.tree.bind(
            "<Double-1>",
            self.select_medicine
        )

    # =========================================================
    # CREATE FORM ENTRY
    # =========================================================

    def create_entry(
        self, parent, label, variable, row, column
    ):
        ctk.CTkLabel(
            parent,
            text=label
        ).grid(
            row=row,
            column=column,
            sticky="w",
            padx=12,
            pady=(5, 0)
        )

        entry = ctk.CTkEntry(
            parent,
            textvariable=variable
        )

        entry.grid(
            row=row + 1,
            column=column,
            sticky="ew",
            padx=12,
            pady=(0, 8)
        )

        return entry

    # =========================================================
    # SUPPLIER MANAGEMENT
    # =========================================================

    def load_suppliers(self):
        self.supplier_map = {"No Supplier": None}
        values = ["No Supplier"]

        try:
            with get_connection() as connection:
                cursor = connection.cursor()

                cursor.execute("""
                    SELECT supplier_id, name
                    FROM suppliers
                    ORDER BY name
                """)

                suppliers = cursor.fetchall()

            for supplier in suppliers:
                supplier_id = supplier["supplier_id"]
                supplier_name = supplier["name"]

                display_name = (
                    f"{supplier_id} - {supplier_name}"
                )

                self.supplier_map[display_name] = supplier_id
                values.append(display_name)

            self.supplier_combo.configure(
                values=values
            )

            if self.supplier_var.get() not in values:
                self.supplier_var.set("No Supplier")

        except Exception as error:
            print("Load suppliers error:", error)

            self.supplier_combo.configure(
                values=["No Supplier"]
            )

            self.supplier_var.set("No Supplier")

    def get_supplier_id(self):
        return self.supplier_map.get(
            self.supplier_var.get()
        )

    def get_supplier_display(self, supplier_id):
        if supplier_id is None:
            return "No Supplier"

        for display_name, current_id in self.supplier_map.items():
            if current_id == supplier_id:
                return display_name

        return "No Supplier"

    # =========================================================
    # VALIDATION
    # =========================================================

    def validate(self):
        name = self.name_var.get().strip()
        batch = self.batch_var.get().strip()
        expiry = self.expiry_var.get().strip()

        if not name:
            messagebox.showwarning(
                "Validation Error",
                "Medicine name is required."
            )
            return False

        if not batch:
            messagebox.showwarning(
                "Validation Error",
                "Batch number is required."
            )
            return False

        if not expiry:
            messagebox.showwarning(
                "Validation Error",
                "Expiry date is required."
            )
            return False

        try:
            datetime.strptime(expiry, "%Y-%m-%d")

        except ValueError:
            messagebox.showwarning(
                "Invalid Expiry Date",
                "Enter expiry date in YYYY-MM-DD format.\n"
                "Example: 2027-12-31"
            )
            return False

        try:
            purchase = float(
                self.purchase_var.get() or 0
            )

            selling = float(
                self.selling_var.get() or 0
            )

            quantity = int(
                self.quantity_var.get() or 0
            )

            min_stock = int(
                self.min_stock_var.get() or 0
            )

            if purchase < 0 or selling < 0:
                messagebox.showwarning(
                    "Invalid Price",
                    "Prices cannot be negative."
                )
                return False

            if quantity < 0 or min_stock < 0:
                messagebox.showwarning(
                    "Invalid Stock",
                    "Quantity and minimum stock cannot be negative."
                )
                return False

        except ValueError:
            messagebox.showwarning(
                "Invalid Input",
                "Enter valid numeric values for prices and stock."
            )
            return False

        if selling < purchase:
            answer = messagebox.askyesno(
                "Price Warning",
                "Selling price is lower than purchase price.\n"
                "Do you want to continue?"
            )

            if not answer:
                return False

        return True

    def get_form_values(self):
        return (
            self.name_var.get().strip(),
            self.category_var.get().strip(),
            self.manufacturer_var.get().strip(),
            self.batch_var.get().strip(),
            float(self.purchase_var.get() or 0),
            float(self.selling_var.get() or 0),
            int(self.quantity_var.get() or 0),
            int(self.min_stock_var.get() or 0),
            self.expiry_var.get().strip(),
            self.get_supplier_id(),
            self.description_var.get().strip()
        )

    # =========================================================
    # ADD MEDICINE
    # =========================================================

    def add_medicine(self):
        if not self.validate():
            return

        values = self.get_form_values()

        try:
            with get_connection() as connection:
                cursor = connection.cursor()

                cursor.execute("""
                    INSERT INTO medicines (
                        name,
                        category,
                        manufacturer,
                        batch_no,
                        purchase_price,
                        selling_price,
                        quantity,
                        min_stock,
                        expiry_date,
                        supplier_id,
                        description
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values)

            messagebox.showinfo(
                "Success",
                "Medicine added successfully."
            )

            self.clear_form()
            self.load_medicines()

        except Exception as error:
            if "UNIQUE" in str(error).upper():
                messagebox.showerror(
                    "Duplicate Medicine",
                    "This batch number may already exist."
                )
            else:
                messagebox.showerror(
                    "Database Error",
                    f"Could not add medicine.\n\n{error}"
                )

    # =========================================================
    # LOAD MEDICINES
    # =========================================================

    def load_medicines(self):
        try:
            with get_connection() as connection:
                cursor = connection.cursor()

                cursor.execute("""
                    SELECT
                        m.medicine_id,
                        m.name,
                        m.category,
                        m.manufacturer,
                        m.batch_no,
                        m.purchase_price,
                        m.selling_price,
                        m.quantity,
                        m.min_stock,
                        m.expiry_date,
                        m.supplier_id,
                        COALESCE(
                            s.name, 'No Supplier'
                        ) AS supplier_name
                    FROM medicines m
                    LEFT JOIN suppliers s
                        ON m.supplier_id = s.supplier_id
                    ORDER BY m.medicine_id DESC
                """)

                medicines = cursor.fetchall()

            self.clear_table()

            for medicine in medicines:
                self.insert_into_table(medicine)

        except Exception as error:
            print("Load medicines error:", error)

            messagebox.showerror(
                "Database Error",
                f"Could not load medicines.\n\n{error}"
            )

    def insert_into_table(self, medicine):
        try:
            purchase = float(
                medicine["purchase_price"] or 0
            )

            selling = float(
                medicine["selling_price"] or 0
            )

        except (TypeError, ValueError):
            purchase = 0.0
            selling = 0.0

        self.tree.insert(
            "",
            "end",
            values=(
                medicine["medicine_id"],
                medicine["name"] or "",
                medicine["category"] or "",
                medicine["manufacturer"] or "",
                medicine["batch_no"] or "",
                f"Rs. {purchase:.2f}",
                f"Rs. {selling:.2f}",
                medicine["quantity"],
                medicine["min_stock"],
                medicine["expiry_date"] or "",
                medicine["supplier_name"] or "No Supplier"
            )
        )

    # =========================================================
    # SEARCH MEDICINES
    # =========================================================

    def search_medicines(self):
        search_text = self.search_var.get().strip()

        if not search_text:
            self.load_medicines()
            return

        pattern = f"%{search_text}%"

        try:
            with get_connection() as connection:
                cursor = connection.cursor()

                cursor.execute("""
                    SELECT
                        m.medicine_id,
                        m.name,
                        m.category,
                        m.manufacturer,
                        m.batch_no,
                        m.purchase_price,
                        m.selling_price,
                        m.quantity,
                        m.min_stock,
                        m.expiry_date,
                        m.supplier_id,
                        COALESCE(
                            s.name, 'No Supplier'
                        ) AS supplier_name
                    FROM medicines m
                    LEFT JOIN suppliers s
                        ON m.supplier_id = s.supplier_id
                    WHERE
                        m.name LIKE ?
                        OR COALESCE(m.category, '') LIKE ?
                        OR COALESCE(m.manufacturer, '') LIKE ?
                        OR m.batch_no LIKE ?
                        OR COALESCE(s.name, '') LIKE ?
                    ORDER BY m.medicine_id DESC
                """, (
                    pattern,
                    pattern,
                    pattern,
                    pattern,
                    pattern
                ))

                medicines = cursor.fetchall()

            self.clear_table()

            for medicine in medicines:
                self.insert_into_table(medicine)

            if not medicines:
                messagebox.showinfo(
                    "Search Results",
                    "No medicines found."
                )

        except Exception as error:
            messagebox.showerror(
                "Search Error",
                f"Could not search medicines.\n\n{error}"
            )

    # =========================================================
    # SELECT MEDICINE
    # =========================================================

    def select_medicine(self, event=None):
        selection = self.tree.selection()

        if not selection:
            return

        item = self.tree.item(selection[0])
        values = item.get("values", [])

        if not values:
            return

        medicine_id = values[0]

        try:
            with get_connection() as connection:
                cursor = connection.cursor()

                cursor.execute("""
                    SELECT *
                    FROM medicines
                    WHERE medicine_id = ?
                """, (medicine_id,))

                medicine = cursor.fetchone()

            if medicine is None:
                messagebox.showwarning(
                    "Not Found",
                    "The selected medicine no longer exists."
                )

                self.load_medicines()
                return

            self.selected_medicine_id = medicine["medicine_id"]

            self.name_var.set(medicine["name"] or "")
            self.category_var.set(medicine["category"] or "")
            self.manufacturer_var.set(
                medicine["manufacturer"] or ""
            )
            self.batch_var.set(medicine["batch_no"] or "")

            self.purchase_var.set(
                str(medicine["purchase_price"] or 0)
            )

            self.selling_var.set(
                str(medicine["selling_price"] or 0)
            )

            self.quantity_var.set(
                str(medicine["quantity"] or 0)
            )

            self.min_stock_var.set(
                str(medicine["min_stock"] or 0)
            )

            self.expiry_var.set(
                medicine["expiry_date"] or ""
            )

            self.description_var.set(
                medicine["description"] or ""
            )

            self.supplier_var.set(
                self.get_supplier_display(
                    medicine["supplier_id"]
                )
            )

        except Exception as error:
            messagebox.showerror(
                "Selection Error",
                f"Could not load the selected medicine.\n\n{error}"
            )

    # =========================================================
    # UPDATE MEDICINE
    # =========================================================

    def update_medicine(self):
        if self.selected_medicine_id is None:
            messagebox.showwarning(
                "Select Medicine",
                "Double-click a medicine in the table before updating."
            )
            return

        if not self.validate():
            return

        values = self.get_form_values()

        try:
            with get_connection() as connection:
                cursor = connection.cursor()

                cursor.execute("""
                    UPDATE medicines
                    SET
                        name = ?,
                        category = ?,
                        manufacturer = ?,
                        batch_no = ?,
                        purchase_price = ?,
                        selling_price = ?,
                        quantity = ?,
                        min_stock = ?,
                        expiry_date = ?,
                        supplier_id = ?,
                        description = ?
                    WHERE medicine_id = ?
                """, values + (self.selected_medicine_id,))

                updated_rows = cursor.rowcount

            if updated_rows > 0:
                messagebox.showinfo(
                    "Success",
                    "Medicine updated successfully."
                )
            else:
                messagebox.showwarning(
                    "Not Found",
                    "The selected medicine was not found."
                )

            self.clear_form()
            self.load_medicines()

        except Exception as error:
            if "UNIQUE" in str(error).upper():
                messagebox.showerror(
                    "Duplicate Medicine",
                    "This batch number may already exist."
                )
            else:
                messagebox.showerror(
                    "Update Error",
                    f"Could not update medicine.\n\n{error}"
                )

    # =========================================================
    # DELETE MEDICINE
    # =========================================================

    def delete_medicine(self):
        if self.selected_medicine_id is None:
            messagebox.showwarning(
                "Select Medicine",
                "Double-click a medicine in the table before deleting."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this medicine?\n\n"
            "This action cannot be undone."
        )

        if not confirm:
            return

        try:
            with get_connection() as connection:
                cursor = connection.cursor()

                cursor.execute("""
                    DELETE FROM medicines
                    WHERE medicine_id = ?
                """, (self.selected_medicine_id,))

                deleted_rows = cursor.rowcount

            if deleted_rows > 0:
                messagebox.showinfo(
                    "Success",
                    "Medicine deleted successfully."
                )
            else:
                messagebox.showwarning(
                    "Not Found",
                    "The selected medicine was not found."
                )

            self.clear_form()
            self.load_medicines()

        except Exception as error:
            messagebox.showerror(
                "Delete Error",
                "Could not delete this medicine.\n\n"
                f"{error}\n\n"
                "It may be linked to an existing sale or invoice."
            )

    # =========================================================
    # CLEAR FORM
    # =========================================================

    def clear_form(self):
        self.selected_medicine_id = None

        self.name_var.set("")
        self.category_var.set("")
        self.manufacturer_var.set("")
        self.batch_var.set("")
        self.purchase_var.set("")
        self.selling_var.set("")
        self.quantity_var.set("")
        self.min_stock_var.set("10")
        self.expiry_var.set("")
        self.description_var.set("")
        self.supplier_var.set("No Supplier")

        for item in self.tree.selection():
            self.tree.selection_remove(item)

    # =========================================================
    # CLEAR TABLE
    # =========================================================

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    # =========================================================
    # REFRESH
    # =========================================================

    def refresh_data(self):
        self.search_var.set("")
        self.load_suppliers()
        self.load_medicines()