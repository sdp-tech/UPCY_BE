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
        
        try:
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
            print('create에 필요한 항목들 잘 가져오는지 확인 :',self.user,category, name, basic_price, option, info, notice, period, transaction_direct, transaction_package, refund)
            print(product,product.name)
            ##여기까지는 잘됨 !!!
            # 이 밑에서 잘 안되는 듯..
            if product is not None:
                ProductPhotoService.process_photos(product=product, product_photos=product_photos )
                ProductKeywordService.process_keywords(product=product, keywords=keywords)
                print(product)
                return product
            else:
                raise ValueError('Product 생성 실패')
            
        except ValueError as ve:
            print(f'productCoordinateService.create 에서 오류 발생 :{ve}')
            raise ve
        except Exception as e:
            print(f"ProductCoorniasdfad 에서 예상치 못한 오류 발생 :{e}")
            raise e
        # print(product_photos)
        # ProductPhotoService.process_photos(product=product,product_photos=product_photos)
        # ProductKeywordService.process_keywords(product=product,keywords=keywords)
        # return product
    
    
class ProductService:
    def __init__(self):
        pass

    @staticmethod
    def create(category: str,name : str,basic_price : str,option : str,info : str,notice : str,
               period : str,transaction_direct : bool,transaction_package : bool,refund : str, reformer : User):
        try:
            category = get_object_or_404(Category, id=category)
            
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

            product.full_clean()
            product.save()
            
            return product
    
        except Category.DoesNotExist:
            print('해당 카테고리를 찾을 수 X')
            raise ValueError("해당카테고리를 찾을 수 없습니다")
        except Exception as e:
            print(f'ProductService.create 오류 : {e}')
            raise ValueError("ProductSerivce.create 오류 발생")

class ProductPhotoService:
    def __init__(self):
        pass
    
    @staticmethod
    def create(image:InMemoryUploadedFile, product:Product):
        ext = image.name.split(".")[-1]
        file_path = '{}.{}'.format(str(time.time())+str(uuid.uuid4().hex),ext)
        image = ImageFile(io.BytesIO(image.read()),name=file_path)
        product_photo = ProductPhoto(image=image, product=product)
        
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
            