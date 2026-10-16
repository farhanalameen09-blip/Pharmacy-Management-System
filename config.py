"""
Central configuration and design system for the Pharmacy Management System.

Every page should import its colors, fonts, spacing and window rules from here
so the whole application looks consistent and can be re-themed in one place.
"""

import os

# ==========================================
# APPLICATION
# ==========================================

APP_NAME = "Pharmacy Management System"
APP_VERSION = "1.0.0"
APP_SUBTITLE = "Inventory, sales and stock alerts"

QUALITY_GOAL = "Q08 - Improve User Satisfaction"


# ==========================================
# PROJECT PATHS
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "pharmacy.db")

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICON_PATH = os.path.join(ASSETS_DIR, "icon.ico")   # optional


# ==========================================
# THEME
# ==========================================

DEFAULT_THEME = "light"      # "light", "dark" or "system"
COLOR_THEME = "blue"         # customtkinter built-in: blue, green, dark-blue


# ==========================================
# COLOR PALETTE
# Each value is a (light, dark) pair, which customtkinter
# switches automatically with the appearance mode.
# ==========================================

class Colors:
    # Brand
    PRIMARY = ("#0B6E69", "#2BB3AB")          # teal, pharmacy / care feel
    PRIMARY_HOVER = ("#095A56", "#3CC7BE")
    PRIMARY_TEXT = ("#FFFFFF", "#06201E")

    # Surfaces
    BACKGROUND = ("#F4F7F8", "#12181B")
    SURFACE = ("#FFFFFF", "#1B2327")
    SURFACE_ALT = ("#EEF3F4", "#232D32")
    BORDER = ("#D8E1E4", "#2F3B41")

    # Sidebar / navigation
    SIDEBAR = ("#0F2F33", "#0C1A1D")
    SIDEBAR_TEXT = ("#D6E6E7", "#C4D6D8")
    SIDEBAR_ACTIVE = ("#17484D", "#17484D")

    # Text
    TEXT = ("#16282C", "#E8F0F1")
    TEXT_MUTED = ("#5B6E73", "#93A5AA")

    # Status (use the same meaning everywhere)
    SUCCESS = ("#2E7D32", "#66BB6A")
    WARNING = ("#E65100", "#FFA726")
    DANGER = ("#C62828", "#EF5350")
    INFO = ("#1565C0", "#64B5F6")

    # Soft status backgrounds for table rows and badges: (light, dark)
    SUCCESS_BG = ("#E8F5E9", "#1E3324")
    WARNING_BG = ("#FFF3E0", "#3A2F1E")
    DANGER_BG = ("#FDECEA", "#3B2224")
    INFO_BG = ("#E8F1FB", "#1F2D3D")


# ==========================================
# TYPOGRAPHY
# ==========================================

import sys

FONT_FAMILY = (
    "Segoe UI" if sys.platform.startswith("win")
    else "SF Pro Text" if sys.platform == "darwin"
    else "DejaVu Sans"
)


class Fonts:
    """Use as ctk.CTkFont(**Fonts.TITLE)."""

    DISPLAY = {"family": FONT_FAMILY, "size": 30, "weight": "bold"}
    TITLE = {"family": FONT_FAMILY, "size": 24, "weight": "bold"}
    HEADING = {"family": FONT_FAMILY, "size": 18, "weight": "bold"}
    SUBHEADING = {"family": FONT_FAMILY, "size": 15, "weight": "bold"}
    BODY = {"family": FONT_FAMILY, "size": 14, "weight": "normal"}
    SMALL = {"family": FONT_FAMILY, "size": 12, "weight": "normal"}
    METRIC = {"family": FONT_FAMILY, "size": 34, "weight": "bold"}


# ==========================================
# SPACING AND SHAPE (8 px grid)
# ==========================================

class Spacing:
    XS = 4
    SM = 8
    MD = 16
    LG = 24
    XL = 32


class Shape:
    RADIUS_SM = 6      # inputs, badges
    RADIUS_MD = 10     # buttons
    RADIUS_LG = 14     # cards, panels

    BUTTON_HEIGHT = 38
    INPUT_HEIGHT = 36
    SIDEBAR_WIDTH = 230
    TABLE_ROW_HEIGHT = 36


# ==========================================
# WINDOW
# ==========================================

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 620


def window_title():
    return f"{APP_NAME}  |  v{APP_VERSION}"


def center_window(window, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
    """Size the window and place it in the middle of the screen.

    Never larger than the screen, so it also works on small laptops.
    """
    window.update_idletasks()

    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()

    width = min(width, screen_w - 40)
    height = min(height, screen_h - 80)

    x = (screen_w - width) // 2
    y = max((screen_h - height) // 2 - 20, 0)

    window.geometry(f"{width}x{height}+{x}+{y}")


def setup_window(window):
    """Apply title, size, minimum size, icon and background in one call."""
    import customtkinter as ctk # type: ignore


    ctk.set_appearance_mode(DEFAULT_THEME)
    ctk.set_default_color_theme(COLOR_THEME)

    window.title(window_title())
    window.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
    window.configure(fg_color=Colors.BACKGROUND)

    if os.path.exists(ICON_PATH):
        try:
            window.iconbitmap(ICON_PATH)
        except Exception:
            pass   # icons are optional and platform dependent

    center_window(window)


# ==========================================
# ENSURE FOLDERS EXIST
# ==========================================

os.makedirs(DATABASE_DIR, exist_ok=True)