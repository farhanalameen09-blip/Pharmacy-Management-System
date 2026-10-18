import customtkinter as ctk  # type: ignore

from tkinter import messagebox
import hashlib

from database import get_connection


class SettingsPage(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        dashboard_callback,
        user_id=None,
        username="",
        role="User",
        logout_callback=None
    ):
        super().__init__(parent, fg_color="transparent")

        self.dashboard_callback = dashboard_callback
        self.user_id = user_id
        self.username = username
        self.role = role
        self.logout_callback = logout_callback

        self.create_ui()

    # ========================================================
    # MAIN UI
    # ========================================================

    def create_ui(self):

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 10))

        ctk.CTkLabel(
            header,
            text="⚙ Settings",
            font=ctk.CTkFont(size=32, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="🏠 Dashboard",
            width=140,
            height=38,
            command=self.dashboard_callback
        ).pack(side="right")

        container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        container.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        # PROFILE SECTION

        profile_frame = ctk.CTkFrame(container, corner_radius=12)
        profile_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            profile_frame,
            text="👤 Profile",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=25, pady=(20, 15))

        ctk.CTkLabel(
            profile_frame,
            text="Username"
        ).pack(anchor="w", padx=25)

        self.username_entry = ctk.CTkEntry(
            profile_frame,
            height=40
        )
        self.username_entry.pack(
            fill="x",
            padx=25,
            pady=(5, 15)
        )
        self.username_entry.insert(0, self.username)

        ctk.CTkLabel(
            profile_frame,
            text="Role"
        ).pack(anchor="w", padx=25)

        self.role_entry = ctk.CTkEntry(
            profile_frame,
            height=40
        )
        self.role_entry.pack(
            fill="x",
            padx=25,
            pady=(5, 20)
        )
        self.role_entry.insert(0, self.role)
        self.role_entry.configure(state="disabled")

        # PASSWORD SECTION

        password_frame = ctk.CTkFrame(container, corner_radius=12)
        password_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            password_frame,
            text="🔐 Change Password",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=25, pady=(20, 15))

        ctk.CTkLabel(
            password_frame,
            text="Current Password"
        ).pack(anchor="w", padx=25)

        self.current_password = ctk.CTkEntry(
            password_frame,
            height=40,
            show="*"
        )
        self.current_password.pack(
            fill="x",
            padx=25,
            pady=(5, 12)
        )

        ctk.CTkLabel(
            password_frame,
            text="New Password"
        ).pack(anchor="w", padx=25)

        self.new_password = ctk.CTkEntry(
            password_frame,
            height=40,
            show="*"
        )
        self.new_password.pack(
            fill="x",
            padx=25,
            pady=(5, 12)
        )

        ctk.CTkLabel(
            password_frame,
            text="Confirm New Password"
        ).pack(anchor="w", padx=25)

        self.confirm_password = ctk.CTkEntry(
            password_frame,
            height=40,
            show="*"
        )
        self.confirm_password.pack(
            fill="x",
            padx=25,
            pady=(5, 15)
        )

        ctk.CTkButton(
            password_frame,
            text="🔑 Change Password",
            height=40,
            command=self.change_password
        ).pack(
            padx=25,
            pady=(0, 20),
            anchor="w"
        )

        # APPEARANCE SECTION

        appearance_frame = ctk.CTkFrame(
            container,
            corner_radius=12
        )
        appearance_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            appearance_frame,
            text="🎨 Appearance",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=25, pady=(20, 15))

        ctk.CTkLabel(
            appearance_frame,
            text="Theme"
        ).pack(anchor="w", padx=25)

        self.theme_option = ctk.CTkOptionMenu(
            appearance_frame,
            values=["Light", "Dark", "System"],
            width=200
        )
        self.theme_option.pack(
            anchor="w",
            padx=25,
            pady=10
        )

        self.load_saved_theme()

        ctk.CTkButton(
            appearance_frame,
            text="💾 Save Appearance",
            height=40,
            command=self.save_theme
        ).pack(
            anchor="w",
            padx=25,
            pady=(5, 20)
        )

        # KEYBOARD SHORTCUTS SECTION

        shortcuts_frame = ctk.CTkFrame(
            container,
            corner_radius=12
        )
        shortcuts_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            shortcuts_frame,
            text="⌨ Keyboard Shortcuts",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=25, pady=(20, 15))

        shortcuts = [
            ("Ctrl + H", "Dashboard"),
            ("Ctrl + M", "Medicines"),
            ("Ctrl + I", "Inventory"),
            ("Ctrl + S", "Sales / Billing"),
            ("Ctrl + R", "Reports"),
            ("Ctrl + N", "Notifications"),
            ("Ctrl + ,", "Settings"),
            ("Ctrl + L", "Logout")
        ]

        for shortcut, action in shortcuts:

            row = ctk.CTkFrame(
                shortcuts_frame,
                fg_color="transparent"
            )
            row.pack(fill="x", padx=25, pady=4)

            ctk.CTkLabel(
                row,
                text=shortcut,
                width=130,
                anchor="w",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=action,
                anchor="w",
                font=ctk.CTkFont(size=14)
            ).pack(side="left")

        ctk.CTkLabel(
            shortcuts_frame,
            text="Use these shortcuts to quickly navigate through the system.",
            text_color=("gray40", "gray70")
        ).pack(anchor="w", padx=25, pady=(10, 20))

        # ACCOUNT SECTION

        account_frame = ctk.CTkFrame(container, corner_radius=12)
        account_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            account_frame,
            text="🚪 Account",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=25, pady=(20, 15))

        ctk.CTkButton(
            account_frame,
            text="Logout",
            height=42,
            fg_color="#C0392B",
            hover_color="#A93226",
            command=self.logout
        ).pack(anchor="w", padx=25, pady=(5, 20))

    # ========================================================
    # LOAD SAVED THEME
    # ========================================================

    def load_saved_theme(self):

        theme = "Light"

        if self.user_id:

            try:
                with get_connection() as conn:
                    result = conn.execute(
                        """
                        SELECT theme
                        FROM user_settings
                        WHERE user_id = ?
                        """,
                        (self.user_id,)
                    ).fetchone()

                if result and result["theme"]:

                    saved_theme = result["theme"].lower()

                    if saved_theme == "dark":
                        theme = "Dark"
                    elif saved_theme == "system":
                        theme = "System"

            except Exception as error:
                print(f"Theme loading error: {error}")

        self.theme_option.set(theme)

    # ========================================================
    # CHANGE PASSWORD
    # ========================================================

    def change_password(self):

        current = self.current_password.get()
        new = self.new_password.get()
        confirm = self.confirm_password.get()

        if not current or not new or not confirm:
            messagebox.showwarning(
                "Missing Information",
                "Please fill all password fields."
            )
            return

        if new != confirm:
            messagebox.showerror(
                "Password Error",
                "New password and confirm password do not match."
            )
            return

        if len(new) < 6:
            messagebox.showwarning(
                "Weak Password",
                "New password must contain at least 6 characters."
            )
            return

        if not self.user_id:
            messagebox.showerror(
                "Password Error",
                "User information is missing."
            )
            return

        old_hash = hashlib.sha256(current.encode()).hexdigest()
        new_hash = hashlib.sha256(new.encode()).hexdigest()

        try:
            with get_connection() as conn:

                user = conn.execute(
                    """
                    SELECT user_id
                    FROM users
                    WHERE user_id = ?
                    AND password = ?
                    """,
                    (self.user_id, old_hash)
                ).fetchone()

                if not user:
                    messagebox.showerror(
                        "Password Error",
                        "Current password is incorrect."
                    )
                    return

                conn.execute(
                    """
                    UPDATE users
                    SET password = ?
                    WHERE user_id = ?
                    """,
                    (new_hash, self.user_id)
                )

            self.current_password.delete(0, "end")
            self.new_password.delete(0, "end")
            self.confirm_password.delete(0, "end")

            messagebox.showinfo(
                "Success",
                "Password changed successfully."
            )

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Unable to change password.\n\n{error}"
            )

    # ========================================================
    # SAVE THEME
    # ========================================================

    def save_theme(self):

        theme = self.theme_option.get()

        try:
            if theme == "Light":
                ctk.set_appearance_mode("light")
            elif theme == "Dark":
                ctk.set_appearance_mode("dark")
            else:
                ctk.set_appearance_mode("system")

            if self.user_id:

                with get_connection() as conn:

                    existing = conn.execute(
                        """
                        SELECT setting_id
                        FROM user_settings
                        WHERE user_id = ?
                        """,
                        (self.user_id,)
                    ).fetchone()

                    if existing:
                        conn.execute(
                            """
                            UPDATE user_settings
                            SET theme = ?
                            WHERE user_id = ?
                            """,
                            (theme.lower(), self.user_id)
                        )
                    else:
                        conn.execute(
                            """
                            INSERT INTO user_settings (user_id, theme)
                            VALUES (?, ?)
                            """,
                            (self.user_id, theme.lower())
                        )

            messagebox.showinfo(
                "Settings Saved",
                "Appearance settings saved successfully."
            )

        except Exception as error:
            messagebox.showerror(
                "Settings Error",
                f"Unable to save settings.\n\n{error}"
            )

    # ========================================================
    # LOGOUT
    # ========================================================

    def logout(self):

        confirm = messagebox.askyesno(
            "Logout",
            "Are you sure you want to logout?"
        )

        if not confirm:
            return

        if self.logout_callback:
            self.logout_callback()