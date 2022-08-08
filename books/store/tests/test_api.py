import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="Test Name")

        self.book1 = Book.objects.create(name="book1", price="150.00", author_name="Author1", owner=self.user)
        self.book2 = Book.objects.create(name="book2", price="123.21", author_name="Author2")
        self.book3 = Book.objects.create(name="book3 Author1", price="111.21", author_name="Author3")

    def test_get(self):
        url = reverse("book-list")

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by("id")
        expected = BooksSerializer(books, many=True).data
        actual = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, actual.status_code)
        self.assertEqual(expected, actual.data)

    def test_get_filter(self):
        url = reverse("book-list")

        books = Book.objects.filter(pk=self.book1.id).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        )
        expected = BooksSerializer(books, many=True).data
        actual = self.client.get(url, data={"price": "150.00"})

        self.assertEqual(status.HTTP_200_OK, actual.status_code)
        self.assertEqual(expected, actual.data)

    def test_get_search(self):
        url = reverse("book-list")

        books = Book.objects.filter(pk__in=[self.book1.id, self.book3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by("id")
        expected = BooksSerializer(books, many=True).data
        actual = self.client.get(url, data={"search": "Author1"})

        self.assertEqual(status.HTTP_200_OK, actual.status_code)
        self.assertEqual(expected, actual.data)

    def test_get_order(self):
        url = reverse("book-list")

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by("price")
        expected = BooksSerializer(books, many=True).data
        actual = self.client.get(url, data={"ordering": "price"})

        self.assertEqual(status.HTTP_200_OK, actual.status_code)
        self.assertEqual(expected, actual.data)

    def test_create(self):
        book_for_create = {
            "name": "some name",
            "price": "150.00",
            "author_name": "some author name"
        }
        url = reverse("book-list")

        json_data = json.dumps(book_for_create)
        self.client.force_login(self.user)

        response = self.client.post(url, data=json_data, content_type="application/json")

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_update(self):
        book_for_update = {
            "name": self.book1.name,
            "price": "777.77",
            "author_name": self.book1.author_name
        }
        new_price_for_book = "777.77"
        url = reverse("book-detail", args=(self.book1.id,))

        json_data = json.dumps(book_for_update)
        self.client.force_login(self.user)

        response = self.client.put(url, data=json_data, content_type="application/json")

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book1.refresh_from_db()

        self.assertEqual(new_price_for_book, str(self.book1.price))

    def test_delete(self):
        book_delete_id = self.book1.id
        url = reverse("book-detail", args=(book_delete_id,))

        self.client.force_login(self.user)

        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)


class BooksRelationApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="Test Name")
        self.user2 = User.objects.create(username="Test Name 2")

        self.book1 = Book.objects.create(name="book1", price="150.00", author_name="Author1", owner=self.user)
        self.book2 = Book.objects.create(name="book2", price="123.21", author_name="Author2")

    def test_like_book(self):
        book_for_create = {
            "like": True,
        }
        url = reverse("userbookrelation-detail", args=(self.book1.id,))

        self.client.force_login(self.user)
        json_data = json.dumps(book_for_create)

        response = self.client.patch(url, data=json_data, content_type="application/json")

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.assertTrue(relation.like)

    def test_rate_book(self):
        book_for_create = {
            "rate": 3,
        }
        url = reverse("userbookrelation-detail", args=(self.book1.id,))

        self.client.force_login(self.user)
        json_data = json.dumps(book_for_create)

        response = self.client.patch(url, data=json_data, content_type="application/json")

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.assertEqual(3, relation.rate)

    def test_rate_book_negative(self):
        book_for_create = {
            "rate": 6,  # bad choice
        }
        url = reverse("userbookrelation-detail", args=(self.book1.id,))

        self.client.force_login(self.user)
        json_data = json.dumps(book_for_create)

        response = self.client.patch(url, data=json_data, content_type="application/json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
