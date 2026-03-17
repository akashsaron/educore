from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (FeeCategoryViewSet, FeeStructureViewSet,
                    FeeInvoiceViewSet, FeePaymentViewSet, ScholarshipViewSet)

router = DefaultRouter()
router.register('categories',  FeeCategoryViewSet)
router.register('structures',  FeeStructureViewSet)
router.register('invoices',    FeeInvoiceViewSet)
router.register('payments',    FeePaymentViewSet)
router.register('scholarships',ScholarshipViewSet)

urlpatterns = [path('', include(router.urls))]
