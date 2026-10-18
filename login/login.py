import customtkinter as ctk  # type: ignore
import hashlib

from database import get_connection
from config import Colors


class LoginFrame(ctk.CTkFrame):

    def __init__(self, parent, login_success):
        super().__init__(parent, fg_color="transparent")

        self.parent = parent
        self.login_success = login_success

        self.create_ui()

    # ==========================================
    # CREATE LOGIN UI
    # ==========================================

    def create_ui(self):
        container = ctk.CTkFrame(
            self,
            corner_radius=20,
            fg_color=Colors.SURFACE,
            border_width=1,
            border_color=Colors.BORDER
        )

        container.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            relwidth=0.60,
            relheight=0.90
        )

        title = ctk.CTkLabel(
            container,
            text="💊 Pharmacy Management System",
            text_color=Colors.PRIMARY,
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(30, 5))

        quality = ctk.CTkLabel(
            container,
            text="Sign in to continue",
            text_color=Colors.TEXT_MUTED,
            font=ctk.CTkFont(size=14)
        )
        quality.pack(pady=(0, 25))

        ctk.CTkLabel(
            container,
            text="Username",
            anchor="w"
        ).pack(fill="x", padx=40)

        self.username_entry = ctk.CTkEntry(
            container,
            placeholder_text="Enter username",
            height=40
        )
        self.username_entry.pack(
            fill="x", padx=40, pady=(5, 15)
        )

        ctk.CTkLabel(
            container,
            text="Password",
            anchor="w"
        ).pack(fill="x", padx=40)

        self.password_entry = ctk.CTkEntry(
            container,
            placeholder_text="Enter password",
            show="*",
            height=40
        )
        self.password_entry.pack(
            fill="x", padx=40, pady=(5, 5)
        )

        self.show_password_var = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(
            container,
            text="Show Password",
            variable=self.show_password_var,
            command=self.toggle_password
        ).pack(anchor="w", padx=40, pady=5)

        self.remember_var = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(
            container,
            text="Remember Username",
            variable=self.remember_var
        ).pack(anchor="w", padx=40, pady=5)

        self.message = ctk.CTkLabel(
            container,
            text="",
            font=ctk.CTkFont(size=13)
        )
        self.message.pack(pady=10)

        ctk.CTkButton(
            container,
            text="Login",
            height=42,
            command=self.login
        ).pack(fill="x", padx=40, pady=5)

        ctk.CTkButton(
            container,
            text="Clear",
            height=42,
            fg_color="gray",
            hover_color="darkgray",
            command=self.clear
        ).pack(fill="x", padx=40, pady=(5, 25))

        self.password_entry.bind(
            "<Return>",
            lambda event: self.login()
        )

        self.username_entry.focus()

    # ==========================================
    # SHOW / HIDE PASSWORD
    # ==========================================

    def toggle_password(self):
        self.password_entry.configure(
            show="" if self.show_password_var.get() else "*"
        )

    # ==========================================
    # CLEAR
    # ==========================================

    def clear(self):
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.message.configure(text="")
        self.username_entry.focus()

    # ==========================================
    # HASH PASSWORD
    # ==========================================

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    # ==========================================
    # LOGIN
    # ==========================================

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username:
            self.message.configure(
                text="Please enter your username."
            )
            self.username_entry.focus()
            return

        if not password:
            self.message.configure(
                text="Please enter your password."
            )
            self.password_entry.focus()
            return

        try:
            hashed_password = self.hash_password(password)

            with get_connection() as connection:
                connection.row_factory = __import__("sqlite3").Row

                user = connection.execute(
                    """
                    SELECT user_id, username, role
                    FROM users
                    WHERE username = ? AND password = ?
                    """,
                    (username, hashed_password)
                ).fetchone()

            if user:
                user_data = dict(user)

                print(
                    f"Login successful: "
                    f"{user_data['username']} ({user_data['role']})"
                )

                # Pass the user information to the main application.
                self.login_success(user_data)

            else:
                self.message.configure(
                    text="Incorrect username or password."
                )
                self.password_entry.delete(0, "end")
                self.password_entry.focus()

        except Exception as error:
            print(f"Login error: {error}")

            self.message.configure(
                text="Unable to process login. Check terminal."
            )