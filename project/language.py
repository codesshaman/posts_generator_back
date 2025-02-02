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

def fs_translator(request: HttpRequest, ru_value: str, en_value: str, *args, **kwargs) -> str:
    """Форматирует строку в зависимости от языка пользователя, подставляя args и kwargs в порядке их передачи."""

    lang = get_language_from_request(request)
    accept_lang = request.headers.get('Accept-Language', 'не указан')

    print(f"Django Language: {lang}, Accept-Language: {accept_lang}")  # Лог для проверки

    template = ru_value if lang.startswith("ru") else en_value

    # Форматируем строку, передавая позиционные и именованные аргументы
    return template.format(*args, **kwargs)