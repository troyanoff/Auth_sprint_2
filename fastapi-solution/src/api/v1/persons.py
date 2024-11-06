from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Annotated

from core.auth import check_auth_and_roles
from models.persons import PersonWithFilms
from models.films import FilmBase
from services.persons import PersonService, get_person_service

router = APIRouter()


@router.get(
    "/search",
    response_model=list[PersonWithFilms],
    response_model_by_alias=False,
    summary="Поиск персон",
    description="Полнотекстовый поиск среди персон",
    response_description="Информация о персоне с фильмами",
)
async def persons(
    request: Request,
    query: Annotated[str, Query(description="Текст для поиска")],
    page_size: Annotated[
        int, Query(description="Объем страницы при пагинации", ge=1)
    ] = 50,
    page_number: Annotated[
        int, Query(description="Номер страницы при пагинации", ge=1)
    ] = 1,
    person_service: PersonService = Depends(get_person_service),
) -> list[PersonWithFilms]:
    check_auth_and_roles(request)
    if page_size * page_number > 10000:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="page_size * page_number give more than 10000",
        )
    persons = await person_service.search(query, page_size, page_number)
    return persons


@router.get(
    "/{person_id}",
    response_model=PersonWithFilms,
    response_model_by_alias=False,
    summary="Информация о персоне",
    description="Получить информацию о персоне по uuid",
    response_description="Информация о персоне с фильмами",
)
async def person_details(
    request: Request,
    person_id: str,
    person_service: PersonService = Depends(get_person_service),
) -> PersonWithFilms:
    check_auth_and_roles(request)
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return person


@router.get(
    "/{person_id}/film",
    response_model=list[FilmBase],
    response_model_by_alias=False,
    summary="Фильмы по персоне",
    description="Получить фильмы персоны",
    response_description="Список фильмов персоны",
)
async def person_films(
    person_id: str,
    request: Request,
    page_size: Annotated[
        int, Query(description="Объем страницы при пагинации", ge=1)
    ] = 50,
    page_number: Annotated[
        int, Query(description="Номер страницы при пагинации", ge=1)
    ] = 1,
    person_service: PersonService = Depends(get_person_service),
) -> list[FilmBase]:
    check_auth_and_roles(request)
    if page_size * page_number > 10000:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="page_size * page_number give more than 10000",
        )
    films = await person_service.get_films(person_id, page_size, page_number)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return films
