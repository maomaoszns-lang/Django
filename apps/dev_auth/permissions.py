from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class GlobalAutoPermission(BasePermission):
    WHITE_LIST = ['login']

    def has_permission(self, request, view):
        # 白名单 login 不需要权限登录
        if request.resolver_match.url_name  in self.WHITE_LIST:
            return True

        # 1. 如果用户不存在 或者用户未认证返回False
        user = request.user
        if not user or not getattr(user, 'is_authenticated', True):
            return False

        # 2.果用户对象有 id 属性 且 id 值为 1 直接返回 True  超级管理员直接放行
        if hasattr(user, 'id') and user.id == 1:
            return True

        raw_url_name = request.resolver_match.url_name  # 例如 'user-info' 或 'upload'
        # print(f"DEBUG: Current URL Name is {raw_url_name}")
        prefix = raw_url_name.split('-')[0]
        # print(prefix)

        method_map = {
            'GET': 'list',
            'POST': 'add',
            'PUT': 'edit',
            'DELETE': 'delete'
        }
        # add
        action = method_map.get(request.method, 'list')

        possible_perms = list(set([f"{prefix}-{action}",prefix,action]))
        # print(possible_perms)

        # 只要数据库里满足其中任何一个，就放行
        has_perm = user.roles.filter(menus__perms__in=possible_perms).exists()

        if not has_perm:
            raise PermissionDenied(f"权限点 {possible_perms} 未分配")

        return True




