from django.db import models
from core.models import TimeStampedModel
# Create your models here.

class Product(TimeStampedModel):
    name = models.CharField(max_length=100)
    #category = models.ForeignKey('Category', related_name='products', on_delete=models.CASCADE, null=False, blank=False)
    basic_price = models.CharField(max_length=500, blank = False)
    option = models.TextField(blank = True)
    info = models.TextField(blank = True)
    notice = models.TextField(blank = True)
    period = models.CharField(max_length=100, blank = True)
    transaction_direct = models.BooleanField(default=False)
    transaction_package = models.BooleanField(default=False)
    refund = models.TextField(blank = True)
    reformer = models.ForeignKey('users.User', related_name='products', on_delete=models.SET_NULL, null=True, blank=False)



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
