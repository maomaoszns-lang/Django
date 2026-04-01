from django.db import models


# 1. 菜单/权限表
class SysMenu(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, verbose_name="菜单名称")
    icon = models.CharField(max_length=100, null=True, blank=True, verbose_name="菜单图标")
    # 建议：使用 ForeignKey 指向自身实现树形结构，比 IntegerField 更方便查询
    parent_id = models.IntegerField(null=True, blank=True, verbose_name="父菜单ID")
    order_num = models.IntegerField(null=True, verbose_name="显示顺序")
    path = models.CharField(max_length=200, null=True, blank=True, verbose_name="路由地址")
    component = models.CharField(max_length=255, null=True, blank=True, verbose_name="组件路径")
    menu_type = models.CharField(max_length=1, null=True, verbose_name="菜单类型（M目录 C菜单 F按钮）")
    perms = models.CharField(max_length=100, null=True, blank=True, verbose_name="权限标识")
    create_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    remark = models.CharField(max_length=500, null=True, blank=True, verbose_name="备注")

    class Meta:
        db_table = "sys_menu"


# 2. 角色表
class SysRole(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, null=True, verbose_name="角色名称")
    code = models.CharField(max_length=100, null=True, verbose_name="角色权限字符串")
    # 【新增】角色与菜单的多对多关联：自动生成 sys_role_menu 表
    menus = models.ManyToManyField(SysMenu, db_table="sys_role_menu", related_name="roles", verbose_name="拥有权限")

    create_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    remark = models.CharField(max_length=500, null=True, blank=True, verbose_name="备注")

    class Meta:
        db_table = "sys_role"


# 3. 用户表
class SysUser(models.Model):
    category_choices = ((0, "正常"), (1, "激活"))
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True, verbose_name="用户名")
    password = models.CharField(max_length=128, verbose_name="密码")
    avatar = models.CharField(max_length=255, null=True, blank=True, verbose_name="用户头像")
    email = models.CharField(max_length=100, null=True, blank=True, verbose_name="用户邮箱")
    phonenumber = models.CharField(max_length=11, null=True, blank=True, verbose_name="手机号码")
    login_date = models.DateTimeField(null=True, blank=True, verbose_name="最后登录时间")
    status = models.IntegerField(choices=category_choices,default=0, verbose_name="帐号状态（0正常 1停用）")
    # 【新增】用户与角色的多对多关联：自动生成 sys_user_role 表
    roles = models.ManyToManyField(SysRole, db_table="sys_user_role", related_name="users", verbose_name="拥有角色")

    create_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    remark = models.CharField(max_length=500, null=True, blank=True, verbose_name="备注")

    class Meta:
        db_table = "sys_user"


    def __str__(self):
        return self.username

