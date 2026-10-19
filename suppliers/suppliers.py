import re
import customtkinter as ctk
from tkinter import ttk, messagebox

from ui_kit import styled_treeview
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
        try:
            with get_connection() as connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS suppliers (
                        supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        contact_person TEXT,
                        phone TEXT,
                        email TEXT,
                        address TEXT
                    )
                """)
        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Unable to initialize suppliers table.\n\n{error}"
            )

    # ==========================================
    # USER INTERFACE
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
            text="Manage your pharmacy suppliers efficiently",
            font=ctk.CTkFont(size=14)
        )
        subtitle.pack(pady=(0, 20))

        # Form
        form_frame = ctk.CTkFrame(self, corner_radius=12)
        form_frame.pack(fill="x", padx=30, pady=10)

        for column in range(3):
            form_frame.grid_columnconfigure(column, weight=1)

        # Supplier name
        self.create_field(
            form_frame, "Supplier Name",
            "Enter supplier name", 0, 0, "name_entry"
        )

        # Contact person
        self.create_field(
            form_frame, "Contact Person",
            "Enter contact person", 0, 1, "contact_entry"
        )

        # Phone
        self.create_field(
            form_frame, "Phone Number",
            "Enter phone number", 0, 2, "phone_entry"
        )

        # Email
        self.create_field(
            form_frame, "Email Address",
            "Enter email address", 2, 0, "email_entry"
        )

        # Address
        ctk.CTkLabel(
            form_frame,
            text="Address",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(
            row=2, column=1,
            padx=15, pady=(8, 5), sticky="w"
        )

        self.address_entry = ctk.CTkEntry(
            form_frame,
            height=38,
            placeholder_text="Enter supplier address"
        )
        self.address_entry.grid(
            row=3, column=1, columnspan=2,
            padx=15, pady=(0, 18), sticky="ew"
        )

        # Action buttons
        button_frame = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        button_frame.pack(pady=10)

        buttons = [
            ("➕ Add Supplier", self.add_supplier),
            ("✏️ Update", self.update_supplier),
            ("🗑️ Delete", self.delete_supplier),
            ("Clear", self.clear_form),
            ("🔄 Refresh", self.load_suppliers),
        ]

        for column, (text, command) in enumerate(buttons):
            ctk.CTkButton(
                button_frame,
                text=text,
                width=135,
                height=36,
                command=command
            ).grid(row=0, column=column, padx=5, pady=4)

        # Search
        search_frame = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        search_frame.pack(
            fill="x", padx=30, pady=(10, 5)
        )

        ctk.CTkLabel(
            search_frame,
            text="Search Supplier:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            height=36,
            placeholder_text="Search by name, contact or phone"
        )
        self.search_entry.pack(side="left")

        ctk.CTkButton(
            search_frame,
            text="🔍 Search",
            width=105,
            command=self.search_suppliers
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            search_frame,
            text="Show All",
            width=100,
            fg_color="gray",
            hover_color="gray30",
            command=self.reset_search
        ).pack(side="left", padx=4)

        # Supplier table
        table_frame = ctk.CTkFrame(self, corner_radius=12)
        table_frame.pack(
            fill="both", expand=True,
            padx=30, pady=10
        )

        columns = (
            "id", "name", "contact",
            "phone", "email", "address"
        )

        self.supplier_tree = styled_treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": ("ID", 60, "center"),
            "name": ("Supplier Name", 180, "w"),
            "contact": ("Contact Person", 170, "w"),
            "phone": ("Phone", 140, "center"),
            "email": ("Email", 210, "w"),
            "address": ("Address", 280, "w"),
        }

        for column, (heading, width, anchor) in headings.items():
            self.supplier_tree.heading(
                column, text=heading
            )
            self.supplier_tree.column(
                column, width=width, anchor=anchor
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
            expand=True,
            padx=(8, 0),
            pady=8
        )

        scrollbar.pack(
            side="right",
            fill="y",
            padx=(0, 8),
            pady=8
        )

        self.supplier_tree.bind(
            "<<TreeviewSelect>>",
            self.select_supplier
        )

        # Back to dashboard
        ctk.CTkButton(
            self,
            text="← Back to Dashboard",
            width=180,
            command=self.back_callback
        ).pack(pady=(5, 15))

    def create_field(
        self, parent, label_text, placeholder,
        row, column, attribute
    ):
        ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(
            row=row, column=column,
            padx=15, pady=(15, 5), sticky="w"
        )

        entry = ctk.CTkEntry(
            parent,
            height=38,
            placeholder_text=placeholder
        )
        entry.grid(
            row=row + 1, column=column,
            padx=15, pady=(0, 10), sticky="ew"
        )

        setattr(self, attribute, entry)

    # ==========================================
    # VALIDATION
    # ==========================================

    def get_form_data(self):
        name = self.name_entry.get().strip()
        contact = self.contact_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name:
            messagebox.showwarning(
                "Required Field",
                "Please enter the supplier name."
            )
            self.name_entry.focus()
            return None

        if phone:
            digits = re.sub(r"\D", "", phone)

            if not 7 <= len(digits) <= 15:
                messagebox.showwarning(
                    "Invalid Phone",
                    "Please enter a valid phone number."
                )
                self.phone_entry.focus()
                return None

        if email and not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+", email
        ):
            messagebox.showwarning(
                "Invalid Email",
                "Please enter a valid email address."
            )
            self.email_entry.focus()
            return None

        return name, contact, phone, email, address

    # ==========================================
    # LOAD AND DISPLAY SUPPLIERS
    # ==========================================

    def load_suppliers(self):
        self.display_suppliers()

    def display_suppliers(self, search_text=""):
        try:
            with get_connection() as connection:
                if search_text:
                    pattern = f"%{search_text}%"

                    suppliers = connection.execute("""
                        SELECT
                            supplier_id, name, contact_person,
                            phone, email, address
                        FROM suppliers
                        WHERE name LIKE ?
                           OR contact_person LIKE ?
                           OR phone LIKE ?
                           OR email LIKE ?
                        ORDER BY supplier_id DESC
                    """, (
                        pattern, pattern, pattern, pattern
                    )).fetchall()

                else:
                    suppliers = connection.execute("""
                        SELECT
                            supplier_id, name, contact_person,
                            phone, email, address
                        FROM suppliers
                        ORDER BY supplier_id DESC
                    """).fetchall()

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
        data = self.get_form_data()

        if data is None:
            return

        try:
            with get_connection() as connection:
                connection.execute("""
                    INSERT INTO suppliers (
                        name, contact_person, phone, email, address
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, data)

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

        values = self.supplier_tree.item(
            selected[0], "values"
        )

        if not values:
            return

        self.selected_supplier_id = int(values[0])

        entries = [
            (self.name_entry, values[1]),
            (self.contact_entry, values[2]),
            (self.phone_entry, values[3]),
            (self.email_entry, values[4]),
            (self.address_entry, values[5]),
        ]

        for entry, value in entries:
            entry.delete(0, "end")
            entry.insert(0, value or "")

    # ==========================================
    # UPDATE SUPPLIER
    # ==========================================

    def update_supplier(self):
        if self.selected_supplier_id is None:
            messagebox.showwarning(
                "Select Supplier",
                "Please select a supplier from the table first."
            )
            return

        data = self.get_form_data()

        if data is None:
            return

        try:
            with get_connection() as connection:
                cursor = connection.execute("""
                    UPDATE suppliers
                    SET
                        name = ?,
                        contact_person = ?,
                        phone = ?,
                        email = ?,
                        address = ?
                    WHERE supplier_id = ?
                """, (*data, self.selected_supplier_id))

                if cursor.rowcount == 0:
                    messagebox.showwarning(
                        "Not Found",
                        "This supplier no longer exists."
                    )
                    self.clear_form()
                    self.load_suppliers()
                    return

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
        if self.selected_supplier_id is None:
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
            with get_connection() as connection:
                cursor = connection.execute("""
                    DELETE FROM suppliers
                    WHERE supplier_id = ?
                """, (self.selected_supplier_id,))

                if cursor.rowcount == 0:
                    messagebox.showwarning(
                        "Not Found",
                        "Supplier was not found."
                    )
                    self.clear_form()
                    self.load_suppliers()
                    return

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
    # SEARCH
    # ==========================================

    def search_suppliers(self):
        search_text = self.search_entry.get().strip()
        self.display_suppliers(search_text)

    def reset_search(self):
        self.search_entry.delete(0, "end")
        self.load_suppliers()

    # ==========================================
    # CLEAR FORM
    # ==========================================

    def clear_form(self):
        self.selected_supplier_id = None

        for entry in (
            self.name_entry,
            self.contact_entry,
            self.phone_entry,
            self.email_entry,
            self.address_entry
        ):
            entry.delete(0, "end")

        for item in self.supplier_tree.selection():
            self.supplier_tree.selection_remove(item)

        self.name_entry.focus()