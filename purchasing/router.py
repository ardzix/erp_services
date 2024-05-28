from rest_framework.routers import DefaultRouter
from .views import (SupplierViewSet, SupplierProductViewSet,
                    PurchaseOrderViewSet, InvalidPOItemViewSet)
from .views.account_payable import AccountsPayableViewSet
from .views.payable import PayableViewSet, PurchaseOrderPaymentViewSet

router = DefaultRouter()
router.register('purchase_order', PurchaseOrderViewSet,
                basename='purchase_order')
router.register('invalid_po_item', InvalidPOItemViewSet,
                basename='invalid_po_item')
router.register('supplier', SupplierViewSet, basename='supplier')
router.register('supplier_product', SupplierProductViewSet,
                basename='supplier_product')
router.register("accounts-payable", AccountsPayableViewSet,
                basename="accounts_payable")
router.register('purchase_order', PurchaseOrderViewSet,
                basename='purchase_order')
router.register('payable', PayableViewSet, basename='payable')
router.register('payment', PurchaseOrderPaymentViewSet, basename='payment')
