from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="my_books")
    readers = models.ManyToManyField(User, through="UserBookRelation", related_name="books")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)

    def __str__(self):
        return f"Id {self.id}: {self.name}"


class UserBookRelation(models.Model):
    RATE_CHOICES = (
        (1, "ok"),
        (2, "fine"),
        (3, "good"),
        (4, "amazing"),
        (5, "incredible"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    def __str__(self):
        return f"{self.user.username}: {self.book.name}, RATE: {self.rate}"

    def save(self, *args, **kwargs):
        from store.logic import set_rating

        creating = not self.pk
        previous_rating = self.rate

        super().save(*args, **kwargs)

        current_rating = self.rate
        if previous_rating != current_rating or creating:
            set_rating(self.book)
