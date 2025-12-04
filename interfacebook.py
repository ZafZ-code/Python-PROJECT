import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from library import Book, Member, Emprunt

BOOKS_FILE = "books.json"
MEMBERS_FILE = "members.json"
EMPRUNTS_FILE = "emprunts.json"

#___________laod and save functions___________

def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

#___________window setup___________
def open_add_window(parent, columns, filename, tree):
    win = tk.Toplevel(parent)
    win.title("Add New Entry")
    win.geometry("800x500")

    entries = {}

    for i, col in enumerate(columns):
        tk.Label(win, text=col).grid(row=i, column=0, padx=5, pady=5, sticky="w")
        e = tk.Entry(win)
        e.grid(row=i, column=1, padx=5, pady=5)
        entries[col] = e

    def save_new_entry():
        data = load_json(filename)

        new_item = {c: entries[c].get() for c in columns}
        if any(v.strip() == "" for v in new_item.values()):
            messagebox.showwarning("Warning", "All fields must be filled!")
            return

        data.append(new_item)
        save_json(filename, data)

        tree.insert("", "end", values=[new_item[c] for c in columns])
        win.destroy()

    tk.Button(win, text="Save", command=save_new_entry).grid(
        row=len(columns), column=0, columnspan=2, pady=15
    )


# ---------------------------
# Delete Function
# ---------------------------

def delete_selected(tree, filename, columns):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select an item to delete.")
        return

    values = tree.item(selected[0])["values"]
    key_data = {columns[i]: values[i] for i in range(len(columns))}

    data = load_json(filename)
    new_data = [
        d for d in data
        if not all(str(d[c]) == str(key_data[c]) for c in columns)
    ]

    save_json(filename, new_data)
    tree.delete(selected[0])


# ---------------------------
# Create Tab
# ---------------------------

def create_tab(notebook, name, filename, parent):
    frame = tk.Frame(notebook)
    notebook.add(frame, text=name)

    data = load_json(filename)
    columns = list(data[0].keys()) if data else []

    # ---------- TREEVIEW STYLE WITH COLORED HEADERS ----------
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading",
                    background="#2ecc71",   # green
                    foreground="white",     # white text
                    font=("Arial", 12, "bold"))

    # --- NORMAL TABLE ROWS ---
    style.configure("Treeview",
                    font=("Arial", 11),
                    rowheight=25)

    # --- MAKE GRID LINES VISIBLE ---
    style.map("Treeview",
            background=[("selected", "#27ae60")],   # darker green on select
            foreground=[("selected", "white")])

    # Force border lines
    style.layout("Treeview", [
        ('Treeview.treearea', {'sticky': 'nswe'})])
    style.map("Treeview.Heading",
          background=[("active", "#ADD8E6"), ("pressed", "#ADD8E6"), ("!active", "#ADD8E6")],
          foreground=[("active", "black"), ("pressed", "black"), ("!active", "black")],
          relief=[("active", "flat"), ("pressed", "flat"), ("!active", "flat")])

    tree = ttk.Treeview(
    frame,
    columns=columns,
    show="headings",
    style="Treeview"
)
        # Configure colored headers
    for col in columns:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, width=140, anchor="center")

    # Insert data
    for row in data:
        tree.insert("", "end", values=[row[c] for c in columns])

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------- BOTTOM BUTTONS ----------
    btn_frame = tk.Frame(frame)
    btn_frame.pack(pady=10)

    btn_add = tk.Button(
        btn_frame,
        text="Add",
        width=15,
        bg="#52ab98",
        fg="white",
        font=("Arial", 11, "bold"),
        command=lambda: open_add_window(parent, columns, filename, tree)
    )
    btn_add.grid(row=0, column=0, padx=15)

    btn_delete = tk.Button(
        btn_frame,
        text="Delete",
        width=15,
        bg="#c72c41",
        fg="white",
        font=("Arial", 11, "bold"),
        command=lambda: delete_selected(tree, filename, columns)
    )
    btn_delete.grid(row=0, column=1, padx=15)

    return frame


# ---------------------------
# MAIN WINDOW
# ---------------------------

root = tk.Tk()
root.title("Library Manager")
root.geometry("1100x700")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

create_tab(notebook, "Books", BOOKS_FILE, root)
create_tab(notebook, "Members", MEMBERS_FILE, root)
create_tab(notebook, "Emprunts", EMPRUNTS_FILE, root)

root.mainloop()