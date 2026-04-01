from rest_framework.pagination import PageNumberPagination


class MyPagination(PageNumberPagination):
    page_query_param = 'pageNum'     # 将默认的 'page' 改为 'pageNum'
    page_size_query_param = 'page_size' # 允许前端通过 page_size 控制每页数量
    page_size = 10