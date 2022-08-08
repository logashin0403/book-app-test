from django.contrib.auth.models import User
from django.test import TestCase

from store.logic import set_rating
from store.models import Book, UserBookRelation


class SetRatingTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="Test Name 1", first_name="Ivan", last_name="Petrov")
        self.user2 = User.objects.create(username="Test Name 2", first_name="Alexey", last_name="Ivanov")
        self.user3 = User.objects.create(username="Test Name 3", first_name="1", last_name="2")

        self.book1 = Book.objects.create(name="book1", price="150.00", author_name="Author1", owner=self.user1)

    def test_ok(self):
        UserBookRelation.objects.create(user=self.user1, book=self.book1, like=True, rate=5)
        UserBookRelation.objects.create(user=self.user2, book=self.book1, like=True, rate=5)
        UserBookRelation.objects.create(user=self.user3, book=self.book1, like=True, rate=3)

        set_rating(self.book1)
        self.book1.refresh_from_db()
        self.assertEqual("4.33", str(self.book1.rating))
