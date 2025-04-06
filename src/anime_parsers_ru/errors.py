class TokenError(Exception):
    """
    Ошибка для обозначения неверного токена.
    """


class ServiceError(Exception):
    """
    Ошибка для обозначения ошибки на стороне сервера
    """


class PostArgumentsError(Exception):
    """
    Ошибка для обозначения неверно переданных аргументов серверу
    """


class NoResults(Exception):
    """
    Ошибка для обозначения отсутствия результатов
    """


class UnexpectedBehavior(Exception):
    """
    Ошибка для обозначения неожиданного или необработанного поведения
    """


class QualityNotFound(Exception):
    """
    Ошибка для обозначения не найденного запрашиваемого качества видео
    """


class AgeRestricted(Exception):
    """
    Ошибка для обозначения что контент заблокирован из-за возрастного рейтинга
    """


class TooManyRequests(Exception):
    """
    Ошибка для обозначения ошибки 429 из-за слишком частых запросов.
    В основном для шикимори
    """


class ContentBlocked(Exception):
    """
    Ошибка для обозначения заблокированного контента/плеера
    """


class ServiceIsOverloaded(Exception):
    """
    Ошибка для обозначения http кода 520
    Используется в парсере shikimori
    """


class DecryptionFailure(Exception):
    """При попытке дешифровать ссылку от Kodik возникла ошибка"""
