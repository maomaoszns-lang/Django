from django.db import models

from apps.dev_auth.models import SysUser


class Ansibleconfig(models.Model):
    ansible_playbook_path = models.CharField(max_length=200, verbose_name='剧本路径')
    host_file = models.CharField(max_length=200, verbose_name='host文件')
    target_group = models.CharField(max_length=200, verbose_name='目标组')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    class Meta:
        verbose_name = 'Ansible 部署配置'

    def __str__(self):
        return self.ansible_playbook_path


# Create your models here.
class Ansiblecomd(models.Model):
    STATUS_CHOICES = [
        (0, '成功'),
        (1, '失败'),
        (2, '执行中'),
        (3, '未执行'),
    ]
    # user = models.ForeignKey(SysUser, on_delete=models.SET_NULL, verbose_name='执行人',null=True,blank=True)
    config = models.ForeignKey(to=Ansibleconfig,on_delete=models.CASCADE, verbose_name='关联配置')
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES,verbose_name='状态',default=3)
    start_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    end_time = models.DateTimeField(verbose_name='结束时间',blank=True,null=True)
    source_output = models.TextField(verbose_name='成功日志',blank=True,default='')
    error_output = models.TextField(verbose_name='错误日志', blank=True,default='')

    class Meta:
        verbose_name = 'Ansible 命令记录'
        verbose_name_plural = 'Ansible 命令记录'

    def __str__(self):
        # return f'{self.status}'
        return f"任务ID:{self.pk} - 状态:{self.get_status_display()}"
