from django.db import models
from core.models import TimeStampedModel
from django.conf import settings # s3를 이용한 이미지 업로드용
from datetime import datetime # s3를 이용한 이미지 업로드용

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100,blank=False)
    
class Style(models.Model):
    name = models.CharField(max_length=100,blank=False)

class Texture(models.Model):
    name = models.CharField(max_length=100,blank=False)
    
class Fit(models.Model):
    name = models.CharField(max_length=100,blank=False)
    
class Detail(models.Model):
    name = models.CharField(max_length=100,blank=False)
    
class Service(TimeStampedModel):
    name = models.CharField(max_length=100)
    #필터링 항목
    category = models.ForeignKey('Category', related_name='services',on_delete=models.CASCADE, null=True, blank=True)
    style = models.ManyToManyField('Style',related_name='services',blank=True)
    texture = models.ManyToManyField('Texture',related_name='services',blank=True)
    fit = models.ManyToManyField('Fit',related_name='services',blank=True)
    detail = models.ManyToManyField('Detail',related_name='services',blank=True)
    
    basic_price = models.CharField(max_length=500, blank = False)
    max_price = models.CharField(max_length=500, blank=True)
    info = models.TextField(blank = True)
    notice = models.TextField(blank = True)
    option = models.TextField(blank = True)
    period = models.CharField(max_length=100, blank = True)
    transaction_direct = models.BooleanField(default=False)
    transaction_package = models.BooleanField(default=False)
    refund = models.TextField(blank = True)
    reformer = models.ForeignKey('users.User', related_name='services', on_delete=models.SET_NULL, null=True, blank=False)
    
    likeuser_set = models.ManyToManyField("users.User", related_name='liked_services', blank=True)
    like_cnt = models.PositiveIntegerField(default=0)
    
    def like(self):
        self.like_cnt+=1
        
    def dislike(self):
        self.like_cnt-=1


class ServiceKeyword(models.Model):
    name = models.CharField(max_length=100)
    service = models.ForeignKey(
        'Service', related_name='keywords', on_delete=models.CASCADE, null=True, blank=True)
    

#Service_Photo 모델 만들기
# get_service_photo_upload_path 함수는 수정 가능성 있음
def get_service_photo_upload_path(instance, filename):
    return 'services/photo/{}'.format(filename)
# get_service_photo_upload_path 함수가 꼭 필요할까?

#class ServicePhoto(models.Model):
#    image = models.ImageField(
#        upload_to=get_service_photo_upload_path, default='service_photo.png')
#   service = models.ForeignKey(
#       'Service', related_name='service_photos', on_delete=models.CASCADE, null=True, blank=True)

class ServicePhoto(models.Model):
    image = models.URLField(default='service_photo.png')
    service = models.ForeignKey(
        'Service', related_name='service_photos', on_delete=models.CASCADE, null=True, blank=True)
