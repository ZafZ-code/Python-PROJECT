
import json
from datetime import datetime, timedelta
from collections import defaultdict
import os
import uuid

BOOKS_FILE = "books.json"
MEMBERS_FILE = "members.json"
EMPRUNTS_FILE = "emprunts.json"

DATEFMT = "%Y-%m-%d"


def load_json(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


class Book:
    def __init__(self, title, author, isbn, year, disponibility=True, reservations=None, borrow_count=0):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.year = year
        self.disponibility = bool(disponibility)
        self.reservations = reservations or []  
        self.borrow_count = borrow_count

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "year": self.year,
            "disponibility": self.disponibility,
            "reservations": self.reservations,
            "borrow_count": self.borrow_count
        }

    @staticmethod
    def from_dict(d):
        return Book(d["title"], d["author"], d["isbn"], d.get("year", ""), d.get("disponibility", True),
                    d.get("reservations", []), d.get("borrow_count", 0))


class Member:
    def __init__(self, nom, prenom, email, phone="", date_inscription=None):
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.phone = phone
        self.date_inscription = date_inscription or datetime.today().strftime(DATEFMT)

    def to_dict(self):
        return {
            "nom": self.nom,
            "prenom": self.prenom,
            "email": self.email,
            "phone": self.phone,
            "date_inscription": self.date_inscription
        }

    @staticmethod
    def from_dict(d):
        return Member(d["nom"], d["prenom"], d["email"], d.get("phone", ""), d.get("date_inscription"))


class Emprunt:
    def __init__(self, emprunt_id, book_isbn, member_email, date_emprunt, date_due, date_return=None, status="ongoing"):
        self.emprunt_id = emprunt_id
        self.book_isbn = book_isbn
        self.member_email = member_email
        self.date_emprunt = date_emprunt
        self.date_due = date_due
        self.date_return = date_return
        self.status = status  

    def to_dict(self):
        return {
            "emprunt_id": self.emprunt_id,
            "book_isbn": self.book_isbn,
            "member_email": self.member_email,
            "date_emprunt": self.date_emprunt,
            "date_due": self.date_due,
            "date_return": self.date_return,
            "status": self.status
        }

    @staticmethod
    def from_dict(d):
        return Emprunt(d["emprunt_id"], d["book_isbn"], d["member_email"], d["date_emprunt"], d["date_due"], d.get("date_return"), d.get("status", "ongoing"))

    def is_overdue(self):
        if self.status != "ongoing":
            return False
        today = datetime.today().date()
        due = datetime.strptime(self.date_due, DATEFMT).date()
        return due < today


class LibraryManager:
    def __init__(self):
        self.books = {}   
        self.members = {} 
        self.emprunts = {} 
        self._load_all()

    # Persistence
    def _load_all(self):
        for b in load_json(BOOKS_FILE):
            book = Book.from_dict(b)
            self.books[book.isbn] = book

        for m in load_json(MEMBERS_FILE):
            member = Member.from_dict(m)
            self.members[member.email] = member

        for e in load_json(EMPRUNTS_FILE):
            empr = Emprunt.from_dict(e)
            self.emprunts[empr.emprunt_id] = empr

    def _save_all(self):
        save_json(BOOKS_FILE, [b.to_dict() for b in self.books.values()])
        save_json(MEMBERS_FILE, [m.to_dict() for m in self.members.values()])
        save_json(EMPRUNTS_FILE, [e.to_dict() for e in self.emprunts.values()])

    def add_book(self, title, author, isbn, year):
        if isbn in self.books:
            raise ValueError("ISBN already exists")
        book = Book(title, author, isbn, year, True, [])
        self.books[isbn] = book
        self._save_all()
        return book

    def remove_book(self, isbn_or_title):
        to_remove = None
        if isbn_or_title in self.books:
            to_remove = self.books[isbn_or_title]
        else:
            for b in list(self.books.values()):
                if b.title.lower() == isbn_or_title.lower():
                    to_remove = b
                    break
        if not to_remove:
            raise KeyError("Book not found")
        for e in self.emprunts.values():
            if e.book_isbn == to_remove.isbn and e.status == "ongoing":
                raise ValueError("Book currently borrowed; cannot remove")
        del self.books[to_remove.isbn]
        self._save_all()

    def search_books(self, query):
        q = query.lower()
        results = []
        for b in self.books.values():
            if q in b.title.lower() or q in b.author.lower() or q in b.isbn.lower():
                results.append(b)
        return results

    def add_member(self, nom, prenom, email, phone=""):
        if email in self.members:
            raise ValueError("Member with this email already exists")
        member = Member(nom, prenom, email, phone)
        self.members[email] = member
        self._save_all()
        return member

    def remove_member(self, email):
        if email not in self.members:
            raise KeyError("Member not found")
        for e in self.emprunts.values():
            if e.member_email == email and e.status == "ongoing":
                raise ValueError("Member has ongoing emprunts; cannot remove")
        del self.members[email]
        self._save_all()

    def list_members(self):
        return list(self.members.values())
    def borrow_book(self, book_isbn, member_email, days=14):
        if book_isbn not in self.books:
            raise KeyError("Book does not exist")
        if member_email not in self.members:
            raise KeyError("Member does not exist")
        book = self.books[book_isbn]
        if not book.disponibility:
            if member_email in book.reservations:
                raise ValueError("Member already in reservation queue")
            book.reservations.append(member_email)
            self._save_all()
            return {"reserved": True}
        if book.reservations:
            if book.reservations[0] != member_email:
                raise ValueError("Book reserved to another member")
            book.reservations.pop(0)

        borrow_id = str(uuid.uuid4())
        date_emprunt = datetime.today().strftime(DATEFMT)
        date_due = (datetime.today() + timedelta(days=days)).strftime(DATEFMT)
        empr = Emprunt(borrow_id, book_isbn, member_email, date_emprunt, date_due, None, "ongoing")
        self.emprunts[borrow_id] = empr
        book.disponibility = False
        book.borrow_count = int(book.borrow_count) + 1
        self._save_all()
        return empr

    def return_book(self, emprunt_id):
        if emprunt_id not in self.emprunts:
            raise KeyError("Emprunt not found")
        empr = self.emprunts[emprunt_id]
        if empr.status != "ongoing":
            raise ValueError("Emprunt already closed")
        empr.date_return = datetime.today().strftime(DATEFMT)
        empr.status = "returned"
        book = self.books.get(empr.book_isbn)
        if not book:
            raise KeyError("Book record missing")
        if book.reservations:
            book.disponibility = False
        else:
            book.disponibility = True
        self._save_all()
        return empr

    def reserve_book(self, book_isbn, member_email):
        if book_isbn not in self.books:
            raise KeyError("Book does not exist")
        if member_email not in self.members:
            raise KeyError("Member does not exist")
        book = self.books[book_isbn]
        if member_email in book.reservations:
            raise ValueError("Already reserved")
        book.reservations.append(member_email)
        self._save_all()

    def overdue_emprunts(self):
        return [e for e in self.emprunts.values() if e.is_overdue()]

    def current_emprunts(self):
        return [e for e in self.emprunts.values() if e.status == "ongoing"]

    def emprunts_by_member(self, member_email):
        return [e for e in self.emprunts.values() if e.member_email == member_email]

    def book_status(self, isbn):
        b = self.books.get(isbn)
        if not b:
            return None
        borrowed_by = None
        for e in self.emprunts.values():
            if e.book_isbn == isbn and e.status == "ongoing":
                borrowed_by = e.member_email
                break
        return {
            "book": b,
            "available": b.disponibility,
            "borrowed_by": borrowed_by,
            "reservations": list(b.reservations)
        }

    def stats(self):
        total_books = len(self.books)
        total_members = len(self.members)
        total_emprunts = len(self.emprunts)
        top_books = sorted(self.books.values(), key=lambda x: x.borrow_count, reverse=True)[:5]
        count_by_member = defaultdict(int)
        for e in self.emprunts.values():
            count_by_member[e.member_email] += 1
        top_members = sorted(count_by_member.items(), key=lambda x: x[1], reverse=True)[:5]
        currently_borrowed = [e for e in self.emprunts.values() if e.status == "ongoing"]
        return {
            "total_books": total_books,
            "total_members": total_members,
            "total_emprunts": total_emprunts,
            "top_books": top_books,
            "top_members": top_members,
            "currently_borrowed": currently_borrowed
        }
