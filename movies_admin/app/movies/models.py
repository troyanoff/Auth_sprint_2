import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(
        _("created"), auto_now_add=True, blank=True, null=True
    )
    modified = models.DateTimeField(_("modified"), auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.TextField(_("name"))
    description = models.TextField(_("description"), blank=True, null=True)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(_("Full Name"))

    class Meta:
        db_table = 'content"."person'
        verbose_name = "Актер"
        verbose_name_plural = "Актеры"

    def __str__(self):
        return self.full_name


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey("Filmwork", on_delete=models.CASCADE)
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    role = models.TextField(_("role"))
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'content"."person_film_work'
        unique_together = (
            "film_work",
            "person",
            "role",
        )


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey("Filmwork", on_delete=models.CASCADE)
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'content"."genre_film_work'
        unique_together = (
            "film_work",
            "genre",
        )


class FilmWork(UUIDMixin, TimeStampedMixin):
    class FilmType(models.TextChoices):
        MOVIE = "movie", _("movie")
        TVSHOW = "tv_show", _("tv_show")

    title = models.TextField(_("title"))
    description = models.TextField(_("description"), blank=True, null=True)
    creation_date = models.DateField(_("creation_date"), blank=True, null=True)
    rating = models.FloatField(
        _("rating"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True,
        null=True,
    )
    type = models.TextField(_("type"), choices=FilmType.choices)
    genres = models.ManyToManyField(
        Genre, through="GenreFilmwork", verbose_name=_("genres")
    )
    persons = models.ManyToManyField(
        Person, through="PersonFilmwork", verbose_name=_("persons")
    )
    file_path = models.FileField(_("file"), blank=True, null=True, upload_to="movies/")

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"

    def __str__(self):
        return self.title
