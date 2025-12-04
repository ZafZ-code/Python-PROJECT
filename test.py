import json
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from library import Book, Member , Emprunt # Your Book and Member classes

BOOKS_FILE = "books.json"
MEMBERS_FILE = "members.json"
EMPRUNTS_FILE = "emprunts.json"
RESERVATIONS_FILE = "reservations.json"

# ------------------ Load and Save Functions ------------------
def load_books():
    books = []
    try:
        with open(BOOKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for b in data:
                book = Book(b["ID"], b["TITLE"], b["AUTHOR"], b["ISBN"], b["YEAR"], b.get("DISPONIBILITY", True))
                books.append(book)
    except FileNotFoundError:
        pass
    # Sort books by ID descending (optional, newest first)
    books.sort(key=lambda x: x.id, reverse=True)
    return books

def load_members():
    members = []
    try:
        with open(MEMBERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for b in data:
                member = Member(b["id"], b["nom"], b["prenom"], b["email"], b["telephone"], b["date_inscription"])
                members.append(member)
    except FileNotFoundError:
        pass
    return members

def load_emprunts():
    emprunts = []
    try:
        with open(EMPRUNTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for b in data:
                emprunt = Emprunt(b["id_emprunt"], b["book_name"], b["member_name"], b["email"], b["date_emprunt"], b.get("status", "null"))
                emprunts.append(emprunt)
    except FileNotFoundError:
        pass
    # Sort books by ID descending (optional, newest first)
    emprunts.sort(key=lambda x: x.id_emprunt, reverse=True)
    return emprunts

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump([d.to_dict() if hasattr(d, "to_dict") else d for d in data], f, indent=4, ensure_ascii=False)

# ------------------ Initial Data ------------------
books = load_books()
members = load_members()
emprunts = load_emprunts()
#reservations = load_json(RESERVATIONS_FILE)

# ------------------ Login Window ------------------
login_window = tk.Tk()
login_window.title("Library Login")
login_window.geometry("300x180")
login_window.resizable(False, False)

tk.Label(login_window, text="Username:").pack(pady=5)
username_entry = tk.Entry(login_window)
username_entry.pack(pady=5)

tk.Label(login_window, text="Password:").pack(pady=5)
password_entry = tk.Entry(login_window, show="*")
password_entry.pack(pady=5)




# ------------------ Main Window ------------------
def open_main_window():
    root = tk.Tk()
    root.title("Library Management System")
    root.geometry("900x500")
    root.resizable(True, True)


    # ------------------ Tabs ------------------
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    tab_books = tk.Frame(notebook)
    tab_members = tk.Frame(notebook)
    tab_emprunts = tk.Frame(notebook)
    tab_reservations = tk.Frame(notebook)

    notebook.add(tab_books, text="Books")
    notebook.add(tab_members, text="Members")
    notebook.add(tab_emprunts, text="Emprunts")
    notebook.add(tab_reservations, text="Reservations")

    # ------------------ Books Tab ------------------
    columns_books = ("ID", "Title", "Author", "ISBN", "Year", "Disponibility")
    tree_books = ttk.Treeview(tab_books, columns=columns_books, show="headings")
    style = ttk.Style()
    style.configure("Treeview.Heading", background="#4a7abc", foreground="white", font=("Arial", 12, "bold"))

    for col in columns_books:
        tree_books.heading(col, text=col)
        tree_books.column(col, width=130, anchor=tk.CENTER)

    tree_books.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    scrollbar_books = ttk.Scrollbar(tab_books, orient=tk.VERTICAL, command=tree_books.yview)
    tree_books.configure(yscroll=scrollbar_books.set)
    scrollbar_books.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_books_table():
        for row in tree_books.get_children():
            tree_books.delete(row)
        for idx, book in enumerate(books):
            bg_color = "#2626cf" if idx % 2 == 0 else "#ffffff"
            tree_books.insert("", tk.END, values=(book.id, book.title, book.author, book.isbn, book.year, book.disponibility), tags=("row",))
            tree_books.tag_configure("row", background=bg_color)

    def add_book_gui():
        title = simpledialog.askstring("Title", "Enter title:")
        author = simpledialog.askstring("Author", "Enter author:")
        isbn = simpledialog.askstring("ISBN", "Enter ISBN:")
        year = simpledialog.askinteger("Year", "Enter year:")

        if not (title and author and isbn and year):
            messagebox.showerror("Error", "All fields must be filled!")
            return

        new_id = max([b.id for b in books], default=0) + 1
        new_book = Book(new_id, title, author, isbn, year)

        for b in books:
            if b.isbn == isbn:
                messagebox.showerror("Error", "ISBN already exists!")
                return

        books.insert(0, new_book)  # newest on top
        save_json(BOOKS_FILE, books)
        refresh_books_table()
        messagebox.showinfo("Success", "Book added successfully!")

    def delete_book_gui():
        selected_item = tree_books.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a book to delete")
            return
        item = tree_books.item(selected_item)
        book_id = item['values'][0]

        global books
        books = [b for b in books if b.id != book_id]
        save_json(BOOKS_FILE, books)
        refresh_books_table()
        messagebox.showinfo("Success", "Book deleted successfully!")

    btn_frame_books = tk.Frame(tab_books)
    btn_frame_books.pack(pady=10)
    tk.Button(btn_frame_books, bg="skyblue", text="Add Book", width=15, command=add_book_gui).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame_books, bg="skyblue", text="Delete Book", width=15, command=delete_book_gui).grid(row=0, column=1, padx=10)

    refresh_books_table()

    # ------------------ Members Tab ------------------
    columns_members = ("ID", "Nom", "Prénom", "Email", "Phone", "Date inscription")
    tree_members = ttk.Treeview(tab_members, columns=columns_members, show="headings")

    for col in columns_members:
        tree_members.heading(col, text=col)
        tree_members.column(col, width=130, anchor=tk.CENTER)

    tree_members.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    scrollbar_members = ttk.Scrollbar(tab_members, orient=tk.VERTICAL, command=tree_members.yview)
    tree_members.configure(yscroll=scrollbar_members.set)
    scrollbar_members.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_members_table():
        for row in tree_members.get_children():
            tree_members.delete(row)
        for idx, m in enumerate(members):
            bg_color = "#d61b1b" if idx % 2 == 0 else "#ffffff"
            tree_members.insert("", tk.END, values=(m.id, m.nom, m.prenom, m.email, m.telephone, m.date_inscription), tags=("row",))
            tree_members.tag_configure("row", background=bg_color)

    def add_member_gui():
        nom = simpledialog.askstring("Nom", "Enter Nom:")
        prenom = simpledialog.askstring("Prénom", "Enter Prénom:")
        email = simpledialog.askstring("Email", "Enter Email:")
        phone = simpledialog.askstring("Phone", "Enter Phone:")
        date_inscription = simpledialog.askstring("Date", "Enter Date inscription (YYYY-MM-DD):")

        if not (nom and prenom and email and phone and date_inscription):
            messagebox.showerror("Error", "All fields must be filled!")
            return

        new_id = max([m.id for m in members], default=0) + 1
        new_member = Member(new_id, nom, prenom, email, phone, date_inscription)
        members.insert(0, new_member)
        save_json(MEMBERS_FILE, members)
        refresh_members_table()
        messagebox.showinfo("Success", "Member added successfully!")

    def delete_member_gui():
        selected_item = tree_members.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a member to delete")
            return
        item = tree_members.item(selected_item)
        member_id = item['values'][0]

        global members
        members = [m for m in members if m.id != member_id]
        save_json(MEMBERS_FILE, members)
        refresh_members_table()
        messagebox.showinfo("Success", "Member deleted successfully!")

    btn_frame_members = tk.Frame(tab_members)
    btn_frame_members.pack(pady=10)
    tk.Button(btn_frame_members, bg="skyblue", text="Add Member", width=15, command=add_member_gui).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame_members, bg="skyblue", text="Delete Member", width=15, command=delete_member_gui).grid(row=0, column=1, padx=10)

    refresh_members_table()

    # ------------------ Emprunts Tab ------------------
    columns_emprunts = ("ID Emprunt", "Book Name", "Member Name", "Email", "Date Emprunt", "Status")
    tree_emprunts = ttk.Treeview(tab_emprunts, columns=columns_emprunts, show="headings")

    for col in columns_emprunts:
        tree_emprunts.heading(col, text=col)
        tree_emprunts.column(col, width=150, anchor=tk.CENTER)

    tree_emprunts.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    scrollbar_emprunts = ttk.Scrollbar(tab_emprunts, orient=tk.VERTICAL, command=tree_emprunts.yview)
    tree_emprunts.configure(yscroll=scrollbar_emprunts.set)
    scrollbar_emprunts.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_emprunts_table():
        for row in tree_emprunts.get_children():
            tree_emprunts.delete(row)
        for idx, e in enumerate(emprunts):
            bg_color = "#00ff40" if idx % 2 == 0 else "#ffffff"
            tree_emprunts.insert("", tk.END, values=(e.id_emprunt, e.book_name, e.member_name, e.email, e.date_emprunt, e.status), tags=("row",))
            tree_emprunts.tag_configure("row", background=bg_color)

    def add_emprunt_gui():
        
        member_name = simpledialog.askinteger("Member Name", "Enter Member Name:")
        member_last_name= simpledialog.askstring("Member Last Name", "Enter Member Last Name:")
        book_name = simpledialog.askinteger("Book Name", "Enter Book Name:")
        email= simpledialog.askstring("Email", "Enter Email:")
        date_emprunt = simpledialog.askstring("Date Emprunt", "Enter Date Emprunt (YYYY-MM-DD):")
        status = simpledialog.askstring("Status", "Enter Status:")

        if not (member_name and book_name and date_emprunt ):
            messagebox.showerror("Error", "All fields must be filled!")
            return

        new_id = max([e.id_emprunt for e in emprunts], default=0) + 1
        new_emprunt = Emprunt(new_id, book_name, member_name, member_last_name, email, date_emprunt, status)
        emprunts.insert(0, new_emprunt)
        save_json(EMPRUNTS_FILE, emprunts)
        refresh_emprunts_table()
        messagebox.showinfo("Success", "Emprunt added successfully!")

    def delete_emprunt_gui():
        selected_item = tree_emprunts.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select an emprunt to delete")
            return
        item = tree_emprunts.item(selected_item)
        emprunt_id = item['values'][0]

        global emprunts
        emprunts = [e for e in emprunts if e.id_emprunt != emprunt_id]
        save_json(EMPRUNTS_FILE, emprunts)
        refresh_emprunts_table()
        messagebox.showinfo("Success", "Emprunt deleted successfully!")

    btn_frame_emprunts = tk.Frame(tab_emprunts)
    btn_frame_emprunts.pack(pady=10)
    tk.Button(btn_frame_emprunts, bg="skyblue", text="Add Emprunt", width=15, command=add_emprunt_gui).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame_emprunts, bg="skyblue", text="Delete Emprunt", width=15, command=delete_emprunt_gui).grid(row=0, column=1, padx=10)

    refresh_emprunts_table()

    # ------------------ Reservations Tab ------------------
"""
    columns_reservations = ("ID Reservation", "Member ID", "Book ID", "Date Reservation")
    tree_reservations = ttk.Treeview(tab_reservations, columns=columns_reservations, show="headings")

    for col in columns_reservations:
        tree_reservations.heading(col, text=col)
        tree_reservations.column(col, width=150, anchor=tk.CENTER)

    tree_reservations.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    scrollbar_reservations = ttk.Scrollbar(tab_reservations, orient=tk.VERTICAL, command=tree_reservations.yview)
    tree_reservations.configure(yscroll=scrollbar_reservations.set)
    scrollbar_reservations.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_reservations_table():
        for row in tree_reservations.get_children():
            tree_reservations.delete(row)
        for idx, r in enumerate(reservations):
            bg_color = "#f0f0ff" if idx % 2 == 0 else "#ffffff"
            tree_reservations.insert("", tk.END, values=(r["id_reservation"], r["member_id"], r["book_id"], r["date_reservation"]), tags=("row",))
            tree_reservations.tag_configure("row", background=bg_color)

    def add_reservation_gui():
        member_id = simpledialog.askinteger("Member ID", "Enter Member ID:")
        book_id = simpledialog.askinteger("Book ID", "Enter Book ID:")
        date_reservation = simpledialog.askstring("Date Reservation", "Enter Date Reservation (YYYY-MM-DD):")

        if not (member_id and book_id and date_reservation):
            messagebox.showerror("Error", "All fields must be filled!")
            return

        new_id = max([r["id_reservation"] for r in reservations], default=0) + 1
        new_reservation = {"id_reservation": new_id, "member_id": member_id, "book_id": book_id, "date_reservation": date_reservation}
        reservations.insert(0, new_reservation)
        save_json(RESERVATIONS_FILE, reservations)
        refresh_reservations_table()
        messagebox.showinfo("Success", "Reservation added successfully!")

    def delete_reservation_gui():
        selected_item = tree_reservations.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a reservation to delete")
            return
        item = tree_reservations.item(selected_item)
        reservation_id = item['values'][0]

        global reservations
        reservations = [r for r in reservations if r["id_reservation"] != reservation_id]
        save_json(RESERVATIONS_FILE, reservations)
        refresh_reservations_table()
        messagebox.showinfo("Success", "Reservation deleted successfully!")

    btn_frame_reservations = tk.Frame(tab_reservations)
    btn_frame_reservations.pack(pady=10)
    tk.Button(btn_frame_reservations, bg="skyblue", text="Add Reservation", width=15, command=add_reservation_gui).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame_reservations, bg="skyblue", text="Delete Reservation", width=15, command=delete_reservation_gui).grid(row=0, column=1, padx=10)

    refresh_reservations_table()
"""
def login():
    username = username_entry.get()
    password = password_entry.get()
    if username == "admin" and password == "admin":
        login_window.destroy()
        open_main_window()
    else:
        messagebox.showerror("Error", "Incorrect login or password!")

tk.Button(login_window, text="Login", width=10, command=login).pack(pady=15)

login_window.mainloop()



#___________________________________________code des class______________________________________________________
from datetime import datetime 
class Book:
    def __init__(self, id, title, author, isbn, year, disponibility=False):
        self.id=id
        self.title=title
        self.author=author
        self.isbn=isbn
        self.year=year
        self.disponibility=disponibility
    def __str__(self):
        return f"ID: {self.id}, Title: {self.title}, Author: {self.author}, ISBN: {self.isbn}, Year: {self.year}, Disponibility: {self.disponibility}"
    def delete(self):
        del self
    def add (self, book_list):
        for b in book_list:
            if (b.id == self.id or b.isbn == self.isbn):
                return "book with this ID or ISBN already exists."
        book_list.append(self)
    def search_by_title(self, book_list, title):
        return[book for book in book_list if book.title == title ]
    def search_by_author(self, book_list, author):
        return[book for book in book_list if book.author == author ]
    def search_by_isbn(self, book_list, isbn):
        return[book for book in book_list if book.isbn == isbn ]
    def to_dict(self):
        return {
            "ID" : self.id,
            "TITLE" : self.title,
            "AUTHOR" : self.author,
            "ISBN" : self.isbn,
            "YEAR" : self.year,
            "DISPONIBILITY" : self.disponibility
        }
class Member:
    def __init__(self,nom,prenom, email,telephone, date_inscription ,id_member):
        self.nom=nom
        self.prenom=prenom
        self.email=email
        self.telephone=telephone
        self.date_inscription =date_inscription 
        self.id_member=id_member
    def user_to_dict(self):
        return {
            "ID" : self.id_member,
            "LAST NAME" : self.nom,
            "FIRST NAME" : self.prenom,
            "EMAIL" : self.email,
            "PHONE" : self.telephone,
            "REGISTRATION DATE" : self.date_inscription,
            
        }
class Emprunt:
    def __init__(self, id_emprunt, book_name, member_name, email, date_emprunt, status= "null"):
        self.id_emprunt=id_emprunt
        self.book_name=book_name
        self.member_name=member_name
        self.email=email
        self.date_emprunt=date_emprunt
        self.status=status
    def verifie_itsmember(self,member_list):
        for member in member_list:
            if member.name==self.member_name and member.email == self.email:
                return True
        return False 
    def verifie_bookdisponibility(self, book_list):
        for book in book_list:
            if book_list.title == self.book_name and book_list.disponibility == True:
                return True 
        return False 
    def Reclamation (self):
        d= datetime.strptime(self.date_emprunt, "%Y-%m-%d").date()
        today = datetime.today().date()
        difference_days=(today -d).days
        if self.status == "null" and difference_days > 14:
            return "Reclamation needed "
        

    def emprunt_to_dict(self):
        return {
            "ID EMPRUNT" : self.id_emprunt,
            "BOOK NAME" : self.book_name,
            "MEMBER NAME" : self.member_name,
            "EMAIL" : self.email,
            "DATE EMPRUNT" : self.date_emprunt,
            "STATUS" : self.status
        }
#____________________________________________autre code interface en tkinter__________________
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