from django.contrib import admin
from .models import Genre, FilmWork, Person, GenreFilmwork, PersonFilmwork


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "id")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("full_name",)
    search_fields = ("full_name", "id")


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (
        GenreFilmworkInline,
        PersonFilmworkInline,
    )
    list_display = ("title", "type", "creation_date", "rating", "created", "modified")
    # list_filter = ("type", "genres", "persons")
    search_fields = ("title", "description", "id")
