import tkinter as tk
from tkinter import ttk, messagebox
import requests
import database as db

API_URL = "http://127.0.0.1:5000"
db.setup_database()

# ---------------- Helper Functions ----------------
def refresh_status():
    response = requests.get(f"{API_URL}/api/status").json()
    status_label.config(text=f"Ship Capacity: {response['capacity']} | Used: {response['used']} | Remaining: {response['remaining']}")
    update_table()

def update_table():
    for item in table.get_children():
        table.delete(item)
    data = requests.get(f"{API_URL}/api/containers").json()
    for row in data:
        table.insert("", tk.END, values=row)

def add_container():
    name = name_entry.get()
    weight = weight_entry.get()
    dest = dest_entry.get()
    type_ = type_combo.get()
    if not (name and weight and dest and type_):
        messagebox.showwarning("Input Error", "All fields required!")
        return
    try:
        weight = float(weight)
    except ValueError:
        messagebox.showerror("Error", "Weight must be numeric")
        return

    response = requests.post(f"{API_URL}/api/container", json={
        "name": name,
        "weight": weight,
        "destination": dest,
        "type": type_
    })

    if response.status_code == 201:
        messagebox.showinfo("Success", "Container added successfully!")
        refresh_status()

# ---------------- New Feature: Load Plan ----------------
def calculate_load_plan():
    """Determine which containers can be shipped given remaining capacity"""
    try:
        status = requests.get(f"{API_URL}/api/status").json()
        remaining_capacity = status["remaining"]

        containers = requests.get(f"{API_URL}/api/containers").json()
        if not containers:
            messagebox.showinfo("Load Plan", "No containers available!")
            return

        # Sort by weight (smallest first)
        containers.sort(key=lambda x: x[2])

        total_loaded = 0
        loaded_containers = []
        skipped_containers = []

        for c in containers:
            cid, name, weight, dest, type_ = c
            if total_loaded + weight <= remaining_capacity:
                total_loaded += weight
                loaded_containers.append(f"{name} ({weight}kg) → {dest}")
            else:
                skipped_containers.append(f"{name} ({weight}kg) → {dest}")

        msg = f"🟢 Containers that can go:\n\n" + "\n".join(loaded_containers) if loaded_containers else "No containers fit."
        msg += "\n\n🔴 Containers that exceed capacity:\n\n" + "\n".join(skipped_containers) if skipped_containers else ""
        msg += f"\n\nTotal Loadable Weight: {total_loaded} / Remaining: {remaining_capacity}"

        messagebox.showinfo("Load Plan Result", msg)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to calculate plan: {e}")

# ---------------- New Feature: Delete All Containers ----------------
def delete_all_containers():
    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete ALL containers?")
    if not confirm:
        return
    try:
        response = requests.delete(f"{API_URL}/api/containers")
        if response.status_code == 200:
            messagebox.showinfo("Deleted", "All containers deleted successfully!")
            refresh_status()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete containers: {e}")

# ---------------- GUI Layout ----------------
root = tk.Tk()
root.title("🚢 Container Ship Loading System")
root.geometry("900x550")
root.config(bg="#e8f4f8")

frame = tk.Frame(root, bg="#e8f4f8")
frame.pack(pady=20)

tk.Label(frame, text="Container Name:").grid(row=0, column=0)
name_entry = tk.Entry(frame)
name_entry.grid(row=0, column=1)

tk.Label(frame, text="Weight (kg):").grid(row=1, column=0)
weight_entry = tk.Entry(frame)
weight_entry.grid(row=1, column=1)

tk.Label(frame, text="Destination:").grid(row=2, column=0)
dest_entry = tk.Entry(frame)
dest_entry.grid(row=2, column=1)

tk.Label(frame, text="Type:").grid(row=3, column=0)
type_combo = ttk.Combobox(frame, values=["Food", "Electronics", "Machinery", "Clothing"])
type_combo.grid(row=3, column=1)

# Buttons
btn_frame = tk.Frame(root, bg="#e8f4f8")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Add Container", command=add_container, bg="#4CAF50", fg="white", width=18).grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text="Calculate Load Plan", command=calculate_load_plan, bg="#2196F3", fg="white", width=18).grid(row=0, column=1, padx=10)
tk.Button(btn_frame, text="Delete All Containers", command=delete_all_containers, bg="#F44336", fg="white", width=18).grid(row=0, column=2, padx=10)

# Status + Table
status_label = tk.Label(root, text="", font=("Arial", 12, "bold"), bg="#e8f4f8")
status_label.pack(pady=5)

table = ttk.Treeview(root, columns=("ID", "Name", "Weight", "Destination", "Type"), show="headings")
for col in ("ID", "Name", "Weight", "Destination", "Type"):
    table.heading(col, text=col)
table.pack(fill="both", expand=True, padx=10, pady=10)

refresh_status()
root.mainloop()
