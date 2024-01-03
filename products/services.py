import io
import time
import uuid

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

from products.models import Product, ProductKeyword, ProductPhoto
#from core.exceptions import ApplicationError

class ProductCoordinatorService:
    def __init__(self):
        pass
    @staticmethod
    @transaction.atomic
    def create(category: str,
               name : str,
               #keywords : list[str],
               basic_price : str,
               option : list[str],
               #image : InMemoryUploadedFile,
               product_photos : list[str],
               info : str,
               notice : str,
               period : str,
               transaction_direct : bool,
               transaction_package : bool,
               refund : str,
               reformer : str) -> Product:
        
        product = ProductService.create(
            category=category,
            name=name,
            #keyword=keyword,
            basic_price=basic_price,
            option=option,
            info=info,
            notice=notice,
            period=period,
            transaction_direct=transaction_direct,
            transaction_package=transaction_package,
            refund=refund,
            reformer=reformer,
        )
        ##productPhoto랑 keywords 다시 구현 필요
        ProductPhotoService.process_photos(product=product,
                                           product_photos=product_photos)
        ProductKeywordService.process_keywords(product=product,
                                               keywords=keywords)
        return product
    
class ProductService:
    def __init__(self):
        pass

    @staticmethod
    def create(category: str,
               name : str,
               #keyword : list[str],
               basic_price : str,
               option : list[str],
               #product_photos : InMemoryUploadedFile,
               info : str,
               notice : str,
               period : str,
               transaction_direct : bool,
               transaction_package : bool,
               refund : str,
               reformer : str):
        
        product = Product(
            name = name,
            category = category,
            basic_price = basic_price,
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
        
        return product

class ProductPhotoService:
    def __init__(self):
        pass
    
    @staticmethod
    def  create(image:InMemoryUploadedFile):
        ext = image.name.split(".")[-1]
        file_path = '{}.{}'.format(str(time.imte())+str(uuid.uuid4().hex),ext)
        image = ImageFile(io.BytesIO(image.read()),name=file_path)
        product_photo = ProductPhoto(image=image, product=None)
        
        product_photo.full_clean()
        product_photo.save()
        
        return settings.MEDIA_URL + product_photo.image.name
    
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
            #keyword = ProductKeyword.objects.filter(product=product)
            
            if op=='add' and not keywords.exits():
                keyword= ProductKeyword(product=product,name=name)
                keyword.full_clean()
                keyword.save()
