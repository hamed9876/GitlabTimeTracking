from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "author", "isbn", "price"]
    search_fields = ["title", "isbn"]
    list_select_related = ["author"]
