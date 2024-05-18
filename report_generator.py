from database import DatabaseManager
from tkinter import messagebox

def generate_report():
    db_manager = DatabaseManager('inventory_management.db')
    report = []
    report.append("Inventory Report\n")
    report.append("================\n")
    items = db_manager.get_inventory()
    for item in items:
        report.append(f"Item: {item.item_name}, Quantity: {item.quantity}, Barcode: {item.barcode}\n")
    
    report.append("\nUser Activity Log\n")
    report.append("=================\n")
    with open('inventory_management.log', 'r') as log_file:
        logs = log_file.readlines()
        report.extend(logs)

    with open('report.txt', 'w') as report_file:
        report_file.writelines(report)
    messagebox.showinfo("Report Generated", "The report has been generated as 'report.txt'")
