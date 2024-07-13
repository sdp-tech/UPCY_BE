import uuid
import boto3
import io
from django.shortcuts import get_list_or_404, get_object_or_404
from django.db import transaction
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

from services.models import Service, ServiceKeyword, ServicePhoto, Category, Style, Fit, Texture, Detail
from .selectors import ServiceSelector
from users.models import User
from core.utils import s3_file_upload_by_file_data
from UpcyProject.settings import settings


class ServiceCoordinatorService:
    def __init__(self,user:User):
        self.user=user
        
    @transaction.atomic
    def create(self, name : str,keywords : list[str],basic_price : str, max_price: str, option : str,
               service_photos : list[str],info : str,notice : str,period : str,transaction_direct : bool,
               transaction_package : bool,refund : str,
               category : str, style : list[str], texture : list[str], fit : list[str], detail:list[str],
        ) -> Service:
        service_service=ServiceService()
        service= service_service.create(
            reformer=self.user,
    
            category=category,
            style=style,
            texture=texture,
            fit=fit,
            detail=detail,
            
            name=name,
            basic_price=basic_price,
            max_price=max_price,
            option=option,
            info=info,
            notice=notice,
            period=period,
            transaction_direct=transaction_direct,
            transaction_package=transaction_package,
            refund=refund,
        )

        if service is not None:
            ServicePhotoService.process_photos(service=service, service_photos=service_photos )
            ServiceKeywordService.process_keywords(service=service, keywords=keywords)
            return service
        else:
            raise ValueError('Service 생성 실패')

    
class ServiceService:
    def __init__(self):
        pass
    
    @staticmethod
    def like_or_dislike(service:Service, user: User)-> bool:
        selector = ServiceSelector()
        if selector.likes(service=service, user=user):
            service.likeuser_set.remove(user)
            service.like_cnt-=1
            
            service.full_clean()
            service.save()
            
            return False
        else:
            service.likeuser_set.add(user)
            service.like_cnt +=1
            
            service.full_clean()
            service.save()
            
            return True
    @staticmethod
    def create(name : str,basic_price : str, max_price: str, option : str,info : str,notice : str,
               period : str,transaction_direct : bool,transaction_package : bool,refund : str, reformer : User,
               category : str, style : list[str], texture : list[str], fit : list[str], detail:list[str],):
            category=get_object_or_404(Category,id=category)
            style=Style.objects.filter(id__in=style)
            texture=Texture.objects.filter(id__in=texture)
            fit=Fit.objects.filter(id__in=fit)
            detail=Detail.objects.filter(id__in=detail)
            
            service = Service(
                name = name,
                category=category,                
                basic_price = basic_price,
                max_price = max_price,
                option = option,
                info = info,
                notice = notice,
                period = period,
                transaction_direct = transaction_direct,
                transaction_package = transaction_package,
                refund = refund,
                reformer = reformer,
            )

            service.full_clean()
            service.save()
            
            service.style.set(style)
            service.texture.set(texture)
            service.fit.set(fit)
            service.detail.set(detail)
            return service
    
    @staticmethod
    def update(service,data):
        for key,value in data.items():
            setattr(service,key,value)
        service.save()
        return service
    
class ServicePhotoService:
    def __init__(self, file):
        self.file = file

    def upload(self):
        s3_client = boto3.client(
            's3',
            aws_access_key_id = settings.AWS_ACCESS_KEY_ID, 
            aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        )
        extension = self.file.name.split('.')[-1]
        url = f'services/photo/{uuid.uuid1().hex}.{extension}'

        file_data = io.BytesIO(self.file.read())
        file_data.seek(0)

        try:
            s3_client.upload_fileobj(
                file_data,  # 파일 데이터 객체
                "upcy-bucket",
                url,
                ExtraArgs={
                    "ContentType": self.file.content_type
                }
            )
            return f"https://upcy-bucket.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{url}"
        
        except Exception as e:
            print(f"Failed to upload file to S3: {e}")
            return None

    @staticmethod
    def process_photos(service:Service, service_photos: list[str]):
        for service_photo in service_photos:
            op, photo_url = service_photo.split(',')
            
            photo_path = photo_url.replace(settings.MEDIA_ROOT,'').lstrip('/')
            
            try:
                service_photo, created = ServicePhoto.objects.get_or_create(image=photo_path)
            except Exception as e:
                print(f"Error in process_photos: {e}")
                service_photo = None
            
            if op == 'add' and service_photo :
                service_photo.service = service
                service_photo.full_clean()
                service_photo.save()
            elif op == 'remove' and service_photo :
                service_photo.delete()

class ServiceKeywordService:
    def __init__(self):
        pass
    
    @staticmethod
    def process_keywords(service: Service, keywords: list[str]):
        print(keywords)
        for keyword_str in keywords:
            keyword_list= keyword_str.split(',')
            print(keyword_list)
            
            for k in keyword_list:
                ex_keyword = ServiceKeyword.objects.filter(service=service,name=k)
                
                if not ex_keyword.exists():
                    new = ServiceKeyword(service=service,name=k)
                    new.full_clean()
                    new.save()
                    print(f"Keyword : '{k}' 추가")
