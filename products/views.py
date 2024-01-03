from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import serializers, status
from rest_framework.response import Response

from users.models import User

from .models import Category, Product
from .services import ProductCoordinatorService, ProductPhotoService, ProductKeywordService, ProductService


class ProductCreateApi(APIView):
    permission_classes=(AllowAny,)
    
    class ProductCreateInputSerializer(serializers.Serializer):
        name = serializers.CharField()
        category = serializers.CharField()
        keywords = serializers.ListField()
        basic_price = serializers.CharField()
        option = serializers.CharField()
        product_photos = serializers.ListField()
        info = serializers.CharField()
        notice = serializers.CharField()
        period = serializers.CharField()
        transaction_direct = serializers.BooleanField()
        transaction_package = serializers.BooleanField()
        refund = serializers.CharField()
        reformer = serializers.EmailField()
    
    def post(self,request):
        serializers = self.ProductCreateInputSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data = serializers.validated_data
    
        reformer_email=data.get('reformer')
        reformer, created = User.objects.get_or_create(email=reformer_email)
        category_name=data.get('category')
        category, created = Category.objects.get_or_create(name=category_name)
        
        product=ProductService.create(
            name=data.get('name'),
            category=category,
            #keywords=data.get('keywords',[]),
            basic_price=data.get('basic_price'),
            option=data.get('option'),
            #product_photos=data.get('product_photos',[]),
            info=data.get('info'),
            notice=data.get('notice'),
            period=data.get('period'),
            transaction_direct=data.get('transaction_direct'),
            transaction_package=data.get('transaction_package'),
            refund=data.get('refund'),
            reformer=reformer,
        )
        
        return Response({
            'status': 'success',
            'data' : {'id': product.id},
        }, status=status.HTTP_201_CREATED)