from  django.urls import  path
from rest_framework.routers import DefaultRouter
from  . import  views
from .views import MenuListView

# trailing_slash=False 不要/
router = DefaultRouter(trailing_slash=False)
# ViewSet 用户增删改查
router.register('sysuser', views.SysUserViewSet, basename='sysuser') #用户
router.register('sysrole', views.RolesViewSet, basename='sysrole')  #角色

app_name = 'dev_auth'
urlpatterns = [
    path('login', views.LoginView.as_view(), name='login'),
    path('test', views.TestView.as_view(), name='ceshi'),
    path('upload', views.UploadImageView.as_view(), name='upload'), #文件
    path('users/search', views.Userinfoview.as_view(), name='user-info'), #搜索+分页
    path('menus', views.MenuListView.as_view(), name='menu-list'),
    path('menus/<int:pk>/', MenuListView.as_view(), name='menu-detail')
] + router.urls
