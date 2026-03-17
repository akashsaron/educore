from rest_framework import serializers
from .models import FeeCategory, FeeStructure, FeeInvoice, FeePayment, Scholarship


class FeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = FeeCategory
        fields = '__all__'


class FeeStructureSerializer(serializers.ModelSerializer):
    grade_name    = serializers.CharField(source='grade.name',         read_only=True)
    category_name = serializers.CharField(source='category.name',      read_only=True)
    year_name     = serializers.CharField(source='academic_year.name', read_only=True)

    class Meta:
        model  = FeeStructure
        fields = '__all__'


class FeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FeePayment
        fields = '__all__'


class FeeInvoiceSerializer(serializers.ModelSerializer):
    student_name  = serializers.CharField(source='student.full_name',             read_only=True)
    section_name  = serializers.CharField(source='student.section.display_name',  read_only=True)
    category_name = serializers.CharField(source='fee_structure.category.name',   read_only=True)
    balance_due   = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    payments      = FeePaymentSerializer(many=True, read_only=True)

    class Meta:
        model  = FeeInvoice
        fields = '__all__'


class ScholarshipSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model  = Scholarship
        fields = '__all__'
