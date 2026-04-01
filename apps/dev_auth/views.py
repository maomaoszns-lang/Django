from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from django.conf import settings
from rest_framework import mixins, generics
import logging
from .models import SysMenu, SysUser,SysRole
from  rest_framework.views import APIView
from .serializers import LoginSerializer, UserSerializer, UploadImageSerializer, SysUserSerializer, RoleSerializer,  MenuTreeSerializer
from  datetime import datetime
from .authentications import generate_jwt
from rest_framework.response import Response
from rest_framework import status, viewsets
from .permissions import GlobalAutoPermission
from shortuuid import uuid
import  os
from django.db.models import Q
from  utls.paginations import MyPagination
from utls.log import log_api_call

logger = logging.getLogger(__name__)

class LoginView(APIView):
    def post(self, request):
        #1.验证数据是否可用
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            user.login_date = datetime.now()
            user.save()
            menus = SysMenu.objects.filter(
                roles__users=user,
                menu_type__in=['M', 'C']
            ).distinct().order_by('order_num')

            menu_tree = self.get_menu_tree(menus, parent_id=0)
            token = generate_jwt(user)
            return Response({'token': token,'user': UserSerializer(user).data,'menus': menu_tree})
        else:
            detail = (list(serializer.errors.values())[0][0])
            return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)

    def get_menu_tree(self, queryset, parent_id=0):
        """递归构造树形结构"""
        tree = []
        for menu in queryset.filter(parent_id=parent_id):
            menu_data = {
                "id": menu.id,
                "name": menu.name,
                "path": menu.path,
                "component": menu.component,
                "icon": menu.icon,
                "children": self.get_menu_tree(queryset, parent_id=menu.id)
            }
            tree.append(menu_data)
        return tree




class  UploadImageView(APIView):
    permission_classes = [GlobalAutoPermission]
    def post(self, request):
        serializer = UploadImageSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data.get('image')
            filename = uuid() + os.path.splitext(file.name)[-1]
            print("filename", filename)
            path = settings.MEDIA_ROOT / filename
            print("path", path)

            try:
                with open(path, 'wb') as fp:
                    for chunk in file.chunks():
                        fp.write(chunk)

                user = request.user
                user.avatar = filename
                user.save()
            except Exception:
                return Response({"message": "图片上传失败"}, status=status.HTTP_400_BAD_REQUEST)
            file_url = settings.MEDIA_URL + filename
            return Response({"url": file_url}, status=status.HTTP_200_OK)
        else:
            detail = (list(serializer.errors.values())[0][0])
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)




class Userinfoview(APIView):
    def post(self,request):
        queryset = SysUser.objects.all().order_by('id')
        #搜索功能
        keyword = request.data.get("keyword") or request.query_params.get('keyword')
        if keyword:
            queryset = queryset.filter(Q(username__icontains=keyword) | Q(email__icontains=keyword))
        #执行分页
        paginator = MyPagination()
        page_obj = paginator.paginate_queryset(queryset, request,view=self)
        if page_obj is not None:
            serializer = UserSerializer(page_obj,many=True)
            return  paginator.get_paginated_response(serializer.data)

        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)



class SysUserViewSet(viewsets.ModelViewSet):
    """
    用户添加修改 用户角色权限分配
    """
    queryset = SysUser.objects.all()
    serializer_class = SysUserSerializer

    # 路径：POST /api/sysuser/{id}/roles/
    @action(detail=True, methods=['post'])
    def roles(self, request, pk=None):
        # print(f"DEBUG: 接收到的数据 -> {request.data}")
        """
        给用户指定角色
        """
        user = self.get_object()
        print(user)
        # {"roleIds": [1, 2, 3]}
        role_ids = request.data.get('roleIds', [])
        # print(f"角色列表: {role_ids}")

        if not isinstance(role_ids, list):
            return Response({"message": "参数格式错误，roleIds 必须是列表"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 3. 核心逻辑：使用 .set() 方法
            # 它会自动：删除该用户在 sys_user_role 中不在 role_ids 里的旧关联，并添加新的关联
            user.roles.set(role_ids)

            return Response({"message": f"用户 [{user.username}] 角色分配成功"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"分配失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class RolesViewSet(viewsets.ModelViewSet):
    """
    角色
    查看角色信息
    """
    queryset = SysRole.objects.all()
    serializer_class = RoleSerializer
    pagination_class = MyPagination

    def get_queryset(self):
        # 重写get_queryset方法用来返回一个queryset对象
        queryset = SysRole.objects.all().order_by('id')
        keyword = self.request.query_params.get('keyword')
        if keyword:
            queryset = queryset.filter(Q(name__icontains=keyword) | Q(remark__icontains=keyword))
        return queryset

    @action(detail=True, methods=['post'])
    def permissions(self, request, pk=None):
        print(f"DEBUG: 接收到的数据 -> {request.data}")
        """
        给角色分配菜单
        POST /api/sysrole/{id}/permissions/
        """
        role_obj = self.get_object()

        print(f"原始数据: {request.data}")
        menu_ids = request.data.get('menu_ids', [])

        if not isinstance(menu_ids, list):
            return Response({"message": "参数格式错误，roleIds 必须是列表"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            print("开始")
            role_obj.menus.set(menu_ids)
            print("结束")

            return Response({"message": f"用户 [{role_obj.name}] 角色分配成功"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"分配失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class MenuListView(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.UpdateModelMixin,
                   generics.GenericAPIView):
    # 只对一级菜单进行分页
    queryset = SysMenu.objects.filter(parent_id=0).order_by('order_num')
    serializer_class = MenuTreeSerializer
    pagination_class = MyPagination
    # 重写delete方法
    def get_queryset(self):
        # if self.request.method == 'DELETE':
        if self.request.method in ('DELETE', 'PATCH'):
            return  SysMenu.objects.all()
        return super().get_queryset()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)






class  TestView(APIView):
    @log_api_call
    def get(self, request):
        return  Response("测试")