from datetime import datetime, timedelta

import pytest

from django.conf import settings
from django.test.client import Client
from django.utils import timezone
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def all_news():
    today = datetime.today()
    all_news = News.objects.bulk_create(
        News(title=f'Новость {index}',
             text='Просто текст.',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return all_news


@pytest.fixture
def comments_list(news, author):
    now = timezone.now()
    for index in range(5):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.fixture
def form_data():
    return {'text': COMMENT_TEXT}


@pytest.fixture
def new_form_data():
    return {'text': NEW_COMMENT_TEXT}


@pytest.fixture
def url_comment(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def url_del_comment(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def url_edit_comment(comment):
    return reverse('news:edit', args=(comment.id,))
