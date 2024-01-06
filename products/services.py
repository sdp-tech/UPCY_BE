import io
import time
import uuid


from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

from products.models import Category, Product, ProductKeyword, ProductPhoto
from users.models import User
#from core.exceptions import ApplicationError

class ProductCoordinatorService:
    def __init__(self, user:User):
        self.user=user
        #pass
    @transaction.atomic
    def create(self, category: str, name : str,keywords : list[str],basic_price : str,option : str,
               product_photos : list[str],info : str,notice : str,period : str,transaction_direct : bool,
               transaction_package : bool,refund : str,
        ) -> Product:
        product_service=ProductService()
        product= product_service.create(
            reformer=self.user,
            category=category,
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
        ##productPhoto랑 keywords 다시 구현 필요
        ProductPhotoService.process_photos(product=product,product_photos=product_photos)
        ProductKeywordService.process_keywords(product=product,keywords=keywords)
        return product
    
class ProductService:
    def __init__(self):
        pass

    @staticmethod
    def create(category: str,name : str,basic_price : str,option : str,info : str,notice : str,
               period : str,transaction_direct : bool,transaction_package : bool,refund : str, reformer : User):
        
        category = get_object_or_404(Category, id=category)
        #reformer = User.objects.get(email='0321minji@ewhain.net')
        
        product = Product(
            name = name,
            category = category,
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
        print('reformer',product.reformer)
        product.full_clean()
        product.save()
        
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
            product_photo = get_object_or_404(
                ProductPhoto, image=photo_url.replace(settings.MEDIA_URL,''))
            
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
        for keyword in keywords:
            op, name= keyword.split(',')
            keyword = ProductKeyword.objects.filter(product=product,name=name)
            
            if op=='add' and not keywords.exits():
                keyword= ProductKeyword(product=product,name=name)
                keyword.full_clean()
                keyword.save()
            # else:
            #     raise ApplicationError("지원하지 않는 keyword 연산입니다.")