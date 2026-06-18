from django.shortcuts import render
from rest_framework import views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Order
# Create your views here.
class PharmacyReceiptVerification(views.APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, order_id):
        try:
            order=Order.objects.get(
                id=order_id,
                pharmacy=request.user.pharmacy_profile,
                status='reviewing'
            )
        except Order.DoesNotExist:
            return Response({"error": "order not found"}, status=status.HTTP_404_NOT_FOUND)
        decision=request.data.get('decision')
        if decision=='approve':
            order.status='approved_assembling'
            order.save()
            return Response({"message":"receipt approved, assembling"})
        elif decision=='reject':
            order.status='rejected'
            order.save()
            return Response({"message":"receipt rejected"})
        else: 
            return Response({"error": "invalid decision"}, status=status.HTTP_400_BAD_REQUEST)
        