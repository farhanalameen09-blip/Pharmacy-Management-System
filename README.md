# 💊 Pharmacy Management System

### A Python-Based Pharmacy Management Application

The Pharmacy Management System is a desktop application developed using Python
to simplify and organize daily pharmacy operations. It aims to help pharmacy
staff manage medicines, inventory, customers, suppliers, sales, billing, and
reports through a centralized application.

The project focuses on improving user satisfaction through an interactive
dashboard, organized navigation, visual reports, and convenient management
features.

**Project Type:** Desktop Application  
**Programming Language:** Python  
**Database:** SQLite  
**GUI Framework:** CustomTkinter  
**Project Status:** Under Development

---

## 📌 Table of Contents

1. About the Project
2. Project Objectives
3. Key Features
4. Technologies Used
5. Project Structure
6. System Requirements
7. Installation Guide
8. How to Run
9. Application Modules
10. Quality Goal
11. Future Improvements
12. Learning Outcomes
13. Author
14. License

---

## 📖 About the Project

Pharmacies handle multiple daily operations, including medicine management,
stock monitoring, customer records, supplier details, and sales transactions.

Managing these operations manually can be time-consuming and may lead to
errors in record maintenance.

The Pharmacy Management System aims to simplify these activities by providing
a centralized desktop application with a graphical user interface.

The application is being developed using Python, CustomTkinter, and SQLite.
It is designed with separate modules to make the project easier to maintain,
test, and improve.

This project is part of an academic software development assignment and is
being developed with a focus on usability and user satisfaction.

---

## 🎯 Project Objectives

The main objectives of this project are:

- To simplify pharmacy management operations.
- To maintain medicine and inventory records.
- To organize customer and supplier information.
- To support sales and billing operations.
- To help staff monitor available medicine stock.
- To provide an organized dashboard.
- To present useful information through reports.
- To improve the usability of the application.
- To maintain data using a database.
- To develop a modular and maintainable software application.

---

## ✨ Key Features

### 1. 🔐 User Login

The login module provides an interface for users to access the application.

Planned capabilities include:

- User authentication.
- Input validation.
- Error messages for invalid credentials.
- User session management.

### 2. 💊 Medicine Management

The medicine management module is intended to organize medicine records.

Its intended capabilities include:

- Adding medicine details.
- Viewing medicine records.
- Updating medicine information.
- Searching for medicines.
- Managing medicine-related information.

### 3. 📦 Inventory Management

The inventory module is designed to help pharmacy staff monitor stock.

Its intended capabilities include:

- Tracking medicine quantities.
- Viewing inventory information.
- Monitoring stock availability.
- Supporting inventory updates.
- Identifying medicines that require restocking.

### 4. 🧾 Sales and Billing

The billing module is intended to support pharmacy sales operations.

Its capabilities may include:

- Selecting medicines for a sale.
- Managing items in a billing cart.
- Calculating bill totals.
- Generating invoice information.
- Updating inventory after successful sales.

### 5. 👥 Customer Management

The customer module is intended to organize customer information.

Its capabilities may include:

- Maintaining customer records.
- Viewing customer details.
- Updating customer information.
- Supporting customer record management.

### 6. 🏭 Supplier Management

The supplier module is designed to organize supplier information.

Its capabilities may include:

- Maintaining supplier records.
- Viewing supplier details.
- Updating supplier information.
- Organizing supplier-related data.

### 7. 📊 Reports

The reporting module is intended to present useful information about pharmacy
operations.

Potential reporting capabilities include:

- Sales summaries.
- Inventory summaries.
- Visual charts.
- Data-based reports.
- Better visibility into pharmacy operations.

### 8. 🔔 Notifications

The notification module is intended to provide relevant information to users.

Potential uses include:

- Low-stock notifications.
- Important inventory updates.
- Operational reminders.

### 9. ⚙️ Settings

The settings module provides a dedicated place for application preferences.

Planned improvements include:

- Application appearance preferences.
- User-specific settings.
- Convenient configuration options.

### 10. 📈 Interactive Dashboard

The dashboard aims to provide a convenient overview of important pharmacy
information.

Potential dashboard elements include:

- Summary cards.
- Medicine and inventory information.
- Sales-related statistics.
- Quick navigation to modules.
- Visual summaries.

**Note:** Features listed as intended or planned should be considered under
development until they have been implemented and tested.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| CustomTkinter | Graphical user interface |
| SQLite | Local database management |
| Matplotlib | Data visualization and charts |
| Pandas | Data processing and analysis |
| Pillow | Image handling in the interface |
| Git | Version control |
| GitHub | Source code hosting |

---

## 📁 Project Structure

The project uses a modular structure to separate application components.

```text
Pharmacy Management System/
│
├── main.py
├── config.py
├── database.py
├── ui_kit.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── assets/
├── billing/
├── customers/
├── database/
├── inventory/
├── login/
├── medicines/
├── notifications/
├── reports/
├── settings/
└── suppliers/