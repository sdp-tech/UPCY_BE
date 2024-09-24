from django.urls import path

from market.views.market_view.market_create_list_view import MarketCreateListView
from market.views.market_view.market_crud_view import MarketCrudView
from market.views.service_view.service_create_retrieve_view import MarketServiceView
from market.views.service_view.service_detail_view import MarketServiceCrudView
from market.views.image_upload_view import MarketImageUploadView, MarketServiceImageUploadView
from market.views.service_view.service_material.service_material_view import ServiceMaterialCreateListView, ServiceMaterialView
from market.views.service_view.service_option.service_option_view import ServiceOptionCreateListView, ServiceOptionView

urlpatterns = [
    path("", MarketCreateListView.as_view(), name="market_create_list"),
    path("/<uuid:market_uuid>", MarketCrudView.as_view(), name="market_crud"),
    path("/<uuid:market_uuid>/image", MarketImageUploadView.as_view(), name="market_image_upload"),
    path("/<uuid:market_uuid>/service", MarketServiceView.as_view(), name="market_service"),
    path("/<uuid:market_uuid>/service/<uuid:service_uuid>", MarketServiceCrudView.as_view(), name="market_service_crud"),
    path("/<uuid:market_uuid>/service/<uuid:service_uuid>/image", MarketServiceImageUploadView.as_view(), name="market_service_image_upload"),
    path("/<uuid:market_uuid>/service/<uuid:service_uuid>/material", ServiceMaterialCreateListView.as_view(), name="service_material_create_list_view"),
    path("/<uuid:market_uuid>/service/<uuid:service_uuid>/material/<uuid:material_uuid>", ServiceMaterialView.as_view(), name="service_material_view"),
    path("/<uuid:market_uuid>/service/<uuid:service_uuid>/option", ServiceOptionCreateListView.as_view(), name="service_option_create_list_view"),
    path("/<uuid:market_uuid>/service/<uuid:service_uuid>/option/<uuid:option_uuid>", ServiceOptionView.as_view(), name="service_option_view"),
    # path("/<uuid:market_uuid>/service/<uuid:service_uuid>/option/<uuid:option_uuid>/image", MarketServiceOptionImageUploadView.as_view(), name="market_service_option_image_upload"),
]
