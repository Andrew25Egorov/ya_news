import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('all_news')
def test_news_count(client):
    """Проверка кол-ва и сортировки новостей на главной странице."""
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures('comments_list')
def test_comments_order(client, news, url_comment):
    """Проверка сортировки комментариев к отдельной новости."""
    response = client.get(url_comment)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, url_comment):
    """Анониму не доступна форма отправки комментариев к отдельной новости."""
    response = client.get(url_comment)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, url_comment):
    """Авторизованному пользователю доступна форма отправки комментариев."""
    response = author_client.get(url_comment)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
