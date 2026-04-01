from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from .models import SysUser, SysRole,SysMenu
from django.contrib.auth.hashers import make_password,check_password


class  LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True,error_messages={'required':'请输入正确的用户'})
    password = serializers.CharField(max_length=20, min_length=6, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        # print(password)
        if username and password:
            user = SysUser.objects.filter(username=username).first()
            if not user:
                raise serializers.ValidationError('该用户不存在，请输入正确的用户')
            # if user.password != password:
            if not check_password(password, user.password):
                raise serializers.ValidationError('请输入正确的密码')
            #判断状态
            if user.status == 1:
                raise serializers.ValidationError('该用户停用')
            #为了查找sql语句次数，这里我把user直接放到attrs中方便视图中使用
            attrs['user'] = user
        else:
            raise serializers.ValidationError('请传入用户名和密码')
        return attrs


class RoleSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    # 显示中文

    menus_names = serializers.SerializerMethodField()
    class Meta:
        model = SysRole
        fields = '__all__'
        # 可以用allow_empty 传一个空列表
        extra_kwargs = {'menus': {'required': False, 'allow_empty': True}}

    def get_menus_names(self, obj):
        return list(obj.menus.values_list('name', flat=True))


class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True,read_only=True)
    create_time = serializers.DateTimeField(format='%Y-%m-%d', read_only=True)
    login_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    class Meta:
        model = SysUser
        exclude = ['password']



class SysUserSerializer(serializers.ModelSerializer):
    # 密码设为只写，默认 123456
    password = serializers.CharField(write_only=True, required=False, default='123456')
    # 获取角色name值
    # roles_name = serializers.SlugRelatedField(many=True,read_only=True,slug_field='name',source='roles')
    class Meta:
        model = SysUser
        fields = ['id', 'username', 'password', 'phonenumber','email', 'status', 'remark']
        extra_kwargs = {
            # 'username': {'max_length': 20, 'min_length': 6, 'error_messages': {'required': '请输入用户名'}}
        }

    def validate(self, attrs):
        request = self.context.get('request')
        print("1",request.user)
        username = attrs.get('username')

        user_id = self.instance.id if self.instance else None
        # print("2",user_id)
        if SysUser.objects.filter(username=username).exclude(id=user_id).exists():
            raise serializers.ValidationError('用户名已存在')


        return attrs

    def create(self, validated_data):
        # 添加用户
        password = validated_data.pop('password', '123456')
        user = SysUser.objects.create(**validated_data)
        user.password = make_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        # 这里的白名单逻辑非常棒，完美实现了“不修改用户名和密码”
        allowed_fields = ['phonenumber', 'email', 'status','remark']
        for attr in allowed_fields:
            if attr in validated_data:
                setattr(instance, attr, validated_data[attr])
        instance.save()
        return instance




class MenuTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = SysMenu
        fields = ['id', 'name', 'parent_id','path', 'icon', 'menu_type', 'create_time', 'perms', 'children']

    def get_children(self, obj):
        # 递归查询子节点
        children = SysMenu.objects.filter(parent_id=obj.id).order_by('order_num')
        if children.exists():
            return MenuTreeSerializer(children, many=True).data
        return []



# 上传图片文件
class UploadImageSerializer(serializers.Serializer):
    image = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
                                   error_messages={'required': '请上传图片!', 'invalid_image': '请上传正确的格式的图片'})

    def validate_image(self, value):
        #图片大小
        max_size =  0.5 * 1024 * 1024
        size = value.size
        if size > max_size:
            raise serializers.ValidationError('图片不能超过0.5MB!')
        return value
