from django.contrib import admin

# Register your models here.
from . import models

@admin.register(models.Category)
class Category(admin.ModelAdmin):

    """ """

    pass

@admin.register(models.Fit)
class Fit(admin.ModelAdmin):

    """ """

    pass

@admin.register(models.Texture)
class Texture(admin.ModelAdmin):

    """ """

    pass

@admin.register(models.Style)
class Style(admin.ModelAdmin):

    """ """

    pass

@admin.register(models.Detail)
class Detail(admin.ModelAdmin):

    """ """

    pass

@admin.register(models.Service)
class Service(admin.ModelAdmin):

    """ """

    pass


@admin.register(models.ServicePhoto)
class Service_Photo(admin.ModelAdmin):

    """ """

    pass


@admin.register(models.ServiceKeyword)
class ServiceKeyword(admin.ModelAdmin):

    """ """

    pass
