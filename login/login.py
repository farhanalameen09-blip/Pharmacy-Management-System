import customtkinter as ctk # type: ignore

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
            relwidth=0.42,
            relheight=0.72
        )

        # TITLE
        title = ctk.CTkLabel(
            container,
            text="💊 Pharmacy Management System",
            text_color=Colors.PRIMARY,
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        )

        title.pack(
            pady=(40, 5)
        )

        # QUALITY GOAL
        quality = ctk.CTkLabel(
            container,
            text="Sign in to continue",
            text_color=Colors.TEXT_MUTED,
            font=ctk.CTkFont(size=14)
        )

        quality.pack(
            pady=(0, 30)
        )

        # USERNAME
        username_label = ctk.CTkLabel(
            container,
            text="Username",
            anchor="w"
        )

        username_label.pack(
            fill="x",
            padx=50
        )

        self.username_entry = ctk.CTkEntry(
            container,
            placeholder_text="Enter username",
            height=40
        )

        self.username_entry.pack(
            fill="x",
            padx=50,
            pady=(5, 15)
        )

        # PASSWORD
        password_label = ctk.CTkLabel(
            container,
            text="Password",
            anchor="w"
        )

        password_label.pack(
            fill="x",
            padx=50
        )

        self.password_entry = ctk.CTkEntry(
            container,
            placeholder_text="Enter password",
            show="*",
            height=40
        )

        self.password_entry.pack(
            fill="x",
            padx=50,
            pady=(5, 5)
        )

        # SHOW PASSWORD
        self.show_password_var = ctk.BooleanVar(
            value=False
        )

        show_password = ctk.CTkCheckBox(
            container,
            text="Show Password",
            variable=self.show_password_var,
            command=self.toggle_password
        )

        show_password.pack(
            anchor="w",
            padx=50,
            pady=5
        )

        # REMEMBER USERNAME
        self.remember_var = ctk.BooleanVar(
            value=False
        )

        remember = ctk.CTkCheckBox(
            container,
            text="Remember Username",
            variable=self.remember_var
        )

        remember.pack(
            anchor="w",
            padx=50,
            pady=5
        )

        # MESSAGE
        self.message = ctk.CTkLabel(
            container,
            text="",
            font=ctk.CTkFont(size=13)
        )

        self.message.pack(
            pady=10
        )

        # LOGIN BUTTON
        login_button = ctk.CTkButton(
            container,
            text="Login",
            height=42,
            command=self.login
        )

        login_button.pack(
            fill="x",
            padx=50,
            pady=5
        )

        # CLEAR BUTTON
        clear_button = ctk.CTkButton(
            container,
            text="Clear",
            height=42,
            fg_color="gray",
            hover_color="darkgray",
            command=self.clear
        )

        clear_button.pack(
            fill="x",
            padx=50,
            pady=5
        )

        # ENTER KEY
        self.password_entry.bind(
            "<Return>",
            lambda event: self.login()
        )

        self.username_entry.focus()

    # ==========================================
    # SHOW / HIDE PASSWORD
    # ==========================================

    def toggle_password(self):

        if self.show_password_var.get():

            self.password_entry.configure(
                show=""
            )

        else:

            self.password_entry.configure(
                show="*"
            )

    # ==========================================
    # CLEAR
    # ==========================================

    def clear(self):

        self.username_entry.delete(
            0,
            "end"
        )

        self.password_entry.delete(
            0,
            "end"
        )

        self.message.configure(
            text=""
        )

        self.username_entry.focus()

    # ==========================================
    # HASH PASSWORD
    # ==========================================

    def hash_password(self, password):

        return hashlib.sha256(
            password.encode()
        ).hexdigest()

    # ==========================================
    # LOGIN
    # ==========================================

    def login(self):

        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        # CHECK USERNAME
        if not username:

            self.message.configure(
                text="Please enter your username."
            )

            self.username_entry.focus()

            return

        # CHECK PASSWORD
        if not password:

            self.message.configure(
                text="Please enter your password."
            )

            self.password_entry.focus()

            return

        hashed_password = self.hash_password(
            password
        )

        connection = None

        try:

            connection = get_connection()

            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT user_id, username, role
                FROM users
                WHERE username = ?
                AND password = ?
                """,
                (
                    username,
                    hashed_password
                )
            )

            user = cursor.fetchone()

            if user:

                # ==================================
                # LOGIN SUCCESS
                # ==================================

                user_data = dict(user)

                logged_username = user_data["username"]
                logged_role = user_data["role"]

                print(
                    f"Login successful: {logged_username} ({logged_role})"
                )

                # IMPORTANT:
                # main.py expects username AND role
                self.login_success(
                    logged_username,
                    logged_role
                )

            else:

                self.message.configure(
                    text="Incorrect username or password."
                )

                self.password_entry.delete(
                    0,
                    "end"
                )

                self.password_entry.focus()

        except Exception as error:

            print(
                "Login error:",
                error
            )

            self.message.configure(
                text="Unable to process login."
            )

        finally:

            if connection:

                connection.close()