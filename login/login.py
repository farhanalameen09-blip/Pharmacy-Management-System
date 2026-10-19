import customtkinter as ctk  # type: ignore
import hashlib
import sqlite3

from tkinter import messagebox

from database import get_connection
from config import Colors


class LoginFrame(ctk.CTkFrame):

    def __init__(self, parent, login_success):
        super().__init__(parent, fg_color="transparent")

        self.parent = parent
        self.login_success = login_success
        self.login_in_progress = False

        self.create_ui()

    # ==========================================
    # CREATE LOGIN UI
    # ==========================================

    def create_ui(self):
        self.container = ctk.CTkFrame(
            self,
            corner_radius=20,
            fg_color=Colors.SURFACE,
            border_width=1,
            border_color=Colors.BORDER
        )

        self.container.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            relwidth=0.70,
            relheight=0.90
        )

        ctk.CTkLabel(
            self.container,
            text="💊 Pharmacy Management System",
            text_color=Colors.PRIMARY,
            font=ctk.CTkFont(size=26, weight="bold")
        ).pack(pady=(30, 5))

        ctk.CTkLabel(
            self.container,
            text="Sign in to continue",
            text_color=Colors.TEXT_MUTED,
            font=ctk.CTkFont(size=14)
        ).pack(pady=(0, 25))

        ctk.CTkLabel(
            self.container,
            text="Username",
            anchor="w"
        ).pack(fill="x", padx=40)

        self.username_entry = ctk.CTkEntry(
            self.container,
            placeholder_text="Enter username",
            height=42
        )
        self.username_entry.pack(
            fill="x",
            padx=40,
            pady=(5, 15)
        )

        ctk.CTkLabel(
            self.container,
            text="Password",
            anchor="w"
        ).pack(fill="x", padx=40)

        self.password_entry = ctk.CTkEntry(
            self.container,
            placeholder_text="Enter password",
            show="*",
            height=42
        )
        self.password_entry.pack(
            fill="x",
            padx=40,
            pady=(5, 5)
        )

        self.show_password_var = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(
            self.container,
            text="Show Password",
            variable=self.show_password_var,
            command=self.toggle_password
        ).pack(
            anchor="w",
            padx=40,
            pady=5
        )

        self.remember_var = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(
            self.container,
            text="Remember Username",
            variable=self.remember_var
        ).pack(
            anchor="w",
            padx=40,
            pady=5
        )

        self.message = ctk.CTkLabel(
            self.container,
            text="",
            text_color=Colors.TEXT_MUTED,
            font=ctk.CTkFont(size=13)
        )
        self.message.pack(pady=10)

        self.login_button = ctk.CTkButton(
            self.container,
            text="Login",
            height=42,
            command=self.login
        )
        self.login_button.pack(
            fill="x",
            padx=40,
            pady=5
        )

        ctk.CTkButton(
            self.container,
            text="Clear",
            height=42,
            fg_color="gray",
            hover_color="darkgray",
            command=self.clear
        ).pack(
            fill="x",
            padx=40,
            pady=(5, 25)
        )

        self.username_entry.bind(
            "<Return>",
            lambda event: self.focus_password()
        )

        self.password_entry.bind(
            "<Return>",
            lambda event: self.login()
        )

        self.username_entry.focus_set()

    # ==========================================
    # PASSWORD VISIBILITY
    # ==========================================

    def toggle_password(self):
        self.password_entry.configure(
            show="" if self.show_password_var.get() else "*"
        )

    # ==========================================
    # FIELD FOCUS
    # ==========================================

    def focus_password(self):
        self.password_entry.focus_set()

    # ==========================================
    # CLEAR FIELDS
    # ==========================================

    def clear(self):
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")

        self.message.configure(text="")

        self.login_in_progress = False
        self.login_button.configure(
            state="normal",
            text="Login"
        )

        self.username_entry.focus_set()

    # ==========================================
    # PASSWORD HASHING
    # ==========================================

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest()

    # ==========================================
    # LOGIN
    # ==========================================

    def login(self):
        if self.login_in_progress:
            return

        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username:
            self.message.configure(
                text="Please enter your username."
            )
            self.username_entry.focus_set()
            return

        if not password:
            self.message.configure(
                text="Please enter your password."
            )
            self.password_entry.focus_set()
            return

        self.login_in_progress = True

        self.login_button.configure(
            state="disabled",
            text="Signing in..."
        )

        self.message.configure(text="")

        try:
            hashed_password = self.hash_password(password)

            with get_connection() as connection:
                connection.row_factory = sqlite3.Row

                user = connection.execute(
                    """
                    SELECT user_id, username, role
                    FROM users
                    WHERE username = ?
                      AND password = ?
                    """,
                    (username, hashed_password)
                ).fetchone()

            if user is None:
                self.message.configure(
                    text="Incorrect username or password."
                )

                self.password_entry.delete(0, "end")
                self.password_entry.focus_set()

                self.login_in_progress = False

                self.login_button.configure(
                    state="normal",
                    text="Login"
                )
                return

            user_data = dict(user)

            print(
                f"Login successful: "
                f"{user_data['username']} "
                f"({user_data['role']})"
            )

            # Preserve compatibility with the application's callback.
            self.login_success(user_data)

        except sqlite3.Error as error:
            print(f"Login database error: {error}")

            self.message.configure(
                text="Database error. Please try again."
            )

            self.login_in_progress = False

            self.login_button.configure(
                state="normal",
                text="Login"
            )

        except Exception as error:
            print(f"Login error: {error}")

            self.message.configure(
                text="Unable to process login. Check terminal."
            )

            self.login_in_progress = False

            self.login_button.configure(
                state="normal",
                text="Login"
            )