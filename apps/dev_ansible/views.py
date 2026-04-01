from django.db.models import Q
from rest_framework.decorators import action
from django.shortcuts import render
from rest_framework import viewsets, generics
from datetime import datetime
import os
from utls.paginations import MyPagination
from .tasks import run_ansible_playbook_task
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .serializers import AnsibleconfigSerializer, AnsiblecomdSerializer
from .models import Ansibleconfig, Ansiblecomd


# Create your views here.
# 创建配置文件
class AnsiblePlaybookViewSet(viewsets.ModelViewSet):
    queryset = Ansibleconfig.objects.all()
    serializer_class = AnsibleconfigSerializer
    pagination_class = MyPagination


# 创建待执行任务 运行待执行任务
#http://127.0.0.1:8000/api/run/ 创建
#http://127.0.0.1:8000/api/run/1/ 删除
#http://127.0.0.1:8000/api/run/{pk}/playbook/ 运行

class AnsiblecomdViewSet(viewsets.ModelViewSet):
    queryset = Ansiblecomd.objects.all().order_by('id')
    serializer_class = AnsiblecomdSerializer
    pagination_class = MyPagination


    @action(detail=True, methods=['post'], url_path='playbook')
    def run_playbook(self, request, pk=None):
        try:
            # 1. 获取目标记录（通过 PK）
            record = self.get_object()
        except Exception as e:
            return Response({"error": f"ID 为 {pk} 的任务记录不存在。{e}"}, status=status.HTTP_404_NOT_FOUND)

        # 2. 检查记录状态 (可选，但推荐)
        # print("----",record.status)
        if record.status in [0, 1, 2]:
            # 0=成功, 1=失败, 2=执行中 3=未执行
            return Response({"error": f"任务已执行或正在执行中 (当前状态: {record.status})。"},status=status.HTTP_400_BAD_REQUEST)

        config_instance = record.config
        # print("config_instance",config_instance)

        # 3. 立即更新状态为“执行中” (2)
        record.status = 2
        record.start_time = datetime.now()  # 重新设置开始时间
        record.save()

        # 4. 准备 Celery 任务参数
        # 依赖于关联的 Ansibleconfig
        try:
            ansible_playbook_path_remote = os.path.join(settings.ANSIBLE_BOOK,config_instance.ansible_playbook_path)
            # print("----",ansible_playbook_path_remote)
            hosts_file = config_instance.host_file
            target_group = config_instance.target_group
        except Exception as e:
            # 如果配置信息有问题，记录错误并返回
            record.status = 1
            record.error_output = f"配置数据读取失败: {str(e)}"
            record.end_time = datetime.now()
            record.save()
            return Response({"error": f"配置信息错误: {str(e)}"},status=status.HTTP_400_BAD_REQUEST)

        #  【关键】将任务发送给 Celery Worker 异步
        run_ansible_playbook_task.delay(
            record.id,
            ansible_playbook_path_remote,
            hosts_file,
            target_group
        )

        return Response(self.get_serializer(record).data,status=status.HTTP_200_OK)
