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

class UnexpectedBehaviour(Exception):
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
    Ошибка для обозначения ошибки сервера из-за слишком частых запросов.
    В основном для шикимориы
    """