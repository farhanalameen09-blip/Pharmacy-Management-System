import customtkinter as ctk # type: ignore

from ui_kit import styled_treeview
from tkinter import ttk, messagebox
from database import get_connection
from datetime import datetime
import matplotlib.pyplot as plt # type: ignore
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # pyright: ignore[reportMissingModuleSource]


class ReportsPage(ctk.CTkFrame):

    def __init__(self, parent, back_callback):
        super().__init__(parent, fg_color="transparent")

        self.back_callback = back_callback

        self.create_ui()
        self.load_reports()

    # ============================================================
    # UI
    # ============================================================

    def create_ui(self):

        # ---------------- HEADER ----------------

        header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header_frame.pack(
            fill="x",
            padx=25,
            pady=(20, 5)
        )

        title = ctk.CTkLabel(
            header_frame,
            text="📊 Visual Reports",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        )
        title.pack(side="left")

        refresh_button = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            width=120,
            command=self.load_reports
        )
        refresh_button.pack(
            side="right",
            padx=5
        )

        back_button = ctk.CTkButton(
            header_frame,
            text="🏠 Dashboard",
            width=130,
            command=self.back_callback
        )
        back_button.pack(
            side="right",
            padx=5
        )

        subtitle = ctk.CTkLabel(
            self,
            text="Sales, revenue and inventory performance",
            font=ctk.CTkFont(size=16)
        )
        subtitle.pack(
            anchor="w",
            padx=30,
            pady=(0, 15)
        )

        # ---------------- SUMMARY CARDS ----------------

        self.cards_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.cards_frame.pack(
            fill="x",
            padx=25,
            pady=5
        )

        for column in range(4):
            self.cards_frame.grid_columnconfigure(
                column,
                weight=1
            )

        self.revenue_card = self.create_card(
            self.cards_frame,
            "💰 Total Revenue",
            "₹ 0"
        )

        self.sales_card = self.create_card(
            self.cards_frame,
            "🧾 Total Bills",
            "0"
        )

        self.medicine_card = self.create_card(
            self.cards_frame,
            "💊 Medicines",
            "0"
        )

        self.stock_card = self.create_card(
            self.cards_frame,
            "📦 Low Stock",
            "0"
        )

        self.revenue_card.grid(
            row=0,
            column=0,
            padx=8,
            sticky="nsew"
        )

        self.sales_card.grid(
            row=0,
            column=1,
            padx=8,
            sticky="nsew"
        )

        self.medicine_card.grid(
            row=0,
            column=2,
            padx=8,
            sticky="nsew"
        )

        self.stock_card.grid(
            row=0,
            column=3,
            padx=8,
            sticky="nsew"
        )

        # ---------------- REPORT AREA ----------------

        report_frame = ctk.CTkFrame(
            self
        )
        report_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=15
        )

        # Chart

        self.chart_frame = ctk.CTkFrame(
            report_frame
        )
        self.chart_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 5),
            pady=10
        )

        chart_title = ctk.CTkLabel(
            self.chart_frame,
            text="📈 Sales Overview",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        )
        chart_title.pack(
            pady=(10, 5)
        )

        # Top medicines

        top_frame = ctk.CTkFrame(
            report_frame
        )
        top_frame.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(5, 10),
            pady=10
        )

        top_title = ctk.CTkLabel(
            top_frame,
            text="🏆 Top Selling Medicines",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        )
        top_title.pack(
            pady=(10, 10)
        )

        self.top_tree = styled_treeview(
            top_frame,
            columns=(
                "medicine",
                "quantity",
                "sales"
            ),
            show="headings",
            height=12
        )

        self.top_tree.heading(
            "medicine",
            text="Medicine"
        )

        self.top_tree.heading(
            "quantity",
            text="Quantity Sold"
        )

        self.top_tree.heading(
            "sales",
            text="Sales"
        )

        self.top_tree.column(
            "medicine",
            width=180
        )

        self.top_tree.column(
            "quantity",
            width=100,
            anchor="center"
        )

        self.top_tree.column(
            "sales",
            width=100,
            anchor="center"
        )

        self.top_tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # ============================================================
    # CARD
    # ============================================================

    def create_card(
        self,
        parent,
        title,
        value
    ):

        card = ctk.CTkFrame(
            parent,
            corner_radius=12
        )

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            )
        )

        title_label.pack(
            pady=(15, 5)
        )

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(
                size=25,
                weight="bold"
            )
        )

        value_label.pack(
            pady=(0, 15)
        )

        card.value_label = value_label

        return card

    # ============================================================
    # LOAD REPORTS
    # ============================================================

    def load_reports(self):

        try:

            connection = get_connection()
            cursor = connection.cursor()

            # ---------------- TOTAL REVENUE ----------------

            cursor.execute("""
                SELECT
                    COALESCE(SUM(total), 0)
                FROM sales
            """)

            total_revenue = cursor.fetchone()[0]

            # ---------------- TOTAL BILLS ----------------

            cursor.execute("""
                SELECT COUNT(*)
                FROM sales
            """)

            total_bills = cursor.fetchone()[0]

            # ---------------- TOTAL MEDICINES ----------------

            cursor.execute("""
                SELECT COUNT(*)
                FROM medicines
            """)

            total_medicines = cursor.fetchone()[0]

            # ---------------- LOW STOCK ----------------

            cursor.execute("""
                SELECT COUNT(*)
                FROM medicines
                WHERE quantity <= min_stock
            """)

            low_stock = cursor.fetchone()[0]

            # Update cards

            self.revenue_card.value_label.configure(
                text=f"₹ {total_revenue:,.2f}"
            )

            self.sales_card.value_label.configure(
                text=str(total_bills)
            )

            self.medicine_card.value_label.configure(
                text=str(total_medicines)
            )

            self.stock_card.value_label.configure(
                text=str(low_stock)
            )

            # ---------------- TOP MEDICINES ----------------

            self.load_top_medicines(cursor)

            # ---------------- SALES CHART ----------------

            self.load_sales_chart(cursor)

            connection.close()

        except Exception as error:

            messagebox.showerror(
                "Reports Error",
                f"Unable to load reports.\n\n{error}"
            )

            print(
                "Reports error:",
                error
            )

    # ============================================================
    # TOP MEDICINES
    # ============================================================

    def load_top_medicines(self, cursor):

        for item in self.top_tree.get_children():
            self.top_tree.delete(item)

        cursor.execute("""
            SELECT
                medicines.name,
                SUM(sale_items.quantity) AS total_quantity,
                SUM(sale_items.total) AS total_sales
            FROM sale_items
            JOIN medicines
                ON medicines.medicine_id =
                   sale_items.medicine_id
            GROUP BY medicines.medicine_id
            ORDER BY total_quantity DESC
            LIMIT 10
        """)

        rows = cursor.fetchall()

        for row in rows:

            self.top_tree.insert(
                "",
                "end",
                values=(
                    row["name"],
                    row["total_quantity"],
                    f"₹ {row['total_sales']:,.2f}"
                )
            )

    # ============================================================
    # SALES CHART
    # ============================================================

    def load_sales_chart(self, cursor):

        # Remove old chart

        for widget in self.chart_frame.winfo_children():

            if isinstance(
                widget,
                FigureCanvasTkAgg
            ):
                widget.get_tk_widget().destroy()

        cursor.execute("""
            SELECT
                sale_date,
                SUM(total) AS total
            FROM sales
            GROUP BY sale_date
            ORDER BY sale_date
            LIMIT 30
        """)

        rows = cursor.fetchall()

        dates = []
        amounts = []

        for row in rows:

            date_value = row["sale_date"]

            try:

                parsed_date = datetime.fromisoformat(
                    date_value
                )

                display_date = parsed_date.strftime(
                    "%d-%m"
                )

            except Exception:

                display_date = str(
                    date_value
                )[:10]

            dates.append(display_date)
            amounts.append(
                float(row["total"] or 0)
            )

        # If no sales exist

        if not dates:

            empty_label = ctk.CTkLabel(
                self.chart_frame,
                text="No sales data available yet.",
                font=ctk.CTkFont(
                    size=16
                )
            )

            empty_label.pack(
                expand=True
            )

            return

        # ---------------- MATPLOTLIB ----------------

        figure = plt.Figure(
            figsize=(6, 4),
            dpi=100
        )

        axis = figure.add_subplot(111)

        axis.plot(
            dates,
            amounts,
            marker="o"
        )

        axis.set_title(
            "Sales Revenue"
        )

        axis.set_xlabel(
            "Date"
        )

        axis.set_ylabel(
            "Revenue (₹)"
        )

        axis.tick_params(
            axis="x",
            rotation=45
        )

        figure.tight_layout()

        canvas = FigureCanvasTkAgg(
            figure,
            master=self.chart_frame
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )