# from typing import List
from typing import Dict

# from django.db.models import QuerySet, Q, F
# from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseBadRequest

from users.models import ReformerProfile, User, UserProfile


class UserSelector:
    def __init__(self):
        pass

    @staticmethod
    def get_user_by_email(email: str) -> User:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise Http404
        except User.MultipleObjectsReturned:
            raise Http404
        
    @staticmethod
    def check_password(user: User, password: str):
        return user.check_password(password)
    
    @staticmethod
    def get_user_profile_by_email(email:str) -> Dict:
        try:
            user = User.objects.get(email=email)
            user_profile = UserProfile.objects.get(user=user)
            
            data = {
                "nickname": user.nickname,
                "profile_image": user_profile.profile_image, 
                "introduce": user_profile.introduce,
            }
            return data
        except ObjectDoesNotExist:
            return {
                "error": "User or UserProfile not found"
            }

class ReformerSelector:
    def __init__(self):
        pass
    @staticmethod
    def profile(user_id:str):
        profile=ReformerProfile.objects.get(user__id=user_id)
        return{
            'market_intro':profile.market_intro,
            'links':profile.links,
            'area':profile.user.area,
            'carrer':profile.school +' '+ profile.major
        }
        