from django.http import HttpRequest
from django.utils.translation import get_language_from_request


def translator(ru_value: str, en_value: str, request: HttpRequest) -> str:
    """Возвращает значение в зависимости от языка пользователя, определённого из заголовка Accept-Language."""

    lang = get_language_from_request(request)  # Определяем язык из заголовка
    accept_lang = request.headers.get('Accept-Language', 'не указан')  # Читаем заголовок Accept-Language

    # print(f"Django Language: {lang}, Accept-Language: {accept_lang}")  # Логируем для отладки

    if lang.startswith("ru"):  # Если язык начинается с "ru", возвращаем русское значение
        return ru_value
    return en_value  # В остальных случаях — английское


# from django.utils.translation import get_language
#
#
# def translator(ru_value: str, en_value: str) -> str:
#     """Возвращает значение в зависимости от текущего языка пользователя."""
#     lang = get_language()  # Получаем текущий язык
#     if lang == "ru":
#         return ru_value
#     return en_value