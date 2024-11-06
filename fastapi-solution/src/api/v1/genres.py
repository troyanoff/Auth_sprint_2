from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request

from core.auth import check_auth_and_roles
from models.genres import Genre
from services.genres import GenreService, get_genre_service

router = APIRouter()


@router.get(
    "/",
    response_model=list[Genre],
    response_model_by_alias=False,
    summary="Cписок жанров",
    description="Получить список жанров",
    response_description="Названия и uuid жанров",
)
async def genres(
    request: Request,
    genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre]:
    check_auth_and_roles(request)
    return await genre_service.get_all()


@router.get(
    "/{genre_id}",
    response_model=Genre,
    response_model_by_alias=False,
    summary="Получить жанр",
    description="Получить информацию о жанре по uuid",
    response_description="Информация о жанре",
)
async def genre_details(
    request: Request,
    genre_id: str,
    genre_service: GenreService = Depends(get_genre_service),
) -> Genre:
    check_auth_and_roles(request)
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
    return genre
