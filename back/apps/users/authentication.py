from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class MultiAuthBackend(BaseBackend):
    """
    支持邮箱、手机号和open_id登录的认证后端
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 尝试通过邮箱、手机号或open_id查找用户
        user = None
        
        if username:
            # 检查是否为邮箱格式
            if '@' in username:
                try:
                    user = User.objects.get(email=username)
                except User.DoesNotExist:
                    return None
            else:
                # 尝试通过open_id或手机号查找
                try:
                    user = User.objects.get(
                        Q(open_id=username) | Q(phone=username)
                    )
                except User.DoesNotExist:
                    return None
                except User.MultipleObjectsReturned:
                    # 如果有多个匹配的用户，返回None
                    return None
        
        if user and user.check_password(password):
            return user
        
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None