import paramiko
import  subprocess
def ssh_exec(cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(
            hostname="162.251.x.x",
            username="root",
            password="xxxx",
            timeout=5
        )
        # 执行命令（cmd 必须是字符串，不能是列表）
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        exit_status = stdout.channel.recv_exit_status()  # 获取命令返回码
        return out, err, exit_status  # 返回元组，匹配 create 方法的预期
    except Exception as e:
        return "", str(e), 1  # 出错时返回错误信息
    finally:
        ssh.close()

