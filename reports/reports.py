import customtkinter as ctk  # type: ignore
from tkinter import messagebox
from datetime import datetime

import matplotlib.pyplot as plt  # type: ignore
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore

from ui_kit import styled_treeview
from database import get_connection


class ReportsPage(ctk.CTkFrame):

    def __init__(self, parent, back_callback):
        super().__init__(parent, fg_color="transparent")

        self.back_callback = back_callback
        self.chart_canvas = None
        self.chart_figure = None

        self.create_ui()
        self.load_reports()

    # ============================================================
    # UI
    # ============================================================

    def create_ui(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=(20, 5))

        title = ctk.CTkLabel(
            header_frame,
            text="📊 Visual Reports",
            font=ctk.CTkFont(size=30, weight="bold")
        )
        title.pack(side="left")

        ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            width=120,
            command=self.load_reports
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            header_frame,
            text="🏠 Dashboard",
            width=130,
            command=self.back_callback
        ).pack(side="right", padx=5)

        ctk.CTkLabel(
            self,
            text="Sales, revenue and inventory performance",
            font=ctk.CTkFont(size=16)
        ).pack(anchor="w", padx=30, pady=(0, 15))

        # Summary cards
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=25, pady=5)

        for column in range(4):
            self.cards_frame.grid_columnconfigure(column, weight=1)

        self.revenue_card = self.create_card(
            self.cards_frame, "💰 Total Revenue", "₹ 0.00"
        )
        self.sales_card = self.create_card(
            self.cards_frame, "🧾 Total Bills", "0"
        )
        self.medicine_card = self.create_card(
            self.cards_frame, "💊 Medicines", "0"
        )
        self.stock_card = self.create_card(
            self.cards_frame, "📦 Low Stock", "0"
        )

        cards = [
            self.revenue_card,
            self.sales_card,
            self.medicine_card,
            self.stock_card
        ]

        for column, card in enumerate(cards):
            card.grid(
                row=0,
                column=column,
                padx=8,
                pady=5,
                sticky="nsew"
            )

        # Reports area
        report_frame = ctk.CTkFrame(self)
        report_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=15
        )

        self.chart_frame = ctk.CTkFrame(report_frame)
        self.chart_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 5),
            pady=10
        )

        ctk.CTkLabel(
            self.chart_frame,
            text="📈 Sales Overview",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(10, 5))

        top_frame = ctk.CTkFrame(report_frame)
        top_frame.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(5, 10),
            pady=10
        )

        ctk.CTkLabel(
            top_frame,
            text="🏆 Top Selling Medicines",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(10, 10))

        self.top_tree = styled_treeview(
            top_frame,
            columns=("medicine", "quantity", "sales"),
            show="headings",
            height=12
        )

        self.top_tree.heading("medicine", text="Medicine")
        self.top_tree.heading("quantity", text="Quantity Sold")
        self.top_tree.heading("sales", text="Sales")

        self.top_tree.column("medicine", width=180)
        self.top_tree.column("quantity", width=100, anchor="center")
        self.top_tree.column("sales", width=120, anchor="center")

        self.top_tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # ============================================================
    # SUMMARY CARD
    # ============================================================

    def create_card(self, parent, title, value):
        card = ctk.CTkFrame(parent, corner_radius=12)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(pady=(15, 5))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=25, weight="bold")
        )
        value_label.pack(pady=(0, 15))

        card.value_label = value_label
        return card

    # ============================================================
    # LOAD REPORTS
    # ============================================================

    def load_reports(self):
        try:
            # get_connection() is a context manager in this project.
            with get_connection() as connection:
                cursor = connection.cursor()

                cursor.execute("""
                    SELECT COALESCE(SUM(total), 0)
                    FROM sales
                """)
                total_revenue = float(cursor.fetchone()[0] or 0)

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM sales
                """)
                total_bills = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM medicines
                """)
                total_medicines = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM medicines
                    WHERE quantity <= min_stock
                """)
                low_stock = cursor.fetchone()[0]

                self.load_top_medicines(cursor)
                self.load_sales_chart(cursor)

            # Update summary cards after successful database reads.
            self.revenue_card.value_label.configure(
                text=f"₹ {total_revenue:,.2f}"
            )
            self.sales_card.value_label.configure(text=str(total_bills))
            self.medicine_card.value_label.configure(
                text=str(total_medicines)
            )
            self.stock_card.value_label.configure(text=str(low_stock))

        except Exception as error:
            print("Reports error:", error)
            messagebox.showerror(
                "Reports Error",
                f"Unable to load reports.\n\n{error}",
                parent=self
            )

    # ============================================================
    # TOP SELLING MEDICINES
    # ============================================================

    def load_top_medicines(self, cursor):
        for item in self.top_tree.get_children():
            self.top_tree.delete(item)

        cursor.execute("""
            SELECT
                medicines.name AS medicine_name,
                COALESCE(SUM(sale_items.quantity), 0) AS total_quantity,
                COALESCE(SUM(sale_items.total), 0) AS total_sales
            FROM sale_items
            JOIN medicines
                ON medicines.medicine_id = sale_items.medicine_id
            GROUP BY medicines.medicine_id, medicines.name
            ORDER BY total_quantity DESC
            LIMIT 10
        """)

        for row in cursor.fetchall():
            self.top_tree.insert(
                "",
                "end",
                values=(
                    row["medicine_name"],
                    row["total_quantity"],
                    f"₹ {float(row['total_sales'] or 0):,.2f}"
                )
            )

    # ============================================================
    # SALES CHART
    # ============================================================

    def load_sales_chart(self, cursor):
        # Remove the previous chart and its Matplotlib figure.
        if self.chart_canvas is not None:
            self.chart_canvas.get_tk_widget().destroy()
            self.chart_canvas = None

        if self.chart_figure is not None:
            plt.close(self.chart_figure)
            self.chart_figure = None

        # Remove an earlier empty-data message.
        for widget in self.chart_frame.winfo_children():
            if getattr(widget, "_reports_empty_message", False):
                widget.destroy()

        cursor.execute("""
            SELECT
                DATE(sale_date) AS sale_day,
                COALESCE(SUM(total), 0) AS daily_total
            FROM sales
            GROUP BY DATE(sale_date)
            ORDER BY DATE(sale_date) DESC
            LIMIT 30
        """)

        rows = list(reversed(cursor.fetchall()))

        if not rows:
            empty_label = ctk.CTkLabel(
                self.chart_frame,
                text="No sales data available yet.",
                font=ctk.CTkFont(size=16)
            )
            empty_label._reports_empty_message = True
            empty_label.pack(expand=True)
            return

        dates = []
        amounts = []

        for row in rows:
            date_value = row["sale_day"]

            try:
                parsed_date = datetime.fromisoformat(str(date_value))
                display_date = parsed_date.strftime("%d-%m")
            except (TypeError, ValueError):
                display_date = str(date_value)[:10]

            dates.append(display_date)
            amounts.append(float(row["daily_total"] or 0))

        self.chart_figure = plt.Figure(figsize=(6, 4), dpi=100)
        axis = self.chart_figure.add_subplot(111)

        axis.plot(
            dates,
            amounts,
            marker="o",
            linewidth=2
        )

        axis.set_title("Daily Sales Revenue")
        axis.set_xlabel("Date")
        axis.set_ylabel("Revenue (₹)")
        axis.tick_params(axis="x", rotation=45)
        axis.grid(True, alpha=0.3)

        self.chart_figure.tight_layout()

        self.chart_canvas = FigureCanvasTkAgg(
            self.chart_figure,
            master=self.chart_frame
        )

        self.chart_canvas.draw()

        self.chart_canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # ============================================================
    # CLEANUP
    # ============================================================

    def destroy(self):
        if self.chart_figure is not None:
            plt.close(self.chart_figure)
            self.chart_figure = None

        self.chart_canvas = None
        super().destroy()