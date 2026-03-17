from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Vehicle, Driver, Route, RouteStop, StudentRoute


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Vehicle
        fields = '__all__'


class DriverSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model  = Driver
        fields = '__all__'


class RouteStopSerializer(serializers.ModelSerializer):
    class Meta:
        model  = RouteStop
        fields = '__all__'


class RouteSerializer(serializers.ModelSerializer):
    vehicle_no   = serializers.CharField(source='vehicle.registration_no', read_only=True)
    driver_name  = serializers.CharField(source='driver.user.get_full_name', read_only=True)
    student_count= serializers.IntegerField(read_only=True)
    stops        = RouteStopSerializer(many=True, read_only=True)

    class Meta:
        model  = Route
        fields = '__all__'


class StudentRouteSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    route_name   = serializers.CharField(source='route.name',        read_only=True)
    stop_name    = serializers.CharField(source='stop.stop_name',    read_only=True)

    class Meta:
        model  = StudentRoute
        fields = '__all__'


class VehicleViewSet(viewsets.ModelViewSet):
    queryset           = Vehicle.objects.all()
    serializer_class   = VehicleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['status']


class DriverViewSet(viewsets.ModelViewSet):
    queryset           = Driver.objects.select_related('user').all()
    serializer_class   = DriverSerializer
    permission_classes = [IsAuthenticated]


class RouteViewSet(viewsets.ModelViewSet):
    queryset           = Route.objects.select_related('vehicle', 'driver__user').prefetch_related('stops').all()
    serializer_class   = RouteSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['is_active']
    search_fields      = ['name', 'code']


class RouteStopViewSet(viewsets.ModelViewSet):
    queryset           = RouteStop.objects.select_related('route').all()
    serializer_class   = RouteStopSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['route']


class StudentRouteViewSet(viewsets.ModelViewSet):
    queryset           = StudentRoute.objects.select_related('student', 'route', 'stop').all()
    serializer_class   = StudentRouteSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['route', 'is_active']
    search_fields      = ['student__first_name', 'student__last_name']
