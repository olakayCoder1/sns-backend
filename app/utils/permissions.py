from rest_framework import permissions
from jwt_auth.serializers import *

class IsAuthenticated(permissions.BasePermission):
    message = 'You are not allowed.'


    def has_permission(self, request, view):
        try:
            if request.user.is_active and request.user.is_allowed:
                return True
            else:
                return False
        except:
            return False
        

class IsSuper(IsAuthenticated):
    message = 'You are not allowed.'


    def has_permission(self, request, view):

        try:
            if request.user.permission == "super":
                return True
            else:
                return False
        except:
            return False

class IsOwner(IsAuthenticated):
    message = 'You are not allowed.'


    def has_permission(self, request, view):
        try:
            if request.user.permission == "owner":
                return True
            else:
                return False
        except:
            return False
        

class IsCustomer(IsAuthenticated):
    message = 'You are not allowed.'


    def has_permission(self, request, view):
        try:
            if request.user.permission == "customer":
                return True
            else:
                return False
        except:
            return False
        
class IsCustomerAndAdmin(IsCustomer):
    message = 'You are not allowed.'


    def has_permission(self, request, view):
        try:
            user = UserSerializer(request.user).data
            if user['user_info']['role']['role_id'] == "admin" :
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False
        
class IsCustomerAndMember(IsCustomer):
    message = 'You are not allowed.'


    def has_permission(self, request, view):
        try:
            user = UserSerializer(request.user).data
            if user['user_info']['role']['role_id'] == "member" :
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False
        
        

def get_role(user):
    try:
        user = UserSerializer(user).data
        return user['user_info']['role']['role_id']
    except Exception as e:
        print(str(e))
        return ""