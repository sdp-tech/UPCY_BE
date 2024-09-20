from django.urls import path

from market.views.market_create_list_view import MarketCreateListView
from market.views.market_crud_view import MarketCrudView
from market.views.market_service_view import MarketServiceView

urlpatterns = [
    path("", MarketCreateListView.as_view(), name="market_create_list"),
    path("/<uuid:market_uuid>", MarketCrudView.as_view(), name="market_crud")
]
