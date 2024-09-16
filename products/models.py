from django.db import models

from core.models import TimeStampedModel

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
    
class Product(TimeStampedModel):
    name = models.CharField(max_length=100)
    #필터링 항목
    # category = models.ForeignKey('Category', related_name='products', on_delete=models.CASCADE, default=1)
    category = models.ForeignKey('Category', related_name='products',on_delete=models.CASCADE, null=True, blank=True)
    style = models.ManyToManyField('Style',related_name='products',blank=True)
    texture = models.ManyToManyField('Texture',related_name='products',blank=True)
    fit = models.ManyToManyField('Fit',related_name='products',blank=True)
    detail = models.ManyToManyField('Detail',related_name='products',blank=True)
    # option = models.ForeignKey('Option',related_name='products', on_delete=models.CASCADE, null=True, blank = True)
    
    basic_price = models.CharField(max_length=500, blank = False)
    info = models.TextField(blank = True)
    notice = models.TextField(blank = True)
    option = models.TextField(blank = True)
    period = models.CharField(max_length=100, blank = True)
    transaction_direct = models.BooleanField(default=False)
    transaction_package = models.BooleanField(default=False)
    refund = models.TextField(blank = True)
    reformer = models.ForeignKey('users.User', related_name='products', on_delete=models.SET_NULL, null=True, blank=False)
    
    likeuser_set = models.ManyToManyField("users.User", related_name='liked_products', blank=True)
    like_cnt = models.PositiveIntegerField(default=0)
    
    def like(self):
        self.like_cnt+=1
        
    def dislike(self):
        self.like_cnt-=1


class ProductKeyword(models.Model):
    name = models.CharField(max_length=100)
    product = models.ForeignKey(
        'Product', related_name='keywords', on_delete=models.CASCADE, null=True, blank=True)
    

#Product_Photo 모델 만들기
def get_product_photo_upload_path(instance, filename):
    return 'products/photo/{}'.format(filename)

class ProductPhoto(models.Model):
    image = models.ImageField(
        upload_to=get_product_photo_upload_path, default='product_photo.png')
    product = models.ForeignKey(
        'Product', related_name='product_photos', on_delete=models.CASCADE, null=True, blank=True)
