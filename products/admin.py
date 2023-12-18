from django.contrib import admin
from . import models


@admin.register(models.Category)
class Category(admin.ModelAdmin):

    """ """

    pass


@admin.register(models.Product)
class Product(admin.ModelAdmin):

    """ """

    pass


@admin.register(models.ProductPhoto)
class Product_Photo(admin.ModelAdmin):

    """ """

    pass


@admin.register(models.ProductKeyword)
class ProductKeyword(admin.ModelAdmin):

    """ """

    pass
