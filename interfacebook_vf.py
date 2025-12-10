

import tkinter as tk
from tkinter import ttk,  simpledialog
from tkcalendar import DateEntry  
from library import LibraryManager, BOOKS_FILE, MEMBERS_FILE, EMPRUNTS_FILE, DATEFMT
from datetime import datetime,timedelta
import csv

from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import os 
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdfcanvas


mgr = LibraryManager()

BUTTON_BG = "#2a6fdb" 
BUTTON_FG = "white"   
HEADER_BG = "#0077c9"  
HEADER_FG = "white"
PRIMARY_COLOR = "#4CAF50" 
DANGER_COLOR = "#E53935"

def format_book_row(book):
   
    dispo_text = f"{book.disponibility} {'✔️' if book.disponibility else '❌'}"
    return (
        book.title,
        book.author,
        book.isbn,
        book.year,
        dispo_text,
        book.borrow_count,
        ", ".join(book.reservations)
    )


def format_member_row(member):
    return (member.nom, member.prenom, member.email, member.phone, member.date_inscription)


def format_emprunt_row(e):
    return (e.emprunt_id, e.book_isbn, e.member_email, e.date_emprunt, e.date_due, e.date_return or "", e.status)


app = tk.Tk()
app.title("Gestion Bibliothèque")
app.geometry("1000x650")

style = ttk.Style(app)
style.theme_use('default')


style.configure("Treeview.Heading", 
                background=HEADER_BG, 
                foreground=HEADER_FG, 
                font=('Arial', 10, 'bold'))

style.configure("Treeview", 
                rowheight=25)

nb = ttk.Notebook(app)
nb.pack(fill="both", expand=True)


tab_books = ttk.Frame(nb)
nb.add(tab_books, text="Livres")

frame_counters_books = tk.Frame(tab_books)
frame_counters_books.pack(fill="x", pady=5)

lbl_total_books = tk.Label(frame_counters_books, text="📘 Total livres : 0",
                           font=("Arial", 11, "bold"), fg="#2196F3")
lbl_total_books.pack(side="left", padx=20)

lbl_dispo_books = tk.Label(frame_counters_books, text="📕 Disponibles : 0",
                           font=("Arial", 11, "bold"), fg="#4CAF50")
lbl_dispo_books.pack(side="left", padx=20)

lbl_empruntes_books = tk.Label(frame_counters_books, text="🔒 Empruntés : 0",
                               font=("Arial", 11, "bold"), fg="#E53935")
lbl_empruntes_books.pack(side="left", padx=20)

books_cols = ("Titre", "Auteur", "ISBN", "Année", "Disponible", "N° Emprunte", "Réservations")
tree_books = ttk.Treeview(tab_books, columns=books_cols, show="headings")
for c in books_cols:
    tree_books.heading(c, text=c, anchor="center")
    tree_books.column(c, width=140, anchor="center")
tree_books.pack(fill="both", expand=True, padx=10, pady=10)


filter_frame = tk.Frame(tab_books)
filter_frame.pack(pady=10)

tk.Label(filter_frame, text="Filtrer par disponibilité :").pack(side="left", padx=6)

filter_var = tk.StringVar()
filter_combobox = ttk.Combobox(filter_frame, textvariable=filter_var, values=["Tous", "Disponible", "Emprunté"])
filter_combobox.set("Tous")  
filter_combobox.pack(side="left", padx=6)


def filter_books():
    selected_filter = filter_var.get()
    refresh_books(selected_filter)  
filter_combobox.bind("<<ComboboxSelected>>", lambda e: filter_books()) 



def refresh_books(selected_filter="Tous"):
    for r in tree_books.get_children():
        tree_books.delete(r)
    
    
    for b in mgr.books.values():
        if selected_filter == "Tous":
            tree_books.insert("", "end", values=format_book_row(b))
        elif selected_filter == "Disponible" and b.disponibility:
            tree_books.insert("", "end", values=format_book_row(b))
        elif selected_filter == "Emprunté" and not b.disponibility:
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
    tk.Button(w, text="Ajouter", bg=PRIMARY_COLOR, fg=BUTTON_FG, command=on_add).grid(row=len(labels), column=0, columnspan=2, pady=8)

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
tk.Button(btn_frame_books, text="📚 Ajouter livre", bg=PRIMARY_COLOR, fg=BUTTON_FG, command=add_book_window).pack(side="left", padx=6)
tk.Button(btn_frame_books, text="❌ Supprimer livre", bg=DANGER_COLOR, fg=BUTTON_FG, command=delete_book).pack(side="left", padx=6)
tk.Button(btn_frame_books, text="🔍 Rechercher", bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: search_book_window()).pack(side="left", padx=6)

def search_book_window():
    q = simpledialog.askstring("Recherche livre", "Titre / Auteur / ISBN :")
    if not q:
        return
    res = mgr.search_books(q)
    txt = "\n".join([f"{b.title} — {b.author} — {b.isbn} — {'dispo' if b.disponibility else 'emprunté'}" for b in res]) or "Aucun résultat"
    messagebox.showinfo("Résultats", txt)




tab_members = ttk.Frame(nb)
nb.add(tab_members, text="Membres")

mem_cols = ("Nom","Prénom","Email","Téléphone","Date inscription")
tree_members = ttk.Treeview(tab_members, columns=mem_cols, show="headings")
for c in mem_cols:
    tree_members.heading(c, text=c, anchor="center")
    tree_members.column(c, width=160, anchor="center")
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
    tk.Button(w, text="Ajouter", bg=PRIMARY_COLOR, fg=BUTTON_FG, command=on_add).grid(row=len(labels), column=0, columnspan=2, pady=8)

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
tk.Button(btn_frame_mem, text="Ajouter membre", command=add_member_window, bg=PRIMARY_COLOR, fg=BUTTON_FG).pack(side="left", padx=6)
tk.Button(btn_frame_mem, text="Supprimer membre", command=delete_member, bg=DANGER_COLOR, fg=BUTTON_FG).pack(side="left", padx=6)


tab_emprunts = ttk.Frame(nb)
nb.add(tab_emprunts, text="Emprunts")
frame_counters = tk.Frame(tab_emprunts)
frame_counters.pack(fill="x", pady=5)

lbl_dispo = tk.Label(frame_counters, text="📘 Disponibles : 0", font=("Arial", 11, "bold"), fg="#4CAF50")
lbl_dispo.pack(side="left", padx=20)

lbl_empruntes = tk.Label(frame_counters, text="🔒 Empruntés : 0", font=("Arial", 11, "bold"), fg="#FF9800")
lbl_empruntes.pack(side="left", padx=20)

lbl_retards = tk.Label(frame_counters, text="⚠️ Retards : 0", font=("Arial", 11, "bold"), fg="#E53935")
lbl_retards.pack(side="left", padx=20)


emp_cols = ("ID","ISBN","Email membre","Date emprunt","Date due","Date retour","Statut")
tree_emprunts = ttk.Treeview(tab_emprunts, columns=emp_cols, show="headings")
for c in emp_cols:
    tree_emprunts.heading(c, text=c, anchor="center")
    tree_emprunts.column(c, width=140, anchor="center")
tree_emprunts.pack(fill="both", expand=True, padx=10, pady=10)

def refresh_emprunts():
    for r in tree_emprunts.get_children():
        tree_emprunts.delete(r)
    for e in mgr.emprunts.values():
        tree_emprunts.insert("", "end", values=format_emprunt_row(e))
    update_counters()

def update_counters():
    total_dispo = sum(1 for b in mgr.books.values() if b.disponibility)
    total_empruntes = sum(1 for b in mgr.books.values() if not b.disponibility)
    total_retards = len(mgr.overdue_emprunts())

    lbl_dispo.config(text=f"📘 Disponibles : {total_dispo}")
    lbl_empruntes.config(text=f"🔒 Empruntés : {total_empruntes}")
    lbl_retards.config(text=f"⚠️ Retards : {total_retards}")

def update_book_counters():
    total = len(mgr.books)
    dispo = sum(1 for b in mgr.books.values() if b.disponibility)
    empruntes = total - dispo

    lbl_total_books.config(text=f"📘 Total livres : {total}")
    lbl_dispo_books.config(text=f"📕 Disponibles : {dispo}")
    lbl_empruntes_books.config(text=f"🔒 Empruntés : {empruntes}")

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
    tk.Button(w, text="Emprunter", command=on_borrow, bg=PRIMARY_COLOR, fg=BUTTON_FG).grid(row=len(labels), column=0, columnspan=2, pady=8)

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
    tk.Button(w, text="Retourner", command=on_return, bg=DANGER_COLOR, fg=BUTTON_FG).grid(row=1, column=0, columnspan=2, pady=8)

def filter_emprunts_window():
    w = tk.Toplevel(app)
    w.title("Filtrer les emprunts par date")
    w.geometry("300x150")

    tk.Label(w, text="Date début:").grid(row=0, column=0, padx=5, pady=5)
    start_date = DateEntry(w, date_pattern='dd/MM/yyyy')
    start_date.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(w, text="Date fin:").grid(row=1, column=0, padx=5, pady=5)
    end_date = DateEntry(w, date_pattern='dd/MM/yyyy')
    end_date.grid(row=1, column=1, padx=5, pady=5)

    def on_filter():
        start = datetime.combine(start_date.get_date(), datetime.min.time())
        end = datetime.combine(end_date.get_date(), datetime.max.time())
    
        for r in tree_emprunts.get_children():
            tree_emprunts.delete(r)
      
        for e in mgr.emprunts.values():
            e_date = datetime.strptime(e.date_emprunt, DATEFMT)
            if start <= e_date <= end:
                tree_emprunts.insert("", "end", values=format_emprunt_row(e))
        w.destroy()

    tk.Button(w, text="Filtrer", command=on_filter, bg=PRIMARY_COLOR, fg=BUTTON_FG).grid(row=2, column=0, columnspan=2, pady=10)


btn_frame_emp = tk.Frame(tab_emprunts)
btn_frame_emp.pack(pady=6)
tk.Button(btn_frame_emp, text="Emprunter", command=borrow_window, bg=PRIMARY_COLOR, fg=BUTTON_FG).pack(side="left", padx=6)
tk.Button(btn_frame_emp, text="Retour", command=return_window, bg=DANGER_COLOR, fg=BUTTON_FG).pack(side="left", padx=6)
tk.Button(btn_frame_emp, text="📅 Filtrer par date", command=filter_emprunts_window, bg="#FFA500", fg="white").pack(side="left", padx=6)






tab_res = ttk.Frame(nb)
nb.add(tab_res, text="Réservations")

res_cols = ("ISBN","Titre","Queue (emails)")
tree_res = ttk.Treeview(tab_res, columns=res_cols, show="headings")
for c in res_cols:
    tree_res.heading(c, text=c, anchor="center")
    tree_res.column(c, width=300, anchor="center")
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
    tk.Button(w, text="Réserver", command=on_reserve, bg=PRIMARY_COLOR, fg=BUTTON_FG).grid(row=2, column=0, columnspan=2, pady=6)

btn_frame_res = tk.Frame(tab_res)
btn_frame_res.pack(pady=6)
tk.Button(btn_frame_res, text="Nouveau réservation", command=reserve_window, bg=PRIMARY_COLOR, fg=BUTTON_FG).pack(side="left", padx=6)
tk.Button(btn_frame_res, text="Refresh", command=refresh_reservations, bg=BUTTON_BG, fg=BUTTON_FG).pack(side="left", padx=6)



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
    for e in mgr.overdue_emprunts():
        book = mgr.books.get(e.book_isbn)
        member = mgr.members.get(e.member_email)

        book_name = book.title if book else "???"
        member_name = f"{member.prenom} {member.nom}" if member else e.member_email
        lines.append(
        f" - ID {e.emprunt_id} | Livre: {book_name} | \n"
        f"Membre: {member_name} | Emprunté le: {e.date_emprunt} | Due: {e.date_due}\n"
        f"Contact information :{member.phone}| {member.email}\n"
        f"_______________________________________________________________________________________\n")
    txt_report.delete("1.0", "end")
    txt_report.insert("1.0", "\n".join(lines))


def export_report_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    try:
        st = mgr.stats()
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
     
            writer.writerow(["Total livres", st["total_books"]])
            writer.writerow(["Total membres", st["total_members"]])
            writer.writerow(["Total emprunts (historique)", st["total_emprunts"]])
            writer.writerow([])

       
            writer.writerow(["Top 5 livres les plus empruntés"])
            writer.writerow(["Titre","Nombre d'emprunts"])
            for b in st["top_books"]:
                writer.writerow([b.title, b.borrow_count])
            writer.writerow([])

        
            writer.writerow(["Top membres (par nombre d'emprunts)"])
            writer.writerow(["Membre","Nombre d'emprunts"])
            for email, ct in st["top_members"]:
                member = mgr.members.get(email)
                name = f"{member.prenom} {member.nom}" if member else email
                writer.writerow([name, ct])
            writer.writerow([])

       
            writer.writerow(["Emprunts en cours"])
            writer.writerow(["ID","Livre","Membre","Date emprunt","Date due","Contact"])
            for e in mgr.overdue_emprunts():
                book = mgr.books.get(e.book_isbn)
                member = mgr.members.get(e.member_email)
                book_name = book.title if book else "???"
                member_name = f"{member.prenom} {member.nom}" if member else e.member_email
                writer.writerow([e.emprunt_id, book_name, member_name, e.date_emprunt, e.date_due, f"{member.phone if member else ''} | {member.email if member else ''}"])
        messagebox.showinfo("Succès", "Rapport exporté en CSV !")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))


btn_frame_rep = tk.Frame(tab_reports)
btn_frame_rep.pack(pady=6)
tk.Button(btn_frame_rep, text="Générer rapport", command=refresh_reports, bg=BUTTON_BG, fg=BUTTON_FG).pack(side="left", padx=6)
tk.Button(btn_frame_rep, text="Exporter CSV", command=export_report_csv, bg="#FFA500", fg="white").pack(side="left", padx=6)

def export_report_pdf():
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                             filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return
    try:
        report_text = txt_report.get("1.0", "end").strip()
        if not report_text:
            messagebox.showwarning("Avertissement", "Le rapport est vide !")
            return

       
        c = pdfcanvas.Canvas(file_path, pagesize=A4)  
        width, height = A4
        c.setFont("Helvetica", 12)

       
        c.drawString(100, height - 50, "Rapport de bibliothèque")

        
        lines = report_text.split("\n")
        y = height - 80  

        for line in lines:
            if y < 50:  
                c.showPage()
                c.setFont("Helvetica", 12)
                y = height - 50
            c.drawString(40, y, line)
            y -= 18

        c.save()  
        messagebox.showinfo("Succès", f"Rapport exporté en PDF !\nChemin : {file_path}")

    except Exception as e:
        messagebox.showerror("Erreur", str(e))
tk.Button(btn_frame_rep, text="Exporter PDF", command=export_report_pdf, bg="#FF5733", fg="white").pack(side="left", padx=6)


tab_performances = ttk.Frame(nb)
nb.add(tab_performances, text="🚀 Performances")

frame_graph = tk.Frame(tab_performances)
frame_graph.pack(fill="both", expand=True, padx=10, pady=10)

lbl_pred = tk.Label(tab_performances, text="Prédiction en cours...", font=("Arial", 14, "bold"))
lbl_pred.pack(pady=20)



def show_emprunt_curve():
    for widget in frame_graph.winfo_children():
        widget.destroy()

    counts = {}
    for e in mgr.emprunts.values():
        try:
            d = datetime.strptime(e.date_emprunt, "%Y-%m-%d")
            key = d.strftime("%Y-%m")
            counts[key] = counts.get(key, 0) + 1
        except:
            pass

    if not counts:
        lbl_pred.config(text="Pas assez de données pour afficher le graphique.")
        return

    mois = sorted(counts.keys())
    valeurs = [counts[m] for m in mois]

    fig = plt.Figure(figsize=(6,4), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(mois, valeurs, marker="o", color="#2a6fdb", linewidth=2)
    ax.set_title("Évolution des emprunts par mois", fontsize=12, fontweight="bold")
    ax.set_ylabel("Nombre d'emprunts")
    ax.set_xlabel("Mois")
    ax.grid(True, linestyle="--", alpha=0.6)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    canvas = FigureCanvasTkAgg(fig, master=frame_graph)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def refresh_prediction():
    emprunts_par_mois = {}

   
    for e in mgr.emprunts.values():
        try:
            d = datetime.strptime(e.date_emprunt, "%Y-%m-%d")
            key = d.strftime("%Y-%m")     # Format YYYY-MM
            emprunts_par_mois[key] = emprunts_par_mois.get(key, 0) + 1
        except:
            pass


    dernier_mois = datetime.today().replace(day=1)
    mois_list = [(dernier_mois - timedelta(days=30*i)).strftime("%Y-%m")
                 for i in reversed(range(3))]

   
    emprunts_par_mois_complete = {m: emprunts_par_mois.get(m, 0) for m in mois_list}

  
    moyenne = sum(emprunts_par_mois_complete[m] for m in mois_list) // 3


    lbl_pred.config(text=f"📈 Emprunts prévus le mois prochain : {moyenne}")


    
btn_graph = tk.Button(tab_performances, text="📈 Afficher courbe des emprunts",
                    bg="#2a6fdb", fg="white", command=show_emprunt_curve)
btn_graph.pack(pady=10)



refresh_prediction()


def refresh_all():
    refresh_books()
    refresh_members()
    refresh_emprunts()
    refresh_reservations()
    refresh_reports()
    update_counters()
    update_book_counters()
    refresh_prediction()

tk.Button(app, text="Refresh tout", command=refresh_all, bg="#607D8B", fg=BUTTON_FG).pack(side="bottom", pady=6)


def show_overdue_startup():
    overdue = mgr.overdue_emprunts()
    if not overdue:
        return


    w = tk.Toplevel(app)
    w.title("Emprunts en retard")
    w.geometry("650x400")  
    w.resizable(False, False)

    tk.Label(w, text="LIST DES EMPRUNTS EN RETARD :", fg="red", font=("Arial", 12, "bold")).pack(pady=10)

    txt = tk.Text(w, wrap="word", font=("Arial", 10))
    txt.pack(fill="both", expand=True, padx=10, pady=10)

    for e in overdue:
        book = mgr.books.get(e.book_isbn)
        member = mgr.members.get(e.member_email)

        book_name = book.title if book else "???"
        member_name = f"{member.prenom} {member.nom}" if member else e.member_email

        txt.insert(
            "end",
            f"• ID emprunt : {e.emprunt_id}\n"
            f"  Livre       : {book_name}\n"
            f"  Membre      : {member_name}\n"
            f"___________________________________________________\n"
        )

    tk.Button(w, text="Fermer", command=w.destroy, bg="#607D8B", fg="white").pack(pady=10)


refresh_all()
app.after(500, show_overdue_startup)


def on_quit():
    mgr._save_all()
    app.destroy()

app.protocol("WM_DELETE_WINDOW", on_quit)
is_dark = False  

def apply_dark_mode():
    app.configure(bg="#1e1e1e")
    style.theme_use('default')

    style.configure(".", background="#1e1e1e", foreground="white")
    style.configure("Treeview",
                    background="#2a2a2a",
                    fieldbackground="#2a2a2a",
                    foreground="white")
    style.configure("Treeview.Heading",
                    background="#444444",
                    foreground="white")

    for widget in app.winfo_children():
        if isinstance(widget, tk.Button):
            widget.configure(bg="#333333", fg="white", activebackground="#555555")

    for top in app.winfo_children():
        if isinstance(top, tk.Toplevel):
            top.configure(bg="#1e1e1e")


def apply_light_mode():
    app.configure(bg="white")
    style.theme_use('default')

    style.configure(".", background="white", foreground="black")
    style.configure("Treeview",
                    background="white",
                    fieldbackground="white",
                    foreground="black")
    style.configure("Treeview.Heading",
                    background="#0077c9",
                    foreground="white")

    for widget in app.winfo_children():
        if isinstance(widget, tk.Button):
            widget.configure(bg="#2a6fdb", fg="white", activebackground="#5590ff")


def toggle_theme():
    global is_dark
    if is_dark:
        apply_light_mode()
    else:
        apply_dark_mode()
    is_dark = not is_dark




tk.Button(app,
          text="Mode Sombre / Clair",
          command=toggle_theme,
          bg="#444444",
          fg="white").pack(side="bottom", pady=4)

tab_stats = ttk.Frame(nb)
nb.add(tab_stats, text="Statistiques 📊")

fig = Figure(figsize=(6,4))
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=tab_stats)
canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

def refresh_stats_graph():
    ax.clear()
    st = mgr.stats()
    top_books = st["top_books"]
    titles = [b.title if len(b.title) <= 20 else b.title[:17]+"..." for b in top_books]
    counts = [b.borrow_count for b in top_books]

    ax.bar(range(len(titles)), counts, color="#4CAF50")
    ax.set_xticks(range(len(titles)))
    ax.set_xticklabels(titles, rotation=45, ha='right')

    ax.set_title("Top 5 livres les plus empruntés")
    ax.set_ylabel("Nombre d'emprunts")

    fig.tight_layout()  
    canvas.draw()

btn_frame_stats = tk.Frame(tab_stats)
btn_frame_stats.pack(pady=4)
tk.Button(btn_frame_stats, text="Rafraîchir Statistiques", command=refresh_stats_graph, bg=BUTTON_BG, fg="white").pack(side="left", padx=6)


refresh_stats_graph()
app.mainloop()
