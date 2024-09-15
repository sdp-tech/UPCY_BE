# from typing import List
from typing import Dict

# from django.db.models import QuerySet, Q, F
# from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from django.http import Http404, HttpResponseBadRequest

from users.models import ReformerProfile, User


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

class ReformerSelector:
    def __init__(self):
        pass

    @staticmethod
    def get_reformer_profile_by_user(user: Dict) -> QuerySet:
        reformer_profile = ReformerProfile.objects.select_related().filter(user=user).first()

        if not reformer_profile:
            raise ReformerProfile.DoesNotExist

        return reformer_profile
        