from typing import Callable

import pytest
from functional.testdata.fims_data import FILM_TITLES
from functional.utils.models.film import EsFilm, ResponseShortFilm
from pydantic import ValidationError
from pydantic.main import ModelMetaclass


@pytest.mark.parametrize(
    'es_data, url_params, res_status, res_count, res_model, check_model_attrs_in',
    [
        # Кейс поиска без параметров
        (
            [EsFilm.create_fake().dict() for _ in range(200)],
            {},
            200,
            50,
            ResponseShortFilm,
            {},
        ),

        # Кейс поиска по 20 фильмов на странице
        (
            [EsFilm.create_fake().dict() for _ in range(200)],
            {'page_size': 20},
            200,
            20,
            ResponseShortFilm,
            {},
        ),

        # Кейс поиска фильмов с 3-й страницы
        (
            [EsFilm.create_fake().dict() for _ in range(200)],
            {'page_number': 3},
            200,
            50,
            ResponseShortFilm,
            {},
        ),

        # Кейс поиска с запросом
        (
            [
                *[EsFilm.create_fake(title=film_title).dict() for film_title in FILM_TITLES],
                *[EsFilm.create_fake(title=f'Film{i}', description='').dict() for i in range(50)],
            ],
            {'query': 'Star', 'page_size': 10},
            200,
            10,
            ResponseShortFilm,
            {'title': 'star'},
        ),
    ]
)
@pytest.mark.asyncio
async def test_films_search(
        redis_client,
        es_write_data: Callable,
        service_get_data: Callable,
        es_data: list[dict],  # данные для отправки в ES
        url_params: dict,  # параметры запроса
        res_status: int,  # код ответа
        res_count: str,  # количество элементов в ответе
        res_model: ModelMetaclass,  # модель ответа
        check_model_attrs_in: dict  # условия для проверки вхождения текста в атрибут модели,
        # например {'title': 'часть названия'}
):
    """Тест: /api/v1/films
    """
    await es_write_data(es_data, 'movies')

    res = await service_get_data('films/search/', url_params)

    assert res.status == res_status
    assert len(res.body) == res_count
    for el in res.body:
        assert res_model.parse_obj(el)
        for attr, val in check_model_attrs_in.items():
            assert getattr(res_model.parse_obj(el), attr).lower().find(val) != -1


@pytest.mark.parametrize(
    'es_data, url_params, res_status, res_count, res_model, change_attrs',
    [
        # Кейс: ошибка валидации поля uuid
        (
            [EsFilm.create_fake().dict() for _ in range(200)],
            None,
            200,
            50,
            ResponseShortFilm,
            {'uuid': 123456},
        ),

        # Кейс: ошибка валидации поля title
        (
            [EsFilm.create_fake().dict() for _ in range(200)],
            None,
            200,
            50,
            ResponseShortFilm,
            {'title': []},
        ),

        # Кейс: ошибка валидации поля imdb_rating
        (
            [EsFilm.create_fake().dict() for _ in range(200)],
            None,
            200,
            50,
            ResponseShortFilm,
            {'imdb_rating': 'good'},
        ),
    ]
)
@pytest.mark.asyncio
async def test_films_search_no_valid(
        redis_client,
        es_write_data: Callable,
        service_get_data: Callable,
        es_data: list[dict],  # данные для отправки в ES
        url_params: dict,  # параметры запроса
        res_status: int,  # код ответа
        res_count: str,  # количество элементов в ответе
        res_model: ModelMetaclass,  # модель ответа
        change_attrs: dict  # подмена атрибута ответа, например {'imdb_rating': []}
):
    """Тест: /api/v1/films
    """
    await es_write_data(es_data, 'movies')

    res = await service_get_data('films/search/', url_params)

    assert res.status == res_status
    assert len(res.body) == res_count

    res.body[0].update(change_attrs)
    with pytest.raises(ValidationError):
        res_model.parse_obj(res.body[0])
