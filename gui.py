import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager, generate_ean13
from barcode_utils import generate_barcode, read_barcodes
from report_generator import generate_report

class InventoryApp:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.main_window = tk.Tk()
        self.main_window.title("Inventory Management System")
        self.create_login_window()

    def create_login_window(self):
        self.login_frame = tk.Frame(self.main_window)
        self.login_frame.pack(padx=10, pady=10)
        tk.Label(self.login_frame, text="Username:").grid(row=0, column=0, sticky="w")
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, pady=5)

        tk.Label(self.login_frame, text="Password:").grid(row=1, column=0, sticky="w")
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)

        login_button = tk.Button(self.login_frame, text="Login", command=self.on_login)
        login_button.grid(row=2, column=0, columnspan=2, pady=10)

    def on_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.db_manager.verify_user(username, password)
        if role:
            messagebox.showinfo("Login Success", f"Welcome {username}!")
            self.main_window.destroy()
            if role == "admin":
                self.open_admin_window(username)
            elif role == "manager":
                self.open_manager_window()
            elif role == "worker":
                self.open_worker_window()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def open_admin_window(self, logged_in_user):
        self.admin_window = tk.Tk()
        self.admin_window.title("Admin Panel")
        self.create_tabs(self.admin_window, logged_in_user)
        self.admin_window.mainloop()

    def open_manager_window(self):
        self.manager_window = tk.Tk()
        self.manager_window.title("Manager Panel")
        self.create_tabs(self.manager_window)
        self.manager_window.mainloop()

    def open_worker_window(self):
        self.worker_window = tk.Tk()
        self.worker_window.title("Worker Panel")
        self.create_tabs(self.worker_window, worker=True)
        self.worker_window.mainloop()

    def create_tabs(self, window, logged_in_user=None, worker=False):
        tab_control = ttk.Notebook(window)
        inventory_mgmt_frame = ttk.Frame(tab_control)
        item_sign_frame = ttk.Frame(tab_control)

        if not worker:
            user_mgmt_frame = ttk.Frame(tab_control)
            tab_control.add(user_mgmt_frame, text='User Management')
            ttk.Button(user_mgmt_frame, text="Add User", command=self.add_user).pack(pady=10)
            ttk.Button(user_mgmt_frame, text="View Users", command=self.view_users).pack(pady=10)
            if logged_in_user:
                ttk.Button(user_mgmt_frame, text="Delete User", command=lambda: self.delete_user(logged_in_user)).pack(pady=10)

        tab_control.add(inventory_mgmt_frame, text='Inventory Management')
        ttk.Button(inventory_mgmt_frame, text="Add Inventory Item", command=self.add_inventory_item).pack(pady=10)
        ttk.Button(inventory_mgmt_frame, text="View Inventory", command=self.view_inventory).pack(pady=10)
        ttk.Button(inventory_mgmt_frame, text="Generate Report", command=generate_report).pack(pady=10)
        ttk.Button(inventory_mgmt_frame, text="Print Barcode", command=self.print_barcode_prompt).pack(pady=10)

        tab_control.add(item_sign_frame, text='Sign In/Out Items')
        ttk.Button(item_sign_frame, text="Sign In/Out Item", command=self.sign_in_out_item).pack(pady=10)
        ttk.Button(item_sign_frame, text="Scan Barcode", command=read_barcodes).pack(pady=10)

        tab_control.pack(expand=1, fill="both")

    def add_user(self):
        add_user_window = tk.Toplevel()
        add_user_window.title("Add New User")
        add_user_window.geometry("300x200")

        tk.Label(add_user_window, text="Username:").grid(row=0, column=0)
        username_entry = tk.Entry(add_user_window)
        username_entry.grid(row=0, column=1)

        tk.Label(add_user_window, text="Password:").grid(row=1, column=0)
        password_entry = tk.Entry(add_user_window, show="*")
        password_entry.grid(row=1, column=1)

        tk.Label(add_user_window, text="Role (admin/manager/worker):").grid(row=2, column=0)
        role_entry = tk.Entry(add_user_window)
        role_entry.grid(row=2, column=1)

        def submit():
            username = username_entry.get()
            password = password_entry.get()
            role = role_entry.get()
            if self.db_manager.add_user(username, password, role):
                messagebox.showinfo("Success", "User successfully added")
                add_user_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to add user")

        submit_button = tk.Button(add_user_window, text="Add User", command=submit)
        submit_button.grid(row=3, column=1, pady=10)

    def delete_user(self, logged_in_user):
        delete_user_window = tk.Toplevel()
        delete_user_window.title("Delete User")
        delete_user_window.geometry("300x200")

        tk.Label(delete_user_window, text="Select user to delete:").pack()
        users_listbox = tk.Listbox(delete_user_window)
        users_listbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        users = self.db_manager.get_users()
        for user in users:
            users_listbox.insert(tk.END, user.username)

        def on_delete_user():
            selected_index = users_listbox.curselection()
            if selected_index:
                selected_user = users_listbox.get(selected_index)
                if selected_user == logged_in_user:
                    messagebox.showerror("Error", "You cannot delete your own account.")
                else:
                    if self.db_manager.delete_user(selected_user):
                        messagebox.showinfo("Success", f"User '{selected_user}' deleted successfully.")
                    else:
                        messagebox.showerror("Error", "Failed to delete user.")
                delete_user_window.destroy()

        delete_button = tk.Button(delete_user_window, text="Delete User", command=on_delete_user)
        delete_button.pack(pady=10)

    def view_users(self):
        view_users_window = tk.Toplevel()
        view_users_window.title("View Users")
        view_users_window.geometry("300x400")

        scrollbar = tk.Scrollbar(view_users_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        users_list = tk.Listbox(view_users_window, yscrollcommand=scrollbar.set)
        for user in self.db_manager.get_users():
            users_list.insert(tk.END, f"{user.username} ({user.role})")
        users_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=users_list.yview)

    def add_inventory_item(self):
        add_item_window = tk.Toplevel()
        add_item_window.title("Add Inventory Item")
        add_item_window.geometry("300x200")

        tk.Label(add_item_window, text="Item Name:").grid(row=0, column=0)
        item_name_entry = tk.Entry(add_item_window)
        item_name_entry.grid(row=0, column=1)

        tk.Label(add_item_window, text="Quantity:").grid(row=1, column=0)
        quantity_entry = tk.Entry(add_item_window)
        quantity_entry.grid(row=1, column=1)

        def submit():
            item_name = item_name_entry.get()
            quantity = int(quantity_entry.get())
            barcode = generate_ean13()
            if self.db_manager.add_inventory_item(item_name, quantity, barcode):
                generate_barcode(barcode, f"barcodes/{item_name}")
                messagebox.showinfo("Success", "Item added to inventory and barcode generated")
                add_item_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to add item")

        submit_button = tk.Button(add_item_window, text="Add Item", command=submit)
        submit_button.grid(row=2, column=0, columnspan=2, pady=10)

    def view_inventory(self):
        inventory_window = tk.Toplevel()
        inventory_window.title("Inventory List")
        inventory_window.geometry("300x400")

        scrollbar = tk.Scrollbar(inventory_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        inventory_list = tk.Listbox(inventory_window, yscrollcommand=scrollbar.set)
        for item in self.db_manager.get_inventory():
            inventory_list.insert(tk.END, f"{item.item_name}: {item.quantity} (Barcode: {item.barcode})")
        inventory_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=inventory_list.yview)

    def print_barcode_prompt(self):
        prompt_window = tk.Toplevel()
        prompt_window.title("Print Barcode")
        prompt_window.geometry("300x150")

        tk.Label(prompt_window, text="Enter barcode number to print:").pack(pady=10)
        barcode_entry = tk.Entry(prompt_window)
        barcode_entry.pack(pady=5)

        def on_print():
            barcode_number = barcode_entry.get()
            print_barcode(barcode_number)
            prompt_window.destroy()

        print_button = tk.Button(prompt_window, text="Print", command=on_print)
        print_button.pack(pady=10)

    def sign_in_out_item(self):
        sign_in_out_window = tk.Toplevel()
        sign_in_out_window.title("Sign In/Out Item")
        sign_in_out_window.geometry("300x200")

        tk.Label(sign_in_out_window, text="Item Name:").grid(row=0, column=0)
        item_name_entry = tk.Entry(sign_in_out_window)
        item_name_entry.grid(row=0, column=1)

        tk.Label(sign_in_out_window, text="Quantity (sign out as negative):").grid(row=1, column=0)
        quantity_entry = tk.Entry(sign_in_out_window)
        quantity_entry.grid(row=1, column=1)

        def submit():
            item_name = item_name_entry.get()
            quantity = int(quantity_entry.get())
            if self.db_manager.update_inventory_item(item_name, quantity):
                messagebox.showinfo("Success", "Inventory updated successfully")
            else:
                messagebox.showerror("Error", "Failed to update inventory. Check item name and quantity.")
            sign_in_out_window.destroy()

        submit_button = tk.Button(sign_in_out_window, text="Update Inventory", command=submit)
        submit_button.grid(row=2, column=0, columnspan=2)

def main():
    db_manager = DatabaseManager('inventory_management.db')
    app = InventoryApp(db_manager)
    app.main_window.mainloop()

if __name__ == "__main__":
    main()
