from django.urls import  path
from rest_framework import  routers
from .views import   AnsiblecomdViewSet,AnsiblePlaybookViewSet

#创建一个路由器实列
router = routers.DefaultRouter(trailing_slash=False)

router.register('run', AnsiblecomdViewSet,basename='run')

router.register('ansible', AnsiblePlaybookViewSet ,basename='ansible')

urlpatterns = []+router.urls