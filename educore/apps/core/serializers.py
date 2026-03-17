from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, AcademicYear, SchoolProfile, Grade, Section


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['role']     = user.role
        token['name']     = user.get_full_name()
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id':       self.user.id,
            'username': self.user.username,
            'name':     self.user.get_full_name(),
            'role':     self.user.role,
            'email':    self.user.email,
        }
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id','username','first_name','last_name','email','role','phone','avatar','is_active']
        read_only_fields = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ['username','first_name','last_name','email','role','phone','password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model  = AcademicYear
        fields = '__all__'


class SchoolProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SchoolProfile
        fields = '__all__'


class GradeSerializer(serializers.ModelSerializer):
    sections_count = serializers.SerializerMethodField()

    class Meta:
        model  = Grade
        fields = '__all__'

    def get_sections_count(self, obj):
        return obj.sections.count()


class SectionSerializer(serializers.ModelSerializer):
    grade_name    = serializers.CharField(source='grade.name', read_only=True)
    display_name  = serializers.CharField(read_only=True)
    student_count = serializers.SerializerMethodField()

    class Meta:
        model  = Section
        fields = '__all__'

    def get_student_count(self, obj):
        return obj.students.filter(is_active=True).count()
