
## 
from datetime import datetime
from dataclasses import dataclass
from django.db.models import Q, Case,Value, When, Exists, OuterRef
from services.models import Service
from users.models import User


@dataclass
class ServiceDto:
     id : int

     name : str
     basic_price : str
     category: dict
     reformer : dict
     style : list[dict]
     texture:list[dict]
     fit : list[dict]
     detail :list[dict]

     user_likes : bool  
    
     created: datetime
     updated: datetime

     like_cnt : int = None
        
     period : str = None 

     option : list[dict] =None
     info : str=None
     notice : str = None
    
     keywords: list[str] = None
     photos: str = None #원래는 list[str]인데, 일단 service 하나당 photo 하나만 추가할 수 있는 것으로
     nickname : str = None
     market:str = None
 
     transaction_direct:bool=None
     transaction_package:bool=None
    
class ServiceSelector:
    def __init__(self):
        pass

    @staticmethod
    def detail(service_id:str, user:User):
        service=Service.objects.annotate(
            user_likes=Case(
                When(Exists(Service.likeuser_set.through.objects.filter(
                    service_id=OuterRef('pk'),
                    user_id=user.pk
                )),
                    then=Value(1)),
                default=Value(0),
            ),
        ).select_related(
            'category','reformer'
        ).prefetch_related(
            'keywords','service_photos','style','fit','texture','detail'
        ).get(
            id=service_id
        )

        service_dto=ServiceDto(
            id=service.id,
            name=service.name,
            nickname=service.reformer.nickname,
            # market=user.market_name,
            basic_price=service.basic_price,
            reformer=service.reformer,
            user_likes=service.user_likes,
            created=service.created.strftime('%Y-%m-%dT%H:%M:%S%z'),
            updated=service.updated.strftime('%Y-%m-%dT%H:%M:%S%z'),

            transaction_direct=service.transaction_direct,
            transaction_package=service.transaction_package,

            category={'id':service.category.id,
                      'name':service.category.name},
            style=[{'id':s.id, 'name':s.name}
                   for s in service.style.all()],
            fit=[{'id':f.id, 'name':f.name}
                 for f in service.fit.all()],
            texture=[{'id':t.id, 'name':t.name}
                   for t in service.texture.all()],
            detail=[{'id':d.id, 'name':d.name}
                   for d in service.detail.all()],
            
            keywords=[keywords.name for keywords in service.keywords.all()],
            photos=[photos.imgage.url for photos in service.service_photos.all()],
            
            period=service.period,
            option=service.option,
            info=service.info,
            notice=service.notice,
            like_cnt=service.like_cnt
        )
        return service_dto

    @staticmethod
    def list(search:str, order:str, user:User,
             category_filter:str, style_filters:list[str],
             fit_filters:list[str],texture_filters:list[str],
             detail_filters:list[str],):
        q=Q()
        # #검색 조건 후에 수정 
        # q.add(Q(info__icontains=search), q.AND)

        if category_filter:
            q.add(Q(category__id__iexact=category_filter), q.AND)

        if style_filters:
            style_filter_q = Q()
            for style_filter in style_filters:
                style_filter_q.add(
                    Q(style__id=style_filter), q.OR
                )
            q.add(style_filter_q, q.AND)

        if fit_filters:
            fit_filter_q = Q()
            for fit_filter in fit_filters:
                fit_filter_q.add(
                    Q(fit__id=fit_filter), q.OR
                )
            q.add(fit_filter_q, q.AND)

        if texture_filters:
            texture_filter_q = Q()
            for texture_filter in texture_filters:
                texture_filter_q.add(
                    Q(texture__id=texture_filter), q.OR
                )
            q.add(texture_filter_q, q.AND)

        if detail_filters:
            option_filter_q = Q()
            for option_filter in detail_filters:
                option_filter_q.add(
                    Q(option__id=option_filter), q.OR
                )
            q.add(option_filter_q, q.AND)
        
        order_pair={'latest':'-created',
                    'oldest':'created',
                    'hot':'-created'}
        
        services=Service.objects.distinct().annotate(
            user_likes=Case(
                When(Exists(Service.likeuser_set.through.objects.filter(
                    service_id=OuterRef('pk'),
                    user_id=user.pk
                )),
                     then=Value(1)),
                default=Value(0),
            ),
        ).select_related(
            'reformer','category'
        ).prefetch_related(
            'keywords','service_photos','style','fit','texture','detail'
        ).filter(q).order_by(order_pair[order])

        services_dtos = [ ServiceDto(
            id=service.id,
            name=service.name,
            basic_price=service.basic_price,
            reformer=service.reformer,
            user_likes=service.user_likes,
            created=service.created.strftime('%Y-%m-%dT%H:%M:%S%z'),
            updated=service.updated.strftime('%Y-%m-%dT%H:%M:%S%z'),

            category={'id':service.category.id,
                      'name':service.category.name},
            style=[{'id':s.id,'name':s.name}
                   for s in service.style.all()],
            fit=[{'id':f.id,'name':f.name}
                 for f in service.fit.all()],
            texture=[{'id':t.id,'name':t.name}
                     for t in service.texture.all()],
            detail=[{'id':d.id,'name':d.name}
                     for d in service.detail.all()],

            keywords=[keywords.name for keywords in service.keywords.all()],
            photos=[photos.image.url for photos in service.service_photos.all()],

            period=service.period,
            

        ) for service in services]

        return services_dtos
    def likes(self, service:Service, user:User):
        return service.likeuser_set.filter(pk=user.pk).exists()