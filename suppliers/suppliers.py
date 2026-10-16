import customtkinter as ctk
from ui_kit import styled_treeview
from tkinter import ttk, messagebox

from database import get_connection


class SupplierPage(ctk.CTkFrame):

    def __init__(self, parent, back_callback):
        super().__init__(parent, fg_color="transparent")

        self.back_callback = back_callback
        self.selected_supplier_id = None

        self.create_database_table()
        self.create_ui()
        self.load_suppliers()

    # ==========================================
    # DATABASE
    # ==========================================

    def create_database_table(self):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT
            )
        """)

        connection.commit()
        connection.close()

    # ==========================================
    # UI
    # ==========================================

    def create_ui(self):

        title = ctk.CTkLabel(
            self,
            text="🚚 Supplier Management",
            font=ctk.CTkFont(size=30, weight="bold")
        )
        title.pack(pady=(20, 5))

        subtitle = ctk.CTkLabel(
            self,
            text="Add, update, search and manage pharmacy suppliers",
            font=ctk.CTkFont(size=15)
        )
        subtitle.pack(pady=(0, 20))

        # ==========================================
        # FORM
        # ==========================================

        form_frame = ctk.CTkFrame(self)
        form_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )

        # Supplier Name
        ctk.CTkLabel(
            form_frame,
            text="Supplier Name"
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 5),
            sticky="w"
        )

        self.name_entry = ctk.CTkEntry(
            form_frame,
            width=250,
            placeholder_text="Enter supplier name"
        )
        self.name_entry.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15)
        )

        # Contact Person
        ctk.CTkLabel(
            form_frame,
            text="Contact Person"
        ).grid(
            row=0,
            column=1,
            padx=15,
            pady=(15, 5),
            sticky="w"
        )

        self.contact_entry = ctk.CTkEntry(
            form_frame,
            width=220,
            placeholder_text="Enter contact person"
        )
        self.contact_entry.grid(
            row=1,
            column=1,
            padx=15,
            pady=(0, 15)
        )

        # Phone
        ctk.CTkLabel(
            form_frame,
            text="Phone"
        ).grid(
            row=0,
            column=2,
            padx=15,
            pady=(15, 5),
            sticky="w"
        )

        self.phone_entry = ctk.CTkEntry(
            form_frame,
            width=200,
            placeholder_text="Enter phone"
        )
        self.phone_entry.grid(
            row=1,
            column=2,
            padx=15,
            pady=(0, 15)
        )

        # Email
        ctk.CTkLabel(
            form_frame,
            text="Email"
        ).grid(
            row=2,
            column=0,
            padx=15,
            pady=(5, 5),
            sticky="w"
        )

        self.email_entry = ctk.CTkEntry(
            form_frame,
            width=250,
            placeholder_text="Enter email"
        )
        self.email_entry.grid(
            row=3,
            column=0,
            padx=15,
            pady=(0, 15)
        )

        # Address
        ctk.CTkLabel(
            form_frame,
            text="Address"
        ).grid(
            row=2,
            column=1,
            padx=15,
            pady=(5, 5),
            sticky="w"
        )

        self.address_entry = ctk.CTkEntry(
            form_frame,
            width=450,
            placeholder_text="Enter address"
        )
        self.address_entry.grid(
            row=3,
            column=1,
            columnspan=2,
            padx=15,
            pady=(0, 15),
            sticky="w"
        )

        # ==========================================
        # BUTTONS
        # ==========================================

        button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        button_frame.pack(pady=10)

        ctk.CTkButton(
            button_frame,
            text="➕ Add Supplier",
            width=140,
            command=self.add_supplier
        ).grid(row=0, column=0, padx=5)

        ctk.CTkButton(
            button_frame,
            text="✏️ Update",
            width=120,
            command=self.update_supplier
        ).grid(row=0, column=1, padx=5)

        ctk.CTkButton(
            button_frame,
            text="🗑️ Delete",
            width=120,
            command=self.delete_supplier
        ).grid(row=0, column=2, padx=5)

        ctk.CTkButton(
            button_frame,
            text="Clear",
            width=100,
            command=self.clear_form
        ).grid(row=0, column=3, padx=5)

        ctk.CTkButton(
            button_frame,
            text="🔄 Refresh",
            width=120,
            command=self.load_suppliers
        ).grid(row=0, column=4, padx=5)

        # ==========================================
        # SEARCH
        # ==========================================

        search_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        search_frame.pack(
            fill="x",
            padx=30,
            pady=(10, 5)
        )

        ctk.CTkLabel(
            search_frame,
            text="Search Supplier:"
        ).pack(
            side="left",
            padx=(0, 10)
        )

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            placeholder_text="Search by name or phone"
        )
        self.search_entry.pack(side="left")

        ctk.CTkButton(
            search_frame,
            text="🔍 Search",
            width=100,
            command=self.search_suppliers
        ).pack(
            side="left",
            padx=10
        )

        # ==========================================
        # TABLE
        # ==========================================

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        columns = (
            "id",
            "name",
            "contact",
            "phone",
            "email",
            "address"
        )

        self.supplier_tree = styled_treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.supplier_tree.heading(
            "id",
            text="ID"
        )

        self.supplier_tree.heading(
            "name",
            text="Supplier Name"
        )

        self.supplier_tree.heading(
            "contact",
            text="Contact Person"
        )

        self.supplier_tree.heading(
            "phone",
            text="Phone"
        )

        self.supplier_tree.heading(
            "email",
            text="Email"
        )

        self.supplier_tree.heading(
            "address",
            text="Address"
        )

        self.supplier_tree.column(
            "id",
            width=60,
            anchor="center"
        )

        self.supplier_tree.column(
            "name",
            width=180
        )

        self.supplier_tree.column(
            "contact",
            width=170
        )

        self.supplier_tree.column(
            "phone",
            width=140
        )

        self.supplier_tree.column(
            "email",
            width=210
        )

        self.supplier_tree.column(
            "address",
            width=280
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.supplier_tree.yview
        )

        self.supplier_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.supplier_tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.supplier_tree.bind(
            "<ButtonRelease-1>",
            self.select_supplier
        )

        # ==========================================
        # BACK BUTTON
        # ==========================================

        ctk.CTkButton(
            self,
            text="← Back to Dashboard",
            width=180,
            command=self.back_callback
        ).pack(
            pady=(5, 15)
        )

    # ==========================================
    # LOAD SUPPLIERS
    # ==========================================

    def load_suppliers(self):

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    supplier_id,
                    name,
                    contact_person,
                    phone,
                    email,
                    address
                FROM suppliers
                ORDER BY supplier_id DESC
            """)

            suppliers = cursor.fetchall()

            connection.close()

            self.supplier_tree.delete(
                *self.supplier_tree.get_children()
            )

            for supplier in suppliers:

                self.supplier_tree.insert(
                    "",
                    "end",
                    values=(
                        supplier["supplier_id"],
                        supplier["name"],
                        supplier["contact_person"] or "",
                        supplier["phone"] or "",
                        supplier["email"] or "",
                        supplier["address"] or ""
                    )
                )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                f"Unable to load suppliers.\n\n{error}"
            )

    # ==========================================
    # ADD SUPPLIER
    # ==========================================

    def add_supplier(self):

        name = self.name_entry.get().strip()
        contact = self.contact_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name:

            messagebox.showwarning(
                "Required",
                "Please enter supplier name."
            )

            return

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO suppliers
                (
                    name,
                    contact_person,
                    phone,
                    email,
                    address
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                name,
                contact,
                phone,
                email,
                address
            ))

            connection.commit()
            connection.close()

            messagebox.showinfo(
                "Success",
                "Supplier added successfully."
            )

            self.clear_form()
            self.load_suppliers()

        except Exception as error:

            messagebox.showerror(
                "Error",
                f"Unable to add supplier.\n\n{error}"
            )

    # ==========================================
    # SELECT SUPPLIER
    # ==========================================

    def select_supplier(self, event=None):

        selected = self.supplier_tree.selection()

        if not selected:
            return

        item = self.supplier_tree.item(
            selected[0]
        )

        values = item["values"]

        if not values:
            return

        self.selected_supplier_id = values[0]

        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, values[1])

        self.contact_entry.delete(0, "end")
        self.contact_entry.insert(0, values[2])

        self.phone_entry.delete(0, "end")
        self.phone_entry.insert(0, values[3])

        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, values[4])

        self.address_entry.delete(0, "end")
        self.address_entry.insert(0, values[5])

    # ==========================================
    # UPDATE SUPPLIER
    # ==========================================

    def update_supplier(self):

        if not self.selected_supplier_id:

            messagebox.showwarning(
                "Select Supplier",
                "Please select a supplier from the table first."
            )

            return

        name = self.name_entry.get().strip()
        contact = self.contact_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name:

            messagebox.showwarning(
                "Required",
                "Supplier name cannot be empty."
            )

            return

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE suppliers
                SET
                    name = ?,
                    contact_person = ?,
                    phone = ?,
                    email = ?,
                    address = ?
                WHERE supplier_id = ?
            """, (
                name,
                contact,
                phone,
                email,
                address,
                self.selected_supplier_id
            ))

            connection.commit()
            connection.close()

            messagebox.showinfo(
                "Success",
                "Supplier updated successfully."
            )

            self.clear_form()
            self.load_suppliers()

        except Exception as error:

            messagebox.showerror(
                "Error",
                f"Unable to update supplier.\n\n{error}"
            )

    # ==========================================
    # DELETE SUPPLIER
    # ==========================================

    def delete_supplier(self):

        if not self.selected_supplier_id:

            messagebox.showwarning(
                "Select Supplier",
                "Please select a supplier first."
            )

            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this supplier?"
        )

        if not confirm:
            return

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                DELETE FROM suppliers
                WHERE supplier_id = ?
            """, (
                self.selected_supplier_id,
            ))

            connection.commit()
            connection.close()

            messagebox.showinfo(
                "Success",
                "Supplier deleted successfully."
            )

            self.clear_form()
            self.load_suppliers()

        except Exception as error:

            messagebox.showerror(
                "Error",
                f"Unable to delete supplier.\n\n{error}"
            )

    # ==========================================
    # SEARCH SUPPLIERS
    # ==========================================

    def search_suppliers(self):

        search_text = self.search_entry.get().strip()

        if not search_text:

            self.load_suppliers()
            return

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    supplier_id,
                    name,
                    contact_person,
                    phone,
                    email,
                    address
                FROM suppliers
                WHERE name LIKE ?
                   OR contact_person LIKE ?
                   OR phone LIKE ?
                ORDER BY supplier_id DESC
            """, (
                f"%{search_text}%",
                f"%{search_text}%",
                f"%{search_text}%"
            ))

            suppliers = cursor.fetchall()

            connection.close()

            self.supplier_tree.delete(
                *self.supplier_tree.get_children()
            )

            for supplier in suppliers:

                self.supplier_tree.insert(
                    "",
                    "end",
                    values=(
                        supplier["supplier_id"],
                        supplier["name"],
                        supplier["contact_person"] or "",
                        supplier["phone"] or "",
                        supplier["email"] or "",
                        supplier["address"] or ""
                    )
                )

        except Exception as error:

            messagebox.showerror(
                "Search Error",
                f"Unable to search suppliers.\n\n{error}"
            )

    # ==========================================
    # CLEAR FORM
    # ==========================================

    def clear_form(self):

        self.selected_supplier_id = None

        self.name_entry.delete(0, "end")
        self.contact_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.address_entry.delete(0, "end")

        for item in self.supplier_tree.selection():

            self.supplier_tree.selection_remove(item)