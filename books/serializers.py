from rest_framework import serializers

from .models import Book


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "author_name",
            "isbn",
            "published_date",
            "price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
