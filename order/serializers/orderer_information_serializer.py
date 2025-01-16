from rest_framework import serializers

from order.models import OrdererInformation


class OrdererInformationSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrdererInformation
        fields = [
            "orderer_name",
            "orderer_phone_number",
            "orderer_email",
            "orderer_address",
        ]
