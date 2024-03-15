from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from ..models import OrderItem
from ..serializers.sales import SalesReportSerializer

class SalesReportAPIView(APIView):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    # DjangoModelPermissions requires a queryset attribute to determine the model it applies to.
    # Since this view might not directly operate on a single model or you want to apply it
    # to OrderItem model permissions, explicitly state the queryset as follows:
    queryset = OrderItem.objects.all()

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        product_id32 = request.query_params.get('product_id32')
        customer_id32 = request.query_params.get('customer_id32')

        queryset = self.queryset

        if start_date and end_date:
            queryset = queryset.filter(order__order_date__range=[start_date, end_date])

        if product_id32:
            queryset = queryset.filter(product__id32=product_id32)

        if customer_id32:
            queryset = queryset.filter(order__customer__id32=customer_id32)


        if queryset.exists():
            aggregated_data = queryset.aggregate(
                total_sales=Sum('price'),
                total_quantity=Sum('quantity')
            )
        else:
            aggregated_data = {
                'total_sales':0,
                'total_quantity':0
            }

        # Use the serializer to format the response data
        serializer = SalesReportSerializer(data=aggregated_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
