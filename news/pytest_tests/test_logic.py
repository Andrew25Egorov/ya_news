from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, form_data, url_comment):
    """Аноним не может создавать комментарии."""
    client.post(url_comment, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author, author_client, form_data, news, url_comment
):
    """Авторизованный пользователь может создать комментарии."""
    response = author_client.post(url_comment, data=form_data)
    assertRedirects(response, f'{url_comment}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, url_comment):
    """Не возможно использовать в комментарии слова из списка BAD_WORDS."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url_comment, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_del_comment(author_client, url_del_comment, url_comment):
    """Автор может удалять свои комментарии."""
    response = author_client.delete(url_del_comment)
    assertRedirects(response, f'{url_comment}#comments')
    assert Comment.objects.count() == 0


def test_user_cant_del_comment_of_another_user(url_del_comment, reader_client):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    response = reader_client.delete(url_del_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
    author_client, url_edit_comment, url_comment, new_form_data
):
    """Автор может редактировать свои комментарии."""
    comment = Comment.objects.get()
    response = author_client.post(url_edit_comment, data=new_form_data)
    assertRedirects(response, f'{url_comment}#comments')
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
    reader_client, url_edit_comment, new_form_data
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    comment = Comment.objects.get()
    response = reader_client.post(url_edit_comment, data=new_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
