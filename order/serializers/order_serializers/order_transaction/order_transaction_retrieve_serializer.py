from rest_framework import serializers
from order.models import TransactionOption

class TransactionOptionRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionOption
        fields = ['transaction_option',
                  'delivery_address',
                  'delivery_name',
                  'delivery_phone_number']

