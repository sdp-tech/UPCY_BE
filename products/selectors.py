
## 
from datetime import datetime
from dataclasses import dataclass
from django.db.models import Q, Case,Value, When, Exists, OuterRef
from products.models import Product
from users.models import User


@dataclass
class ProductDto:
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
        
    period : str =None 

    option : list[dict] =None
    info : str=None
    notice : str = None
    
    keywords: list[str] = None
    photos: list[str] = None
    
    
class ProductSelector:
    def __init__(self):
        pass

    @staticmethod
    def list(search: str,order : str, user: User,
             category_filter:str, style_filters:list[str], fit_filters:list[str],texture_filters:list[str],detail_filters:list[str],):
        q=Q()
        # #검색 조건 후에 수정 
        # q.add(Q(info__icontains=search), q.AND)
        
        if category_filter:
            q.add(Q(category__id__iexact=category_filter),q.AND)
        

        if style_filters:
            style_filter_q = Q()
            for style_filter in style_filters:
                style_filter_q.add(
                    Q(style__id=style_filter), q.OR)
            q.add(style_filter_q, q.AND)
            
        if fit_filters:
            fit_filter_q=Q()
            for fit_filter in fit_filters:
                fit_filter_q.add(
                    Q(fit__id=fit_filter),q.OR)
            q.add(fit_filter_q, q.AND)
            
        if texture_filters:
            texture_filter_q=Q()
            for texture_filter in texture_filters:
                texture_filter_q.add(
                    Q(texture__id=texture_filter),q.OR)
            q.add(texture_filter_q,q.AND)
        
        if detail_filters:
            option_filter_q=Q()
            for option_filter in detail_filters:
                option_filter_q.add(
                    Q(option__id=option_filter),q.OR)
            q.add(option_filter_q,q.AND)
        
        order_pair={'latest':'-created',
                    'oldest':'created',
                    'hot':'-created'}
        
        products = Product.objects.distinct().annotate(
            user_likes = Case(
                When(Exists(Product.likeuser_set.through.objects.filter(
                   product_id=OuterRef('pk'),
                   user_id=user.pk 
                )),
                     then=Value(1)),
                default=Value(0),
            ),
        ).select_related(
            'reformer','category'
        ).prefetch_related(
            'keywords','product_photos','style','fit','texture','detail'
        ).filter(q).order_by(order_pair[order])       
        
        products_dtos =[ ProductDto(
            id=product.id,
            name=product.name,
            basic_price=product.basic_price,
            reformer=product.reformer,
            # reformer={
            #     'nickname':product.reformer.nickname,
            #     'profile_image':product.reformer.profile_image,
            # },
            user_likes=product.user_likes,
            created=product.created.strftime('%Y-%m-%dT%H:%M:%S%z'),
            updated=product.updated.strftime('%Y-%m-%dT%H:%M:%S%z'),
            
            category={'id':product.category.id,
                      'name':product.category.name},
            style=[{'id':s.id,'name':s.name}
                   for s in product.style.all()],
            fit=[{'id':f.id,'name':f.name}
                 for f in product.fit.all()],
            texture=[{'id':t.id,'name':t.name}
                     for t in product.texture.all()],
            detail=[{'id':d.id,'name':d.name}
                     for d in product.detail.all()],

            keywords=[keywords.name for keywords in product.keywords.all()],
            photos=[photos.image.url for photos in product.product_photos.all()],
            
            period=product.period,
            # option=product.option,
            # info=product.info,
            # notice=product.notice,   
        ) for product in products]
        
        
        return products_dtos
    
    def likes(self, product:Product, user:User):
        return product.likeuser_set.filter(pk=user.pk).exists()