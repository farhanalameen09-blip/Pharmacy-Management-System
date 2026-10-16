import customtkinter as ctk # type: ignore

from ui_kit import styled_treeview
from tkinter import ttk, messagebox
from datetime import datetime

from database import get_connection


class MedicinePage(ctk.CTkFrame):

    def __init__(self, parent, back_to_dashboard):

        super().__init__(parent, fg_color="transparent")

        self.back_to_dashboard = back_to_dashboard
        self.selected_medicine_id = None
        self.supplier_map = {}

        # =====================================================
        # VARIABLES
        # =====================================================

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

    # =====================================================
    # UI
    # =====================================================

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
            text="Medicine Management",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        )

        title.pack(side="left")

        back_button = ctk.CTkButton(
            header,
            text="Back to Dashboard",
            width=160,
            command=self.back_to_dashboard
        )

        back_button.pack(side="right")

        # =====================================================
        # FORM
        # =====================================================

        form_frame = ctk.CTkFrame(
            self,
            corner_radius=12
        )

        form_frame.pack(
            fill="x",
            padx=25,
            pady=10
        )

        form_title = ctk.CTkLabel(
            form_frame,
            text="Medicine Details",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        )

        form_title.grid(
            row=0,
            column=0,
            columnspan=4,
            padx=15,
            pady=(15, 10),
            sticky="w"
        )

        # Row 1

        self.create_entry(
            form_frame,
            "Medicine Name *",
            self.name_var,
            1,
            0,
            "Example: Paracetamol"
        )

        self.create_entry(
            form_frame,
            "Category",
            self.category_var,
            1,
            1,
            "Example: Tablet"
        )

        self.create_entry(
            form_frame,
            "Manufacturer",
            self.manufacturer_var,
            1,
            2,
            "Example: Cipla"
        )

        self.create_entry(
            form_frame,
            "Batch Number *",
            self.batch_var,
            1,
            3,
            "Example: PCM001"
        )

        # Row 2

        self.create_entry(
            form_frame,
            "Purchase Price",
            self.purchase_var,
            2,
            0,
            "Example: 20"
        )

        self.create_entry(
            form_frame,
            "Selling Price",
            self.selling_var,
            2,
            1,
            "Example: 25"
        )

        self.create_entry(
            form_frame,
            "Quantity",
            self.quantity_var,
            2,
            2,
            "Example: 100"
        )

        self.create_entry(
            form_frame,
            "Minimum Stock",
            self.min_stock_var,
            2,
            3,
            "Example: 10"
        )

        # Row 3

        self.create_entry(
            form_frame,
            "Expiry Date *",
            self.expiry_var,
            3,
            0,
            "YYYY-MM-DD"
        )

        # Supplier

        supplier_frame = ctk.CTkFrame(
            form_frame,
            fg_color="transparent"
        )

        supplier_frame.grid(
            row=3,
            column=1,
            padx=10,
            pady=6,
            sticky="ew"
        )

        ctk.CTkLabel(
            supplier_frame,
            text="Supplier"
        ).pack(anchor="w")

        self.supplier_combo = ctk.CTkComboBox(
            supplier_frame,
            variable=self.supplier_var,
            values=["No Supplier"],
            height=35
        )

        self.supplier_combo.pack(
            fill="x",
            pady=(3, 0)
        )

        # Description

        self.create_entry(
            form_frame,
            "Description",
            self.description_var,
            3,
            2,
            "Optional"
        )

        # =====================================================
        # BUTTONS
        # =====================================================

        button_frame = ctk.CTkFrame(
            form_frame,
            fg_color="transparent"
        )

        button_frame.grid(
            row=3,
            column=3,
            padx=10,
            pady=10,
            sticky="e"
        )

        ctk.CTkButton(
            button_frame,
            text="Add",
            width=80,
            command=self.add_medicine
        ).pack(
            side="left",
            padx=3
        )

        ctk.CTkButton(
            button_frame,
            text="Update",
            width=80,
            command=self.update_medicine
        ).pack(
            side="left",
            padx=3
        )

        ctk.CTkButton(
            button_frame,
            text="Delete",
            width=80,
            fg_color="#c0392b",
            hover_color="#922b21",
            command=self.delete_medicine
        ).pack(
            side="left",
            padx=3
        )

        ctk.CTkButton(
            button_frame,
            text="Clear",
            width=80,
            fg_color="gray",
            hover_color="#666666",
            command=self.clear_form
        ).pack(
            side="left",
            padx=3
        )

        # =====================================================
        # SEARCH
        # =====================================================

        search_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        search_frame.pack(
            fill="x",
            padx=25,
            pady=5
        )

        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Search medicine, category, manufacturer, batch or supplier...",
            height=38
        )

        search_entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        search_entry.bind(
            "<KeyRelease>",
            lambda event: self.search_medicines()
        )

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=100,
            command=self.search_medicines
        ).pack(
            side="left",
            padx=5
        )

        ctk.CTkButton(
            search_frame,
            text="Refresh",
            width=100,
            command=self.refresh_data
        ).pack(
            side="left"
        )

        # =====================================================
        # TABLE
        # =====================================================

        table_frame = ctk.CTkFrame(
            self,
            corner_radius=10
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(5, 20)
        )

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
            show="headings"
        )

        headings = {
            "id": "ID",
            "name": "Medicine",
            "category": "Category",
            "manufacturer": "Manufacturer",
            "batch": "Batch",
            "purchase": "Purchase",
            "selling": "Selling",
            "quantity": "Quantity",
            "min_stock": "Min Stock",
            "expiry": "Expiry",
            "supplier": "Supplier"
        }

        widths = {
            "id": 50,
            "name": 150,
            "category": 100,
            "manufacturer": 120,
            "batch": 100,
            "purchase": 90,
            "selling": 90,
            "quantity": 80,
            "min_stock": 80,
            "expiry": 105,
            "supplier": 130
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

        self.tree.column(
            "name",
            anchor="w"
        )

        self.tree.bind(
            "<Double-1>",
            self.select_medicine
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar_y = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        scrollbar_y.pack(
            side="right",
            fill="y"
        )

        self.tree.configure(
            yscrollcommand=scrollbar_y.set
        )

        scrollbar_x = ttk.Scrollbar(
            self,
            orient="horizontal",
            command=self.tree.xview
        )

        scrollbar_x.pack(
            fill="x",
            padx=25
        )

        self.tree.configure(
            xscrollcommand=scrollbar_x.set
        )

    # =====================================================
    # ENTRY CREATOR
    # =====================================================

    def create_entry(
        self,
        parent,
        label,
        variable,
        row,
        column,
        placeholder=""
    ):

        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        frame.grid(
            row=row,
            column=column,
            padx=10,
            pady=6,
            sticky="ew"
        )

        parent.grid_columnconfigure(
            column,
            weight=1
        )

        ctk.CTkLabel(
            frame,
            text=label
        ).pack(
            anchor="w"
        )

        ctk.CTkEntry(
            frame,
            textvariable=variable,
            height=35,
            placeholder_text=placeholder
        ).pack(
            fill="x",
            pady=(3, 0)
        )

    # =====================================================
    # SUPPLIERS
    # =====================================================

    def load_suppliers(self):

        connection = None

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT supplier_id, name
                FROM suppliers
                ORDER BY name
                """
            )

            suppliers = cursor.fetchall()

            self.supplier_map = {
                "No Supplier": None
            }

            values = [
                "No Supplier"
            ]

            for supplier in suppliers:

                supplier_id = supplier["supplier_id"]
                supplier_name = supplier["name"]

                display_name = (
                    f"{supplier_id} - {supplier_name}"
                )

                self.supplier_map[
                    display_name
                ] = supplier_id

                values.append(
                    display_name
                )

            self.supplier_combo.configure(
                values=values
            )

        except Exception as error:

            print(
                "Load suppliers error:",
                error
            )

            self.supplier_map = {
                "No Supplier": None
            }

            self.supplier_combo.configure(
                values=["No Supplier"]
            )

        finally:

            if connection:
                connection.close()

    def get_supplier_id(self):

        return self.supplier_map.get(
            self.supplier_var.get()
        )

    def get_supplier_display(
        self,
        supplier_id
    ):

        if supplier_id is None:
            return "No Supplier"

        for name, value in self.supplier_map.items():

            if value == supplier_id:
                return name

        return "No Supplier"

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(self):

        name = self.name_var.get().strip()
        batch = self.batch_var.get().strip()
        expiry = self.expiry_var.get().strip()

        if not name:

            messagebox.showwarning(
                "Validation",
                "Please enter medicine name."
            )

            return False

        if not batch:

            messagebox.showwarning(
                "Validation",
                "Please enter batch number."
            )

            return False

        if not expiry:

            messagebox.showwarning(
                "Validation",
                "Please enter expiry date."
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

            minimum = int(
                self.min_stock_var.get() or 0
            )

            if purchase < 0:
                raise ValueError

            if selling < 0:
                raise ValueError

            if quantity < 0:
                raise ValueError

            if minimum < 0:
                raise ValueError

        except ValueError:

            messagebox.showwarning(
                "Validation",
                "Please enter valid non-negative prices and quantities."
            )

            return False

        try:

            datetime.strptime(
                expiry,
                "%Y-%m-%d"
            )

        except ValueError:

            messagebox.showwarning(
                "Validation",
                "Expiry date must be in YYYY-MM-DD format."
            )

            return False

        if selling < purchase:

            answer = messagebox.askyesno(
                "Price Warning",
                "Selling price is lower than purchase price.\n\n"
                "Do you want to continue?"
            )

            if not answer:
                return False

        return True

    # =====================================================
    # ADD
    # =====================================================

    def add_medicine(self):

        if not self.validate():
            return

        connection = None

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO medicines
                (
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
                """,
                (
                    self.name_var.get().strip(),
                    self.category_var.get().strip(),
                    self.manufacturer_var.get().strip(),
                    self.batch_var.get().strip(),
                    float(
                        self.purchase_var.get() or 0
                    ),
                    float(
                        self.selling_var.get() or 0
                    ),
                    int(
                        self.quantity_var.get() or 0
                    ),
                    int(
                        self.min_stock_var.get() or 0
                    ),
                    self.expiry_var.get().strip(),
                    self.get_supplier_id(),
                    self.description_var.get().strip()
                )
            )

            connection.commit()

            messagebox.showinfo(
                "Success",
                "Medicine added successfully."
            )

            self.clear_form()
            self.load_medicines()

        except Exception as error:

            if "UNIQUE" in str(error).upper():

                messagebox.showerror(
                    "Duplicate Batch",
                    "This batch number already exists."
                )

            else:

                messagebox.showerror(
                    "Database Error",
                    f"Unable to add medicine.\n\n{error}"
                )

            print(
                "Add medicine error:",
                error
            )

        finally:

            if connection:
                connection.close()

    # =====================================================
    # LOAD
    # =====================================================

    def load_medicines(self):

        self.clear_table()

        connection = None

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
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
                        s.name,
                        'No Supplier'
                    ) AS supplier_name
                FROM medicines m
                LEFT JOIN suppliers s
                    ON m.supplier_id = s.supplier_id
                ORDER BY m.medicine_id DESC
                """
            )

            medicines = cursor.fetchall()

            for medicine in medicines:

                self.insert_into_table(
                    medicine
                )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                f"Unable to load medicines.\n\n{error}"
            )

            print(
                "Load medicines error:",
                error
            )

        finally:

            if connection:
                connection.close()

    # =====================================================
    # TABLE
    # =====================================================

    def insert_into_table(
        self,
        medicine
    ):

        try:

            purchase = float(
                medicine["purchase_price"] or 0
            )

        except (TypeError, ValueError):

            purchase = 0

        try:

            selling = float(
                medicine["selling_price"] or 0
            )

        except (TypeError, ValueError):

            selling = 0

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
                medicine["quantity"] or 0,
                medicine["min_stock"] or 0,
                medicine["expiry_date"] or "",
                medicine["supplier_name"] or "No Supplier"
            )
        )

    # =====================================================
    # SEARCH
    # =====================================================

    def search_medicines(self):

        search = self.search_var.get().strip()

        if not search:

            self.load_medicines()

            return

        self.clear_table()

        connection = None

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
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
                        s.name,
                        'No Supplier'
                    ) AS supplier_name
                FROM medicines m
                LEFT JOIN suppliers s
                    ON m.supplier_id = s.supplier_id
                WHERE
                    m.name LIKE ?
                    OR m.category LIKE ?
                    OR m.manufacturer LIKE ?
                    OR m.batch_no LIKE ?
                    OR s.name LIKE ?
                ORDER BY m.medicine_id DESC
                """,
                (
                    f"%{search}%",
                    f"%{search}%",
                    f"%{search}%",
                    f"%{search}%",
                    f"%{search}%"
                )
            )

            medicines = cursor.fetchall()

            for medicine in medicines:

                self.insert_into_table(
                    medicine
                )

        except Exception as error:

            messagebox.showerror(
                "Search Error",
                f"Unable to search medicines.\n\n{error}"
            )

            print(
                "Search error:",
                error
            )

        finally:

            if connection:
                connection.close()

    # =====================================================
    # SELECT
    # =====================================================

    def select_medicine(
        self,
        event=None
    ):

        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(
            selected[0]
        )["values"]

        if not values:
            return

        self.selected_medicine_id = values[0]

        connection = None

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT *
                FROM medicines
                WHERE medicine_id = ?
                """,
                (
                    self.selected_medicine_id,
                )
            )

            medicine = cursor.fetchone()

            if medicine:

                self.name_var.set(
                    medicine["name"] or ""
                )

                self.category_var.set(
                    medicine["category"] or ""
                )

                self.manufacturer_var.set(
                    medicine["manufacturer"] or ""
                )

                self.batch_var.set(
                    medicine["batch_no"] or ""
                )

                self.purchase_var.set(
                    medicine["purchase_price"]
                    if medicine["purchase_price"] is not None
                    else ""
                )

                self.selling_var.set(
                    medicine["selling_price"]
                    if medicine["selling_price"] is not None
                    else ""
                )

                self.quantity_var.set(
                    medicine["quantity"]
                    if medicine["quantity"] is not None
                    else ""
                )

                self.min_stock_var.set(
                    medicine["min_stock"]
                    if medicine["min_stock"] is not None
                    else "10"
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
                "Error",
                f"Unable to select medicine.\n\n{error}"
            )

            print(
                "Select medicine error:",
                error
            )

        finally:

            if connection:
                connection.close()

    # =====================================================
    # UPDATE
    # =====================================================

    def update_medicine(self):

        if not self.selected_medicine_id:

            messagebox.showwarning(
                "Update Medicine",
                "Please double-click a medicine from the table first."
            )

            return

        if not self.validate():
            return

        connection = None

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
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
                """,
                (
                    self.name_var.get().strip(),
                    self.category_var.get().strip(),
                    self.manufacturer_var.get().strip(),
                    self.batch_var.get().strip(),
                    float(
                        self.purchase_var.get() or 0
                    ),
                    float(
                        self.selling_var.get() or 0
                    ),
                    int(
                        self.quantity_var.get() or 0
                    ),
                    int(
                        self.min_stock_var.get() or 0
                    ),
                    self.expiry_var.get().strip(),
                    self.get_supplier_id(),
                    self.description_var.get().strip(),
                    self.selected_medicine_id
                )
            )

            connection.commit()

            messagebox.showinfo(
                "Success",
                "Medicine updated successfully."
            )

            self.clear_form()
            self.load_medicines()

        except Exception as error:

            if "UNIQUE" in str(error).upper():

                messagebox.showerror(
                    "Duplicate Batch",
                    "This batch number already exists."
                )

            else:

                messagebox.showerror(
                    "Update Error",
                    f"Unable to update medicine.\n\n{error}"
                )

            print(
                "Update medicine error:",
                error
            )

        finally:

            if connection:
                connection.close()

    # =====================================================
    # DELETE
    # =====================================================

    def delete_medicine(self):

        if not self.selected_medicine_id:

            messagebox.showwarning(
                "Delete Medicine",
                "Please double-click a medicine from the table first."
            )

            return

        confirm = messagebox.askyesno(
            "Delete Medicine",
            "Are you sure you want to delete this medicine?"
        )

        if not confirm:
            return

        connection = None

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM medicines
                WHERE medicine_id = ?
                """,
                (
                    self.selected_medicine_id,
                )
            )

            connection.commit()

            messagebox.showinfo(
                "Success",
                "Medicine deleted successfully."
            )

            self.clear_form()
            self.load_medicines()

        except Exception as error:

            messagebox.showerror(
                "Delete Error",
                f"Unable to delete medicine.\n\n{error}"
            )

            print(
                "Delete medicine error:",
                error
            )

        finally:

            if connection:
                connection.close()

    # =====================================================
    # CLEAR
    # =====================================================

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

        self.supplier_var.set(
            "No Supplier"
        )

        try:

            for item in self.tree.selection():

                self.tree.selection_remove(
                    item
                )

        except Exception:
            pass

    # =====================================================
    # CLEAR TABLE
    # =====================================================

    def clear_table(self):

        if hasattr(
            self,
            "tree"
        ):

            for item in self.tree.get_children():

                self.tree.delete(
                    item
                )

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh_data(self):

        self.load_suppliers()
        self.load_medicines()