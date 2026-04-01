FROM python:3.12.3

# 设置环境变量，防止 python 产生 pyc 文件及缓冲输出
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# 设置时区环境变量
ENV TZ=Asia/Shanghai
WORKDIR /www

# 复制项目文件
COPY . /www/

RUN apt-get update && apt-get install -y \
    sshpass \
    iproute2 \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# 合并安装步骤，节省空间
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir \
    -r requirements.txt \
    uwsgi==2.0.25.1 \
    ansible-core==2.14.16

#resolvelib==0.8.1
ENV ANSIBLE_HOST_KEY_CHECKING=False
copy hosts /etc/ansible/hosts

EXPOSE 8000


CMD ["uwsgi", "--ini", "uwsgi.ini"]