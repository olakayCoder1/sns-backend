from rest_framework import serializers

from db_schema.models import *

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "role_id", "name"]

class UserInfoSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = UserInfo
        fields = ["name", "last_name", "first_name", "name_furi", "last_name_furi", "first_name_furi", "phone","is_youtube","is_instagram","is_tiktok","is_twitter", "role"]
        
class UserSerializer(serializers.ModelSerializer):
    user_info = UserInfoSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "user_id", 'email', "user_info", "created_at", "updated_at", 'is_active', 'is_allowed', 'permission']
        
class UserNameSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["id", 'email', "name"]

    def get_name(self, obj):
        obj = User.objects.get(id=obj.id)
        return obj.user_info.name
        
class UserFlatSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    is_allowed = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = UserInfo
        fields = ["id", "last_name", "first_name", "last_name_furi", "first_name_furi", "phone", 'email', 'role', 'is_allowed']

    def get_id(self, obj):
        user = User.objects.get(user_info=obj)
        return user.id

    def get_email(self, obj):
        user = User.objects.get(user_info=obj)
        return user.email
    
    def get_is_allowed(self, obj):
        user = User.objects.get(user_info=obj)
        return user.is_allowed