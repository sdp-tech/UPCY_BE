
## 
from datetime import datetime
from dataclasses import dataclass
from django.db.models import Q, Case,Value, When, Exists, OuterRef
from services.models import Service
from users.models import User


# @dataclass
# class ServiceDto:
#     id : int

#     name : str
#     basic_price : str
#     category: dict
#     reformer : dict
#     style : list[dict]
#     texture:list[dict]
#     fit : list[dict]
#     detail :list[dict]

#     user_likes : bool  
    
#     created: datetime
#     updated: datetime

#     like_cnt : int = None
        
#     period : str =None 

#     option : list[dict] =None
#     info : str=None
#     notice : str = None
    
#     keywords: list[str] = None
#     photos: list[str] = None
#     nickname : str = None
#     market:str = None
 
#     transaction_direct:bool=None
#     transaction_package:bool=None
    
class ServiceSelector:
    def __init__(self):
        pass
    
    def likes(self, service:Service, user:User):
        return service.likeuser_set.filter(pk=user.pk).exists()