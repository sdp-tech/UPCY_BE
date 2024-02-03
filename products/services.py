import io
import time
import uuid


from django.shortcuts import get_list_or_404, get_object_or_404
from django.db import transaction
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

from products.models import Product, ProductKeyword, ProductPhoto, Category, Style, Fit, Texture, Detail
from products.selectors import ProductSelector
from users.models import User
# from .selectors import ProductSelector
#from core.exceptions import ApplicationError

class ProductCoordinatorService:
    def __init__(self, user:User):
        self.user=user
        #pass
    @transaction.atomic
    def create(self, name : str,keywords : list[str],basic_price : str,option : str,
               product_photos : list[str],info : str,notice : str,period : str,transaction_direct : bool,
               transaction_package : bool,refund : str,
               category : str, style : list[str], texture : list[str], fit : list[str], detail:list[str],
        ) -> Product:
        product_service=ProductService()
        
        product= product_service.create(
            reformer=self.user,
    
            category=category,
            style=style,
            texture=texture,
            fit=fit,
            detail=detail,
            
            name=name,
            basic_price=basic_price,
            option=option,
            info=info,
            notice=notice,
            period=period,
            transaction_direct=transaction_direct,
            transaction_package=transaction_package,
            refund=refund,
        )

        if product is not None:
            ProductPhotoService.process_photos(product=product, product_photos=product_photos )
            ProductKeywordService.process_keywords(product=product, keywords=keywords)
            return product
        else:
            raise ValueError('Product 생성 실패')

class ProductService:
    def __init__(self):
        pass

    @staticmethod
    def like_or_dislike(product:Product, user: User)-> bool:
        if ProductSelector.likes(product=product, user=user):
            product.likeuser_set.remove(user)
            product.like_cnt-=1
            
            product.full_clean()
            product.save()
            
            return False
        else:
            product.likeuser_set.add(user)
            product.like_cnt +=1
            
            product.full_clean()
            product.save()
            
            return True


    @staticmethod
    def create(name : str,basic_price : str,option : str,info : str,notice : str,
               period : str,transaction_direct : bool,transaction_package : bool,refund : str, reformer : User,
               category : str, style : list[str], texture : list[str], fit : list[str], detail:list[str],):
            category=get_object_or_404(Category,id=category)
            style=Style.objects.filter(id__in=style)
            texture=Texture.objects.filter(id__in=texture)
            fit=Fit.objects.filter(id__in=fit)
            detail=Detail.objects.filter(id__in=detail)
            
            product = Product(
                name = name,
                category=category,                
                basic_price = basic_price,
                option = option,
                info = info,
                notice = notice,
                period = period,
                transaction_direct = transaction_direct,
                transaction_package = transaction_package,
                refund = refund,
                reformer = reformer,
            )

            product.full_clean()
            product.save()
            
            product.style.set(style)
            product.texture.set(texture)
            product.fit.set(fit)
            product.detail.set(detail)
            return product
    

class ProductPhotoService:
    def __init__(self):
        pass
    
    @staticmethod
    def create(image:InMemoryUploadedFile):
        ext = image.name.split(".")[-1]
        file_path = '{}.{}'.format(str(time.time())+str(uuid.uuid4().hex),ext)
        image = ImageFile(io.BytesIO(image.read()),name=file_path)
        product_photo = ProductPhoto(image=image, product=None)
        
        product_photo.full_clean()
        product_photo.save()
        
        return settings.MEDIA_URL + product_photo.image.name
    
    @staticmethod
    def process_photos(product: Product, product_photos: list[str]):
        for product_photo in product_photos:
            op, photo_url = product_photo.split(',')
            
            photo_path = photo_url.replace(settings.MEDIA_ROOT,'').lstrip('/')
            
            try:
                product_photo, created = ProductPhoto.objects.get_or_create(image=photo_path)
            except Exception as e:
                print(f"Error in process_photos: {e}")
                product_photo = None
            
            if op == 'add':
                product_photo.product = product
                product_photo.full_clean()
                product_photo.save()
            elif op == 'remove':
                product_photo.delete()

            
                
class ProductKeywordService:
    def __init__(self):
        pass
    
    @staticmethod
    def process_keywords(product: Product, keywords: list[str]):
        print(keywords)
        for keyword_str in keywords:
            keyword_list= keyword_str.split(',')
            print(keyword_list)
            
            for k in keyword_list:
                ex_keyword = ProductKeyword.objects.filter(product=product,name=k)
                
                if not ex_keyword.exists():
                    new = ProductKeyword(product=product,name=k)
                    new.full_clean()
                    new.save()
                    print(f"Keyword : '{k}' 추가")
