import customtkinter as ctk # type: ignore
from ui_kit import styled_treeview
from tkinter import ttk, messagebox

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

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (

                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

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

        # Main title
        title = ctk.CTkLabel(
            self,
            text="👥 Customer Management",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        )

        title.pack(
            pady=(20, 10)
        )

        # Subtitle
        subtitle = ctk.CTkLabel(
            self,
            text="Add, update, search and manage pharmacy customers",
            font=ctk.CTkFont(size=15)
        )

        subtitle.pack(
            pady=(0, 20)
        )

        # ==========================================
        # FORM FRAME
        # ==========================================

        form_frame = ctk.CTkFrame(self)

        form_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )

        # Customer Name
        name_label = ctk.CTkLabel(
            form_frame,
            text="Customer Name"
        )

        name_label.grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 5),
            sticky="w"
        )

        self.name_entry = ctk.CTkEntry(
            form_frame,
            width=250,
            placeholder_text="Enter customer name"
        )

        self.name_entry.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15)
        )

        # Phone
        phone_label = ctk.CTkLabel(
            form_frame,
            text="Phone"
        )

        phone_label.grid(
            row=0,
            column=1,
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
            column=1,
            padx=15,
            pady=(0, 15)
        )

        # Email
        email_label = ctk.CTkLabel(
            form_frame,
            text="Email"
        )

        email_label.grid(
            row=0,
            column=2,
            padx=15,
            pady=(15, 5),
            sticky="w"
        )

        self.email_entry = ctk.CTkEntry(
            form_frame,
            width=230,
            placeholder_text="Enter email"
        )

        self.email_entry.grid(
            row=1,
            column=2,
            padx=15,
            pady=(0, 15)
        )

        # Address
        address_label = ctk.CTkLabel(
            form_frame,
            text="Address"
        )

        address_label.grid(
            row=2,
            column=0,
            padx=15,
            pady=(5, 5),
            sticky="w"
        )

        self.address_entry = ctk.CTkEntry(
            form_frame,
            width=680,
            placeholder_text="Enter address"
        )

        self.address_entry.grid(
            row=3,
            column=0,
            columnspan=3,
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

        button_frame.pack(
            pady=10
        )

        add_button = ctk.CTkButton(
            button_frame,
            text="➕ Add Customer",
            width=140,
            command=self.add_customer
        )

        add_button.grid(
            row=0,
            column=0,
            padx=5
        )

        update_button = ctk.CTkButton(
            button_frame,
            text="✏️ Update",
            width=120,
            command=self.update_customer
        )

        update_button.grid(
            row=0,
            column=1,
            padx=5
        )

        delete_button = ctk.CTkButton(
            button_frame,
            text="🗑️ Delete",
            width=120,
            command=self.delete_customer
        )

        delete_button.grid(
            row=0,
            column=2,
            padx=5
        )

        clear_button = ctk.CTkButton(
            button_frame,
            text="Clear",
            width=100,
            command=self.clear_form
        )

        clear_button.grid(
            row=0,
            column=3,
            padx=5
        )

        refresh_button = ctk.CTkButton(
            button_frame,
            text="🔄 Refresh",
            width=120,
            command=self.load_customers
        )

        refresh_button.grid(
            row=0,
            column=4,
            padx=5
        )

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

        search_label = ctk.CTkLabel(
            search_frame,
            text="Search Customer:"
        )

        search_label.pack(
            side="left",
            padx=(0, 10)
        )

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            placeholder_text="Search by name or phone"
        )

        self.search_entry.pack(
            side="left"
        )

        search_button = ctk.CTkButton(
            search_frame,
            text="🔍 Search",
            width=100,
            command=self.search_customers
        )

        search_button.pack(
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
            "phone",
            "email",
            "address"
        )

        self.customer_tree = styled_treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.customer_tree.heading(
            "id",
            text="ID"
        )

        self.customer_tree.heading(
            "name",
            text="Customer Name"
        )

        self.customer_tree.heading(
            "phone",
            text="Phone"
        )

        self.customer_tree.heading(
            "email",
            text="Email"
        )

        self.customer_tree.heading(
            "address",
            text="Address"
        )

        self.customer_tree.column(
            "id",
            width=60,
            anchor="center"
        )

        self.customer_tree.column(
            "name",
            width=200
        )

        self.customer_tree.column(
            "phone",
            width=140
        )

        self.customer_tree.column(
            "email",
            width=220
        )

        self.customer_tree.column(
            "address",
            width=300
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
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.customer_tree.bind(
            "<ButtonRelease-1>",
            self.select_customer
        )

        # ==========================================
        # BACK BUTTON
        # ==========================================

        back_button = ctk.CTkButton(
            self,
            text="← Back to Dashboard",
            width=180,
            command=self.back_callback
        )

        back_button.pack(
            pady=(5, 15)
        )

    # ==========================================
    # LOAD CUSTOMERS
    # ==========================================

    def load_customers(self):

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    customer_id,
                    name,
                    phone,
                    email,
                    address
                FROM customers
                ORDER BY customer_id DESC
            """)

            customers = cursor.fetchall()

            connection.close()

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

        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name:

            messagebox.showwarning(
                "Required",
                "Please enter customer name."
            )

            return

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO customers
                (
                    name,
                    phone,
                    email,
                    address
                )
                VALUES (?, ?, ?, ?)
            """, (
                name,
                phone,
                email,
                address
            ))

            connection.commit()
            connection.close()

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

        item = self.customer_tree.item(
            selected[0]
        )

        values = item["values"]

        if not values:
            return

        self.selected_customer_id = values[0]

        self.name_entry.delete(0, "end")
        self.name_entry.insert(
            0,
            values[1]
        )

        self.phone_entry.delete(0, "end")
        self.phone_entry.insert(
            0,
            values[2]
        )

        self.email_entry.delete(0, "end")
        self.email_entry.insert(
            0,
            values[3]
        )

        self.address_entry.delete(0, "end")
        self.address_entry.insert(
            0,
            values[4]
        )

    # ==========================================
    # UPDATE CUSTOMER
    # ==========================================

    def update_customer(self):

        if not self.selected_customer_id:

            messagebox.showwarning(
                "Select Customer",
                "Please select a customer from the table first."
            )

            return

        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name:

            messagebox.showwarning(
                "Required",
                "Customer name cannot be empty."
            )

            return

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE customers
                SET
                    name = ?,
                    phone = ?,
                    email = ?,
                    address = ?
                WHERE customer_id = ?
            """, (
                name,
                phone,
                email,
                address,
                self.selected_customer_id
            ))

            connection.commit()
            connection.close()

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

        if not self.selected_customer_id:

            messagebox.showwarning(
                "Select Customer",
                "Please select a customer from the table first."
            )

            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this customer?"
        )

        if not confirm:
            return

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                DELETE FROM customers
                WHERE customer_id = ?
            """, (
                self.selected_customer_id,
            ))

            connection.commit()
            connection.close()

            messagebox.showinfo(
                "Success",
                "Customer deleted successfully."
            )

            self.clear_form()
            self.load_customers()

        except Exception as error:

            messagebox.showerror(
                "Error",
                f"Unable to delete customer.\n\n{error}"
            )

    # ==========================================
    # SEARCH CUSTOMERS
    # ==========================================

    def search_customers(self):

        search_text = self.search_entry.get().strip()

        if not search_text:

            self.load_customers()
            return

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    customer_id,
                    name,
                    phone,
                    email,
                    address
                FROM customers
                WHERE name LIKE ?
                   OR phone LIKE ?
                ORDER BY customer_id DESC
            """, (
                f"%{search_text}%",
                f"%{search_text}%"
            ))

            customers = cursor.fetchall()

            connection.close()

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
                "Search Error",
                f"Unable to search customers.\n\n{error}"
            )

    # ==========================================
    # CLEAR FORM
    # ==========================================

    def clear_form(self):

        self.selected_customer_id = None

        self.name_entry.delete(
            0,
            "end"
        )

        self.phone_entry.delete(
            0,
            "end"
        )

        self.email_entry.delete(
            0,
            "end"
        )

        self.address_entry.delete(
            0,
            "end"
        )

        for item in self.customer_tree.selection():

            self.customer_tree.selection_remove(
                item
            )