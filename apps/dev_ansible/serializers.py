from rest_framework import serializers
from .models import Ansiblecomd, Ansibleconfig


class AnsibleconfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ansibleconfig
        fields = '__all__'

class AnsiblecomdSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M',read_only=True)
    end_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M',read_only=True)
    config_detail = AnsibleconfigSerializer( source='config',read_only=True)
    config_data = AnsibleconfigSerializer( write_only=True )
    # ansible_user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Ansiblecomd
        fields = ['id', 'config_data','config_detail','status','start_time','end_time','source_output','error_output']

        # fields = ('id', 'config_data', 'status', 'start_time', 'end_time', 'source_output','error_output')


    #查找或创建 Ansibleconfig 记录
    def create(self, validated_data):
        # 1. 提取配置数据，如果没传则为空字典
        config_data = validated_data.pop('config_data', {})
        # config_data = validated_data.pop('config', {})
        config_instance, created = Ansibleconfig.objects.get_or_create(**config_data)


        # 4. 创建 Ansiblecomd 记录，并关联找到/创建的 config 实例
        ansiblecomd = Ansiblecomd.objects.create(config=config_instance, **validated_data)

        return ansiblecomd






