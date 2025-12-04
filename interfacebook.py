# interface.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry  # pip install tkcalendar
from library import LibraryManager, BOOKS_FILE, MEMBERS_FILE, EMPRUNTS_FILE, DATEFMT
from datetime import datetime

# initialise manager
mgr = LibraryManager()


def format_book_row(book):
    return (book.title, book.author, book.isbn, book.year, str(book.disponibility), ", ".join(book.reservations))


def format_member_row(member):
    return (member.nom, member.prenom, member.email, member.phone, member.date_inscription)


def format_emprunt_row(e):
    return (e.emprunt_id, e.book_isbn, e.member_email, e.date_emprunt, e.date_due, e.date_return or "", e.status)


app = tk.Tk()
app.title("Gestion Bibliothèque")
app.geometry("1000x650")

nb = ttk.Notebook(app)
nb.pack(fill="both", expand=True)

# --- Books Tab ---
tab_books = ttk.Frame(nb)
nb.add(tab_books, text="Livres")

books_cols = ("Titre", "Auteur", "ISBN", "Année", "Disponible", "Réservations")
tree_books = ttk.Treeview(tab_books, columns=books_cols, show="headings")
for c in books_cols:
    tree_books.heading(c, text=c)
    tree_books.column(c, width=140)
tree_books.pack(fill="both", expand=True, padx=10, pady=10)

def refresh_books():
    for r in tree_books.get_children():
        tree_books.delete(r)
    for b in mgr.books.values():
        tree_books.insert("", "end", values=format_book_row(b))

def add_book_window():
    w = tk.Toplevel(app)
    w.title("Ajouter un livre")
    labels = ["Titre","Auteur","ISBN","Année"]
    entries = {}
    for i,l in enumerate(labels):
        tk.Label(w, text=l).grid(row=i, column=0, padx=5, pady=5)
        ent = tk.Entry(w)
        ent.grid(row=i, column=1, padx=5, pady=5)
        entries[l]=ent
    def on_add():
        try:
            mgr.add_book(entries["Titre"].get(), entries["Auteur"].get(), entries["ISBN"].get(), entries["Année"].get())
            refresh_books()
            w.destroy()
        except Exception as ex:
            messagebox.showerror("Erreur", str(ex))
    tk.Button(w, text="Ajouter", command=on_add).grid(row=len(labels), column=0, columnspan=2, pady=8)

def delete_book():
    sel = tree_books.selection()
    if not sel:
        messagebox.showwarning("Info", "Sélectionnez un livre")
        return
    vals = tree_books.item(sel[0])["values"]
    isbn = vals[2]
    try:
        mgr.remove_book(isbn)
        refresh_books()
        messagebox.showinfo("OK", "Livre supprimé")
    except Exception as ex:
        messagebox.showerror("Erreur", str(ex))

btn_frame_books = tk.Frame(tab_books)
btn_frame_books.pack(pady=6)
tk.Button(btn_frame_books, text="Ajouter livre", command=add_book_window).pack(side="left", padx=6)
tk.Button(btn_frame_books, text="Supprimer livre", command=delete_book).pack(side="left", padx=6)
tk.Button(btn_frame_books, text="Rechercher", command=lambda: search_book_window()).pack(side="left", padx=6)

def search_book_window():
    q = simpledialog.askstring("Recherche livre", "Titre / Auteur / ISBN :")
    if not q:
        return
    res = mgr.search_books(q)
    txt = "\n".join([f"{b.title} — {b.author} — {b.isbn} — {'dispo' if b.disponibility else 'emprunté'}" for b in res]) or "Aucun résultat"
    messagebox.showinfo("Résultats", txt)

# --- Members Tab ---
tab_members = ttk.Frame(nb)
nb.add(tab_members, text="Membres")

mem_cols = ("Nom","Prénom","Email","Téléphone","Date inscription")
tree_members = ttk.Treeview(tab_members, columns=mem_cols, show="headings")
for c in mem_cols:
    tree_members.heading(c, text=c)
    tree_members.column(c, width=160)
tree_members.pack(fill="both", expand=True, padx=10, pady=10)

def refresh_members():
    for r in tree_members.get_children():
        tree_members.delete(r)
    for m in mgr.list_members():
        tree_members.insert("", "end", values=format_member_row(m))

def add_member_window():
    w = tk.Toplevel(app)
    w.title("Ajouter membre")
    labels = ["Nom","Prénom","Email","Téléphone"]
    entries = {}
    for i,l in enumerate(labels):
        tk.Label(w, text=l).grid(row=i, column=0, padx=5, pady=5)
        ent = tk.Entry(w)
        ent.grid(row=i, column=1, padx=5, pady=5)
        entries[l]=ent
    def on_add():
        try:
            mgr.add_member(entries["Nom"].get(), entries["Prénom"].get(), entries["Email"].get(), entries["Téléphone"].get())
            refresh_members()
            w.destroy()
        except Exception as ex:
            messagebox.showerror("Erreur", str(ex))
    tk.Button(w, text="Ajouter", command=on_add).grid(row=len(labels), column=0, columnspan=2, pady=8)

def delete_member():
    sel = tree_members.selection()
    if not sel:
        messagebox.showwarning("Info", "Sélectionnez un membre")
        return
    vals = tree_members.item(sel[0])["values"]
    email = vals[2]
    try:
        mgr.remove_member(email)
        refresh_members()
        messagebox.showinfo("OK", "Membre supprimé")
    except Exception as ex:
        messagebox.showerror("Erreur", str(ex))

btn_frame_mem = tk.Frame(tab_members)
btn_frame_mem.pack(pady=6)
tk.Button(btn_frame_mem, text="Ajouter membre", command=add_member_window).pack(side="left", padx=6)
tk.Button(btn_frame_mem, text="Supprimer membre", command=delete_member).pack(side="left", padx=6)

# --- Emprunts Tab ---
tab_emprunts = ttk.Frame(nb)
nb.add(tab_emprunts, text="Emprunts")

emp_cols = ("ID","ISBN","Email membre","Date emprunt","Date due","Date retour","Statut")
tree_emprunts = ttk.Treeview(tab_emprunts, columns=emp_cols, show="headings")
for c in emp_cols:
    tree_emprunts.heading(c, text=c)
    tree_emprunts.column(c, width=140)
tree_emprunts.pack(fill="both", expand=True, padx=10, pady=10)

def refresh_emprunts():
    for r in tree_emprunts.get_children():
        tree_emprunts.delete(r)
    for e in mgr.emprunts.values():
        tree_emprunts.insert("", "end", values=format_emprunt_row(e))

def borrow_window():
    w = tk.Toplevel(app)
    w.title("Emprunter un livre")
    labels = ["ISBN du livre","Email du membre","Durée (jours)"]
    entries = {}
    for i,l in enumerate(labels):
        tk.Label(w, text=l).grid(row=i, column=0, padx=5, pady=5)
        if l == "Date emprunt":
            ent = DateEntry(w)
        else:
            ent = tk.Entry(w)
        ent.grid(row=i, column=1, padx=5, pady=5)
        entries[l] = ent

    def on_borrow():
        isbn = entries["ISBN du livre"].get()
        email = entries["Email du membre"].get()
        try:
            days = int(entries["Durée (jours)"].get() or 14)
        except:
            days = 14
        try:
            res = mgr.borrow_book(isbn, email, days)
            if isinstance(res, dict) and res.get("reserved"):
                messagebox.showinfo("Réservé", "Le livre n'est pas disponible: vous avez été ajouté(e) à la file de réservation.")
            else:
                messagebox.showinfo("OK", f"Emprunt créé. ID: {res.emprunt_id}")
            refresh_books(); refresh_emprunts()
            w.destroy()
        except Exception as ex:
            messagebox.showerror("Erreur", str(ex))
    tk.Button(w, text="Emprunter", command=on_borrow).grid(row=len(labels), column=0, columnspan=2, pady=8)

def return_window():
    w = tk.Toplevel(app)
    w.title("Retour livre")
    tk.Label(w, text="ID emprunt").grid(row=0, column=0, padx=5, pady=5)
    ent = tk.Entry(w); ent.grid(row=0, column=1, padx=5, pady=5)
    def on_return():
        empr_id = ent.get()
        try:
            empr = mgr.return_book(empr_id)
            messagebox.showinfo("OK", f"Livre retourné. Date retour: {empr.date_return}")
            # if there are reservations, inform who is next
            book = mgr.books.get(empr.book_isbn)
            if book and book.reservations:
                next_email = book.reservations[0]
                messagebox.showinfo("Réservation", f"Le livre est réservé au membre: {next_email}")
            refresh_books(); refresh_emprunts()
            w.destroy()
        except Exception as ex:
            messagebox.showerror("Erreur", str(ex))
    tk.Button(w, text="Retourner", command=on_return).grid(row=1, column=0, columnspan=2, pady=8)

btn_frame_emp = tk.Frame(tab_emprunts)
btn_frame_emp.pack(pady=6)
tk.Button(btn_frame_emp, text="Emprunter", command=borrow_window).pack(side="left", padx=6)
tk.Button(btn_frame_emp, text="Retour", command=return_window).pack(side="left", padx=6)

# --- Reservations Tab ---
tab_res = ttk.Frame(nb)
nb.add(tab_res, text="Réservations")

res_cols = ("ISBN","Titre","Queue (emails)")
tree_res = ttk.Treeview(tab_res, columns=res_cols, show="headings")
for c in res_cols:
    tree_res.heading(c, text=c)
    tree_res.column(c, width=300)
tree_res.pack(fill="both", expand=True, padx=10, pady=10)

def refresh_reservations():
    for r in tree_res.get_children():
        tree_res.delete(r)
    for b in mgr.books.values():
        if b.reservations:
            tree_res.insert("", "end", values=(b.isbn, b.title, ", ".join(b.reservations)))

def reserve_window():
    w = tk.Toplevel(app)
    w.title("Réserver un livre")
    tk.Label(w, text="ISBN").grid(row=0, column=0, padx=5, pady=5)
    e1 = tk.Entry(w); e1.grid(row=0, column=1)
    tk.Label(w, text="Email membre").grid(row=1, column=0, padx=5, pady=5)
    e2 = tk.Entry(w); e2.grid(row=1, column=1)
    def on_reserve():
        try:
            mgr.reserve_book(e1.get(), e2.get())
            messagebox.showinfo("OK","Réservation enregistrée")
            refresh_reservations()
            w.destroy()
        except Exception as ex:
            messagebox.showerror("Erreur", str(ex))
    tk.Button(w, text="Réserver", command=on_reserve).grid(row=2, column=0, columnspan=2, pady=6)

btn_frame_res = tk.Frame(tab_res)
btn_frame_res.pack(pady=6)
tk.Button(btn_frame_res, text="Nouveau réservation", command=reserve_window).pack(side="left", padx=6)
tk.Button(btn_frame_res, text="Refresh", command=refresh_reservations).pack(side="left", padx=6)

# --- Reports Tab ---
tab_reports = ttk.Frame(nb)
nb.add(tab_reports, text="Rapports")

txt_report = tk.Text(tab_reports, wrap="word")
txt_report.pack(fill="both", expand=True, padx=10, pady=10)

def refresh_reports():
    st = mgr.stats()
    lines = []
    lines.append(f"Total livres: {st['total_books']}")
    lines.append(f"Total membres: {st['total_members']}")
    lines.append(f"Total emprunts (historique): {st['total_emprunts']}")
    lines.append("\nTop 5 livres les plus empruntés:")
    for b in st["top_books"]:
        lines.append(f" - {b.title} ({b.borrow_count} emprunts)")
    lines.append("\nTop membres (par nombre d'emprunts):")
    for email, ct in st["top_members"]:
        member = mgr.members.get(email)
        name = f"{member.prenom} {member.nom}" if member else email
        lines.append(f" - {name} ({ct})")
    lines.append("\nEmprunts en cours:")
    for e in st["currently_borrowed"]:
        lines.append(f" - ID {e.emprunt_id} | {e.book_isbn} | {e.member_email} | due {e.date_due}")
    txt_report.delete("1.0", "end")
    txt_report.insert("1.0", "\n".join(lines))

btn_frame_rep = tk.Frame(tab_reports)
btn_frame_rep.pack(pady=6)
tk.Button(btn_frame_rep, text="Générer rapport", command=refresh_reports).pack(side="left", padx=6)

# --- Utility refresh on start and buttons ---
def refresh_all():
    refresh_books()
    refresh_members()
    refresh_emprunts()
    refresh_reservations()
    refresh_reports()

tk.Button(app, text="Refresh tout", command=refresh_all).pack(side="bottom", pady=6)

# Show overdue warnings at startup
def show_overdue_startup():
    overdue = mgr.overdue_emprunts()
    if overdue:
        lines = []
        for e in overdue:
            lines.append(f"ID: {e.emprunt_id} | ISBN: {e.book_isbn} | Membre: {e.member_email} | due: {e.date_due}")
        messagebox.showwarning("Emprunts en retard", "\n".join(lines))

# initial load
refresh_all()
app.after(500, show_overdue_startup)

# quit button
def on_quit():
    mgr._save_all()
    app.destroy()

app.protocol("WM_DELETE_WINDOW", on_quit)
app.mainloop()
