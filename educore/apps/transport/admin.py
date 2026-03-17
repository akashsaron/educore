from django.contrib import admin
from .models import Vehicle, Driver, Route, RouteStop, StudentRoute

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['registration_no', 'vehicle_type', 'capacity', 'status']
    list_filter  = ['status']

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'license_no', 'license_expiry', 'is_active']

class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 0
    ordering = ['order']

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'vehicle', 'driver', 'morning_start', 'is_active']
    list_filter  = ['is_active']
    inlines      = [RouteStopInline]

@admin.register(StudentRoute)
class StudentRouteAdmin(admin.ModelAdmin):
    list_display  = ['student', 'route', 'stop', 'is_active']
    list_filter   = ['route', 'is_active']
    search_fields = ['student__first_name', 'student__last_name']
