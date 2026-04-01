from   devops import  celery_app
import  subprocess
from  datetime import datetime
from .models import Ansiblecomd

"""
celery 定义任务
"""
# 定义名字
@celery_app.task()
def run_ansible_playbook_task(record_id, ansible_playbook_path_remote, hosts_file, target_group):
    """
        Celery 任务：在后台执行 Ansible Playbook 并更新记录。
        """
    try:
        record = Ansiblecomd.objects.get(pk=record_id)

        # 1. 构建完整的远程 Ansible 命令字符串 (与原视图函数逻辑相同)
        extra_vars = f"'{target_group}'"
        # ansible-playbook -i /etc/ansible/hosts /ansible_playbooks/nginx.yml -e 'web'
        ansible_command_list = [
            'ansible-playbook',
            '-i', hosts_file,  # 远程 Inventory 文件
            ansible_playbook_path_remote,
            '-e', extra_vars,
        ]

        final_cmd = " ".join(ansible_command_list)

        # 2. 执行命令
        result = subprocess.run(
            final_cmd,
            capture_output=True,
            text=True,
            check=False,
            shell=True  # 允许 shell 执行，因为 final_cmd 是一个完整的字符串
        )

        # 3. 更新记录结果
        record.end_time = datetime.now()
        record.source_output = result.stdout  # 注意：您的模型中字段名为 source_output
        record.error_output = result.stderr

        if result.returncode == 0:
            record.status = 0  # 成功
            record.end_time = datetime.now()
        else:
            record.status = 1  # 失败
            record.end_time = datetime.now()
    except Ansiblecomd.DoesNotExist:
        print(f"Error: Ansiblecomd record {record_id} not found.")
        # 可能还需要其他错误处理

    except Exception as e:
        # 处理系统级执行错误
        record.end_time = datetime.now()
        record.status = 1
        record.error_output = f"系统执行错误或任务内部错误: {str(e)}"
        record.source_output = record.error_output

    finally:
        # 4. 保存最终结果到数据库
        # if 'record' in locals():
            record.save()

