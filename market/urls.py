from django.urls import path

from market.views.market_crud_view import MarketCrudView
from market.views.market_service_view import MarketServiceView

urlpatterns = [
    path("", MarketCrudView.as_view(), name="market_crud"),
    path("/<uuid:market_uuid>", MarketServiceView.as_view(), name="service_view")
]
