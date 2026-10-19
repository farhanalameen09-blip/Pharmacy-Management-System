import re
import customtkinter as ctk  # type: ignore
from tkinter import ttk, messagebox

from ui_kit import styled_treeview
from database import get_connection


class CustomerPage(ctk.CTkFrame):

    def __init__(self, parent, back_callback):
        super().__init__(parent, fg_color="transparent")

        self.back_callback = back_callback
        self.selected_customer_id = None

        self.create_database_table()
        self.create_ui()
        self.load_customers()

    # ==========================================
    # DATABASE
    # ==========================================

    def create_database_table(self):
        try:
            with get_connection() as connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS customers (
                        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone TEXT,
                        email TEXT,
                        address TEXT
                    )
                """)
        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Unable to initialize customers table.\n\n{error}"
            )

    # ==========================================
    # UI
    # ==========================================

    def create_ui(self):
        title = ctk.CTkLabel(
            self,
            text="👥 Customer Management",
            font=ctk.CTkFont(size=30, weight="bold")
        )
        title.pack(pady=(20, 8))

        subtitle = ctk.CTkLabel(
            self,
            text="Add, update, search and manage pharmacy customers",
            font=ctk.CTkFont(size=14)
        )
        subtitle.pack(pady=(0, 18))

        # Customer form
        form_frame = ctk.CTkFrame(self, corner_radius=12)
        form_frame.pack(fill="x", padx=30, pady=8)

        form_frame.grid_columnconfigure(
            (0, 1, 2), weight=1
        )

        # Customer name
        self.create_field(
            form_frame, "Customer Name", "Enter customer name",
            row=0, column=0, width=250, attribute="name_entry"
        )

        # Phone
        self.create_field(
            form_frame, "Phone Number", "Enter phone number",
            row=0, column=1, width=220, attribute="phone_entry"
        )

        # Email
        self.create_field(
            form_frame, "Email Address", "Enter email address",
            row=0, column=2, width=250, attribute="email_entry"
        )

        # Address
        address_label = ctk.CTkLabel(
            form_frame,
            text="Address",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        address_label.grid(
            row=2, column=0,
            padx=15, pady=(8, 5), sticky="w"
        )

        self.address_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter customer address",
            height=38
        )
        self.address_entry.grid(
            row=3, column=0, columnspan=3,
            padx=15, pady=(0, 18), sticky="ew"
        )

        # Buttons
        button_frame = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        button_frame.pack(pady=10)

        buttons = [
            ("➕ Add Customer", self.add_customer),
            ("✏️ Update", self.update_customer),
            ("🗑️ Delete", self.delete_customer),
            ("Clear", self.clear_form),
            ("🔄 Refresh", self.load_customers),
        ]

        for column, (text, command) in enumerate(buttons):
            ctk.CTkButton(
                button_frame,
                text=text,
                width=135,
                height=36,
                command=command
            ).grid(
                row=0, column=column, padx=5, pady=4
            )

        # Search
        search_frame = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        search_frame.pack(
            fill="x", padx=30, pady=(8, 5)
        )

        ctk.CTkLabel(
            search_frame,
            text="Search Customer:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            height=36,
            placeholder_text="Search by name or phone"
        )
        self.search_entry.pack(side="left")

        ctk.CTkButton(
            search_frame,
            text="🔍 Search",
            width=105,
            command=self.search_customers
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            search_frame,
            text="Show All",
            width=100,
            fg_color="gray",
            hover_color="gray30",
            command=self.reset_search
        ).pack(side="left", padx=4)

        # Customer table
        table_frame = ctk.CTkFrame(self, corner_radius=12)
        table_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        columns = (
            "id", "name", "phone", "email", "address"
        )

        self.customer_tree = styled_treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": ("ID", 60, "center"),
            "name": ("Customer Name", 200, "w"),
            "phone": ("Phone", 140, "center"),
            "email": ("Email", 220, "w"),
            "address": ("Address", 300, "w"),
        }

        for column, (heading, width, anchor) in headings.items():
            self.customer_tree.heading(
                column, text=heading
            )
            self.customer_tree.column(
                column, width=width, anchor=anchor
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.customer_tree.yview
        )

        self.customer_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.customer_tree.pack(
            side="left", fill="both", expand=True,
            padx=(8, 0), pady=8
        )
        scrollbar.pack(
            side="right", fill="y", padx=(0, 8), pady=8
        )

        self.customer_tree.bind(
            "<<TreeviewSelect>>", self.select_customer
        )

        # Back button
        ctk.CTkButton(
            self,
            text="← Back to Dashboard",
            width=180,
            command=self.back_callback
        ).pack(pady=(3, 15))

    def create_field(
        self, parent, label_text, placeholder,
        row, column, width, attribute
    ):
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        label.grid(
            row=row, column=column,
            padx=15, pady=(15, 5), sticky="w"
        )

        entry = ctk.CTkEntry(
            parent,
            width=width,
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
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name:
            messagebox.showwarning(
                "Required Field",
                "Please enter the customer's name."
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

        return name, phone, email, address

    # ==========================================
    # LOAD CUSTOMERS
    # ==========================================

    def load_customers(self):
        self.display_customers()

    def display_customers(self, search_text=""):
        try:
            with get_connection() as connection:
                if search_text:
                    pattern = f"%{search_text}%"

                    customers = connection.execute("""
                        SELECT customer_id, name, phone, email, address
                        FROM customers
                        WHERE name LIKE ?
                           OR phone LIKE ?
                        ORDER BY customer_id DESC
                    """, (pattern, pattern)).fetchall()
                else:
                    customers = connection.execute("""
                        SELECT customer_id, name, phone, email, address
                        FROM customers
                        ORDER BY customer_id DESC
                    """).fetchall()

            self.customer_tree.delete(
                *self.customer_tree.get_children()
            )

            for customer in customers:
                self.customer_tree.insert(
                    "",
                    "end",
                    values=(
                        customer["customer_id"],
                        customer["name"],
                        customer["phone"] or "",
                        customer["email"] or "",
                        customer["address"] or ""
                    )
                )

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Unable to load customers.\n\n{error}"
            )

    # ==========================================
    # ADD CUSTOMER
    # ==========================================

    def add_customer(self):
        data = self.get_form_data()

        if data is None:
            return

        try:
            with get_connection() as connection:
                connection.execute("""
                    INSERT INTO customers
                        (name, phone, email, address)
                    VALUES (?, ?, ?, ?)
                """, data)

            messagebox.showinfo(
                "Success",
                "Customer added successfully."
            )

            self.clear_form()
            self.load_customers()

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"Unable to add customer.\n\n{error}"
            )

    # ==========================================
    # SELECT CUSTOMER
    # ==========================================

    def select_customer(self, event=None):
        selected = self.customer_tree.selection()

        if not selected:
            return

        values = self.customer_tree.item(
            selected[0], "values"
        )

        if not values:
            return

        self.selected_customer_id = int(values[0])

        entries = [
            (self.name_entry, values[1]),
            (self.phone_entry, values[2]),
            (self.email_entry, values[3]),
            (self.address_entry, values[4]),
        ]

        for entry, value in entries:
            entry.delete(0, "end")
            entry.insert(0, value or "")

    # ==========================================
    # UPDATE CUSTOMER
    # ==========================================

    def update_customer(self):
        if self.selected_customer_id is None:
            messagebox.showwarning(
                "Select Customer",
                "Select a customer from the table first."
            )
            return

        data = self.get_form_data()

        if data is None:
            return

        try:
            with get_connection() as connection:
                cursor = connection.execute("""
                    UPDATE customers
                    SET name = ?, phone = ?, email = ?, address = ?
                    WHERE customer_id = ?
                """, (*data, self.selected_customer_id))

                if cursor.rowcount == 0:
                    messagebox.showwarning(
                        "Not Found",
                        "This customer no longer exists."
                    )
                    self.clear_form()
                    self.load_customers()
                    return

            messagebox.showinfo(
                "Success",
                "Customer updated successfully."
            )

            self.clear_form()
            self.load_customers()

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"Unable to update customer.\n\n{error}"
            )

    # ==========================================
    # DELETE CUSTOMER
    # ==========================================

    def delete_customer(self):
        if self.selected_customer_id is None:
            messagebox.showwarning(
                "Select Customer",
                "Select a customer from the table first."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this customer?"
        )

        if not confirm:
            return

        try:
            with get_connection() as connection:
                cursor = connection.execute("""
                    DELETE FROM customers
                    WHERE customer_id = ?
                """, (self.selected_customer_id,))

                if cursor.rowcount == 0:
                    messagebox.showwarning(
                        "Not Found",
                        "Customer was not found."
                    )

            self.clear_form()
            self.load_customers()

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"Unable to delete customer.\n\n{error}"
            )
            return

        messagebox.showinfo(
            "Success",
            "Customer deleted successfully."
        )

    # ==========================================
    # SEARCH CUSTOMERS
    # ==========================================

    def search_customers(self):
        search_text = self.search_entry.get().strip()
        self.display_customers(search_text)

    def reset_search(self):
        self.search_entry.delete(0, "end")
        self.load_customers()

    # ==========================================
    # CLEAR FORM
    # ==========================================

    def clear_form(self):
        self.selected_customer_id = None

        for entry in (
            self.name_entry,
            self.phone_entry,
            self.email_entry,
            self.address_entry
        ):
            entry.delete(0, "end")

        for item in self.customer_tree.selection():
            self.customer_tree.selection_remove(item)

        self.name_entry.focus()