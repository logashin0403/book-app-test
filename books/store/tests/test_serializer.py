from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="Test Name 1", first_name="Ivan", last_name="Petrov")
        self.user2 = User.objects.create(username="Test Name 2", first_name="Alexey", last_name="Ivanov")
        self.user3 = User.objects.create(username="Test Name 3", first_name="1", last_name="2")

        self.book1 = Book.objects.create(name="book1", price="150.00", author_name="Author1", owner=self.user1)
        self.book2 = Book.objects.create(name="book2", price="123.21", author_name="Author2")

    def test_ok(self):
        UserBookRelation.objects.create(user=self.user1, book=self.book1, like=True, rate=5)
        UserBookRelation.objects.create(user=self.user2, book=self.book1, like=True, rate=5)
        UserBookRelation.objects.create(user=self.user3, book=self.book1, like=True, rate=3)

        UserBookRelation.objects.create(user=self.user1, book=self.book2, like=True, rate=2)
        UserBookRelation.objects.create(user=self.user2, book=self.book2, like=True, rate=5)
        UserBookRelation.objects.create(user=self.user3, book=self.book2, like=False)

        expected = [
            {
                "id": self.book1.id,
                "name": self.book1.name,
                "price": self.book1.price,
                "author_name": self.book1.author_name,
                "annotated_likes": 3,
                "rating": "4.33",
                "owner_name": "Test Name 1",
                "readers": [
                    {
                        "first_name": "Ivan",
                        "last_name": "Petrov"
                    },
                    {
                        "first_name": "Alexey",
                        "last_name": "Ivanov"
                    },
                    {
                        "first_name": "1",
                        "last_name": "2"
                    },
                ]
            },
            {
                "id": self.book2.id,
                "name": self.book2.name,
                "price": self.book2.price,
                "author_name": self.book2.author_name,
                "annotated_likes": 2,
                "rating": "3.50",
                "owner_name": "",
                "readers": [
                    {
                        "first_name": "Ivan",
                        "last_name": "Petrov"
                    },
                    {
                        "first_name": "Alexey",
                        "last_name": "Ivanov"
                    },
                    {
                        "first_name": "1",
                        "last_name": "2"
                    },
                ]
            }
        ]

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by("id")
        actual = BooksSerializer(books, many=True).data

        self.assertEqual(expected, actual)
