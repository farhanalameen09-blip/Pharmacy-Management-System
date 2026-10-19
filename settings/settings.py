import customtkinter as ctk  # type: ignore
import hashlib
import sqlite3

from tkinter import messagebox

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
        self.load_saved_theme()

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

        self.create_profile_section(container)
        self.create_password_section(container)
        self.create_appearance_section(container)
        self.create_shortcuts_section(container)
        self.create_account_section(container)

    # ========================================================
    # PROFILE SECTION
    # ========================================================

    def create_profile_section(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=12)
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            frame,
            text="👤 Profile",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=25, pady=(20, 15))

        ctk.CTkLabel(
            frame,
            text="Username"
        ).pack(anchor="w", padx=25)

        self.username_entry = ctk.CTkEntry(
            frame,
            height=40,
            placeholder_text="Enter username"
        )
        self.username_entry.pack(
            fill="x",
            padx=25,
            pady=(5, 10)
        )
        self.username_entry.insert(0, self.username)

        ctk.CTkLabel(
            frame,
            text="Role"
        ).pack(anchor="w", padx=25)

        self.role_entry = ctk.CTkEntry(
            frame,
            height=40
        )
        self.role_entry.pack(
            fill="x",
            padx=25,
            pady=(5, 15)
        )
        self.role_entry.insert(0, self.role)
        self.role_entry.configure(state="disabled")

        ctk.CTkButton(
            frame,
            text="💾 Save Profile",
            height=40,
            command=self.save_profile
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 20)
        )

    # ========================================================
    # PASSWORD SECTION
    # ========================================================

    def create_password_section(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=12)
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            frame,
            text="🔐 Change Password",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=25, pady=(20, 15))

        ctk.CTkLabel(
            frame,
            text="Current Password"
        ).pack(anchor="w", padx=25)

        self.current_password = ctk.CTkEntry(
            frame,
            height=40,
            show="*",
            placeholder_text="Enter current password"
        )
        self.current_password.pack(
            fill="x",
            padx=25,
            pady=(5, 12)
        )

        ctk.CTkLabel(
            frame,
            text="New Password"
        ).pack(anchor="w", padx=25)

        self.new_password = ctk.CTkEntry(
            frame,
            height=40,
            show="*",
            placeholder_text="Enter new password"
        )
        self.new_password.pack(
            fill="x",
            padx=25,
            pady=(5, 12)
        )

        ctk.CTkLabel(
            frame,
            text="Confirm New Password"
        ).pack(anchor="w", padx=25)

        self.confirm_password = ctk.CTkEntry(
            frame,
            height=40,
            show="*",
            placeholder_text="Confirm new password"
        )
        self.confirm_password.pack(
            fill="x",
            padx=25,
            pady=(5, 15)
        )

        ctk.CTkButton(
            frame,
            text="🔑 Change Password",
            height=40,
            command=self.change_password
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 20)
        )

    # ========================================================
    # APPEARANCE SECTION
    # ========================================================

    def create_appearance_section(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=12)
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            frame,
            text="🎨 Appearance",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=25, pady=(20, 15))

        ctk.CTkLabel(
            frame,
            text="Theme"
        ).pack(anchor="w", padx=25)

        self.theme_option = ctk.CTkOptionMenu(
            frame,
            values=["Light", "Dark", "System"],
            width=200
        )
        self.theme_option.pack(
            anchor="w",
            padx=25,
            pady=10
        )

        ctk.CTkButton(
            frame,
            text="💾 Save Appearance",
            height=40,
            command=self.save_theme
        ).pack(
            anchor="w",
            padx=25,
            pady=(5, 20)
        )

    # ========================================================
    # KEYBOARD SHORTCUTS SECTION
    # ========================================================

    def create_shortcuts_section(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=12)
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            frame,
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
            row = ctk.CTkFrame(frame, fg_color="transparent")
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
            frame,
            text="Shortcut bindings must be configured in the main application.",
            text_color=("gray40", "gray70")
        ).pack(anchor="w", padx=25, pady=(10, 20))

    # ========================================================
    # ACCOUNT SECTION
    # ========================================================

    def create_account_section(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=12)
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            frame,
            text="🚪 Account",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=25, pady=(20, 15))

        ctk.CTkButton(
            frame,
            text="Logout",
            height=42,
            fg_color="#C0392B",
            hover_color="#A93226",
            command=self.logout
        ).pack(anchor="w", padx=25, pady=(5, 20))

    # ========================================================
    # PROFILE UPDATE
    # ========================================================

    def save_profile(self):
        new_username = self.username_entry.get().strip()

        if not new_username:
            messagebox.showwarning(
                "Invalid Username",
                "Username cannot be empty.",
                parent=self
            )
            self.username_entry.focus_set()
            return

        if len(new_username) < 3:
            messagebox.showwarning(
                "Invalid Username",
                "Username must contain at least 3 characters.",
                parent=self
            )
            return

        if not self.user_id:
            messagebox.showerror(
                "Profile Error",
                "User information is missing.",
                parent=self
            )
            return

        try:
            with get_connection() as conn:
                existing = conn.execute(
                    """
                    SELECT user_id
                    FROM users
                    WHERE username = ?
                      AND user_id != ?
                    """,
                    (new_username, self.user_id)
                ).fetchone()

                if existing:
                    messagebox.showerror(
                        "Username Unavailable",
                        "This username is already in use.",
                        parent=self
                    )
                    return

                conn.execute(
                    """
                    UPDATE users
                    SET username = ?
                    WHERE user_id = ?
                    """,
                    (new_username, self.user_id)
                )

            self.username = new_username

            messagebox.showinfo(
                "Profile Updated",
                "Username updated successfully. "
                "You may need to log in again for other screens "
                "to display the new username.",
                parent=self
            )

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                f"Unable to update profile.\n\n{error}",
                parent=self
            )

    # ========================================================
    # PASSWORD HASHING
    # ========================================================

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest()

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
                "Please fill all password fields.",
                parent=self
            )
            return

        if new != confirm:
            messagebox.showerror(
                "Password Error",
                "New password and confirmation do not match.",
                parent=self
            )
            return

        if len(new) < 6:
            messagebox.showwarning(
                "Weak Password",
                "New password must contain at least 6 characters.",
                parent=self
            )
            return

        if current == new:
            messagebox.showwarning(
                "Password Error",
                "Your new password must differ from the current password.",
                parent=self
            )
            return

        if not self.user_id:
            messagebox.showerror(
                "Password Error",
                "User information is missing.",
                parent=self
            )
            return

        old_hash = self.hash_password(current)
        new_hash = self.hash_password(new)

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
                        "Current password is incorrect.",
                        parent=self
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
                "Password changed successfully.",
                parent=self
            )

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                f"Unable to change password.\n\n{error}",
                parent=self
            )

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

            except sqlite3.Error as error:
                print(f"Theme loading error: {error}")

        self.theme_option.set(theme)

    # ========================================================
    # SAVE THEME
    # ========================================================

    def save_theme(self):
        theme = self.theme_option.get()
        previous_theme = ctk.get_appearance_mode()

        try:
            if self.user_id:
                with get_connection() as conn:
                    existing = conn.execute(
                        """
                        SELECT user_id
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

            ctk.set_appearance_mode(theme.lower())

            messagebox.showinfo(
                "Settings Saved",
                "Appearance settings saved successfully.",
                parent=self
            )

        except sqlite3.Error as error:
            messagebox.showerror(
                "Settings Error",
                f"Unable to save appearance settings.\n\n{error}",
                parent=self
            )

        except Exception as error:
            # Restore the previous appearance if applying the new
            # theme fails after the database operation.
            try:
                ctk.set_appearance_mode(previous_theme.lower())
            except Exception:
                pass

            messagebox.showerror(
                "Settings Error",
                f"Unable to apply the selected theme.\n\n{error}",
                parent=self
            )

    # ========================================================
    # LOGOUT
    # ========================================================

    def logout(self):
        if not self.logout_callback:
            messagebox.showwarning(
                "Logout Unavailable",
                "The logout action is not configured.",
                parent=self
            )
            return

        confirm = messagebox.askyesno(
            "Logout",
            "Are you sure you want to logout?",
            parent=self
        )

        if confirm:
            self.logout_callback()