import logging
from functools import wraps

# 获取你在 settings 中配置的 logger
logger = logging.getLogger(__name__)


def log_api_call(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        user = request.user if hasattr(request, 'user') else "未知用户"

        logger.info(f"接口调用: {self.__class__.__name__} | 用户: {user} | 路径: {request.path}")

        return func(self, request, *args, **kwargs)

    return wrapper