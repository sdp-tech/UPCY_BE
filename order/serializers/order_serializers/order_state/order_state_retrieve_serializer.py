from rest_framework import serializers
from order.models import OrderState

class OrderStateRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderState
        field = ['reformer_status']