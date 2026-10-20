from rest_framework import viewsets

from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("author")
    serializer_class = BookSerializer
