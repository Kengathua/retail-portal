"""Mpesa adapter serializers file."""

from rest_framework import serializers

from elites_retail_portal.transactions import models


class MpesaCheckoutSerializer(serializers.ModelSerializer):
    """Serializer class for Mpesa Checkout."""

    class Meta:
        """."""

        model = models.PaymentRequest
        fields = '__all__'
