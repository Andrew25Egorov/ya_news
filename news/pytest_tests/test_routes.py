from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects

from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_pages_availability(client, name, args, news):
    """Проверка доступности страниц для анонима."""
    if name == 'news:detail':
        args = (news.id,)
    response = client.get(reverse(name, args=args))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    """
    Проверка доступности страниц редактирования и удаления комментов
    для разных пользователей.
    """
    response = parametrized_client.get(reverse(name, args=(comment.id,)))
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_for_anonymous_client(client, name, comment):
    """
    При переходе на страницы редактирования и удаления комментов
    аноним перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
