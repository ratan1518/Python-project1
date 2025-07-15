import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from ttkbootstrap import Style
from ttkbootstrap.widgets import DateEntry

# Initialize an empty DataFrame
expenses = pd.DataFrame(columns=['Date', 'Credited', 'Debited', 'Amount', 'Account Balance', 'Category'])
account_balance = 0  # Global variable to track balance

# ----------------------------- FUNCTIONS -----------------------------------
def add_expense():
    """ Adds a new expense to the table and updates visualization """
    global expenses, account_balance

    date = date_entry.entry.get().strip()
    credited = credited_entry.get().strip()
    debited = debited_entry.get().strip()
    category = category_var.get().strip()

    if not date or category in ["Select Category", "", None] or (not credited and not debited):
        messagebox.showwarning("Warning", "Please fill all required fields correctly!")
        return

    try:
        credited = float(credited) if credited else 0
        debited = float(debited) if debited else 0
        amount = credited - debited
        account_balance += amount  # Update balance

        # Ensure category is valid
        if pd.isna(category) or category == "":
            category = "Other"  # Set default category

        new_expense = pd.DataFrame([[date, credited, debited, amount, account_balance, category]],
                                   columns=expenses.columns)
        expenses = pd.concat([expenses, new_expense], ignore_index=True)

        # Fill any NaN categories with "Other"
        expenses["Category"].fillna("Other", inplace=True)

        update_table()
        visualize_expenses()

    except ValueError:
        messagebox.showerror("Error", "Credited and Debited values must be numbers!")


def update_table():
    """ Updates the expense records table in the UI """
    for row in table.get_children():
        table.delete(row)  # Clear previous entries

    for _, row in expenses.iterrows():
        table.insert("", tk.END, values=list(row))  # Insert updated data


def save_expenses():
    """ Saves the current expenses to a CSV file """
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        expenses.to_csv(file_path, index=False)
        messagebox.showinfo("Success", "Expenses saved successfully!")


def load_expenses():
    """ Loads expenses from a CSV file and updates the table and visualization """
    global expenses, account_balance
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    try:
        expenses = pd.read_csv(file_path)

        required_columns = ['Date', 'Credited', 'Debited', 'Amount', 'Account Balance', 'Category']
        for col in required_columns:
            if col not in expenses.columns:
                raise ValueError(f"Missing column in CSV: {col}")

        expenses["Credited"] = pd.to_numeric(expenses["Credited"], errors="coerce").fillna(0)
        expenses["Debited"] = pd.to_numeric(expenses["Debited"], errors="coerce").fillna(0)
        expenses["Amount"] = pd.to_numeric(expenses["Amount"], errors="coerce").fillna(0)
        expenses["Account Balance"] = pd.to_numeric(expenses["Account Balance"], errors="coerce").fillna(0)

        expenses["Category"].fillna("Other", inplace=True)

        account_balance = expenses.iloc[-1]["Account Balance"] if not expenses.empty else 0

        update_table()
        visualize_expenses()

        messagebox.showinfo("Success", "Expenses loaded successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load CSV: {e}")


def visualize_expenses():
    """ Creates a Pie Chart visualization of expenses """
    if expenses.empty:
        messagebox.showwarning("Warning", "No expenses to visualize!")
        return

    category_totals = expenses.groupby('Category')['Debited'].sum()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(category_totals, labels=category_totals.index, autopct='%1.1f%%',
           colors=sns.color_palette("coolwarm", len(category_totals)))
    ax.set_title("Expense Distribution", fontsize=12, fontweight='bold')

    for widget in graph_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()


def toggle_theme():
    """ Toggles between light and dark mode """
    if style.theme_use() == "flatly":
        style.theme_use("darkly")
    else:
        style.theme_use("flatly")


def clear_all():
    """ Clears all expenses from the table and visualization """
    global expenses, account_balance
    expenses = pd.DataFrame(columns=['Date', 'Credited', 'Debited', 'Amount', 'Account Balance', 'Category'])
    account_balance = 0
    update_table()
    for widget in graph_frame.winfo_children():
        widget.destroy()
    messagebox.showinfo("Cleared", "All expenses have been cleared!")

# ---------------------------- UI DESIGN -----------------------------------

window = tk.Tk()
window.title("Expense Tracker")
window.geometry("800x500")

style = Style(theme="flatly")

frame = ttk.Frame(window, padding=5)
frame.pack(fill=tk.BOTH, expand=True)

left_frame = ttk.LabelFrame(frame, text="Add Expense", padding=5)
left_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)

ttk.Label(left_frame, text="Date:").pack(anchor="w")
date_entry = DateEntry(left_frame, bootstyle="primary")
date_entry.pack(anchor="w", pady=2)

ttk.Label(left_frame, text="Credited:").pack(anchor="w")
credited_entry = ttk.Entry(left_frame)
credited_entry.pack(anchor="w", pady=2)

ttk.Label(left_frame, text="Debited:").pack(anchor="w")
debited_entry = ttk.Entry(left_frame)
debited_entry.pack(anchor="w", pady=2)

ttk.Label(left_frame, text="Category:").pack(anchor="w")
category_var = tk.StringVar(value="Other")
category_menu = ttk.Combobox(left_frame, textvariable=category_var, values=["Food", "Transport", "Entertainment", "Utilities", "Other"])
category_menu.pack(anchor="w", pady=2)

ttk.Button(left_frame, text="Add Expense", command=add_expense, bootstyle="success").pack(pady=2)
ttk.Button(left_frame, text="Save Expenses", command=save_expenses, bootstyle="info").pack(pady=2)
ttk.Button(left_frame, text="Load Expenses", command=load_expenses, bootstyle="warning").pack(pady=2)
ttk.Button(left_frame, text="Visualize", command=visualize_expenses, bootstyle="secondary").pack(pady=2)
ttk.Button(left_frame, text="Toggle Dark Mode", command=toggle_theme, bootstyle="danger").pack(pady=2)
ttk.Button(left_frame, text="Clear All", command=clear_all, bootstyle="danger").pack(pady=2)

center_frame = ttk.LabelFrame(frame, text="Expense Records", padding=5)
center_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)

table = ttk.Treeview(center_frame, columns=("Date", "Credited", "Debited", "Amount", "Account Balance", "Category"), show="headings")
for col in table["columns"]:
    table.heading(col, text=col)
    if col == "Date":
        table.column(col, width=70, anchor="center")
    elif col in ["Credited", "Debited", "Amount"]:
        table.column(col, width=60, anchor="center")
    else:
        table.column(col, width=80, anchor="center")

table.pack(fill=tk.BOTH, expand=True)

graph_frame = ttk.LabelFrame(frame, text="Expense Visualization", padding=5)
graph_frame.pack(side=tk.BOTTOM, padx=5, pady=5, fill=tk.BOTH, expand=True)

window.mainloop()
