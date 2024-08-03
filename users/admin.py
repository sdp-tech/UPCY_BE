from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.User)
class CustomUserAdmin(admin.ModelAdmin):
    pass

@admin.register(models.PortfolioPhoto)
class PortfolioPhoto(admin.ModelAdmin):
    pass

@admin.register(models.Style)
class Style(admin.ModelAdmin):
    pass

@admin.register(models.Material)
class Material(admin.ModelAdmin):
    pass

@admin.register(models.ReformerProfile)
class ReformerProfile(admin.ModelAdmin):
    pass

@admin.register(models.Certification)
class Certification(admin.ModelAdmin):
    pass

@admin.register(models.Competition)
class Competition(admin.ModelAdmin):
    pass

@admin.register(models.Internship)
class Intership(admin.ModelAdmin):
    pass

@admin.register(models.Freelancer)
class Freelancer(admin.ModelAdmin):
    pass

@admin.register(models.UserProfile)
class UserProfile(admin.ModelAdmin):
    pass