from  django.urls import  path

from  . import  views
urlpatterns = [
    path('health', views.HealthCheckView.as_view(), name='health_check'), #健康检查
]