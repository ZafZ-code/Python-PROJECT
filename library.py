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