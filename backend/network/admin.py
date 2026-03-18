from django.contrib import admin
from .models import Building, Room, DeviceType, Device, Port, Cable, Link


class RoomInline(admin.TabularInline):
    model = Room
    extra = 0


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    inlines = [RoomInline]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "building", "x", "y", "width", "height")
    list_filter = ("building",)
    search_fields = ("name", "building__name")
    autocomplete_fields = ("building",)


@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "kind", "ports_count", "base_price", "width", "height")
    list_filter = ("kind",)
    search_fields = ("name",)


class PortInline(admin.TabularInline):
    model = Port
    extra = 0


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "device_type", "room", "x", "y", "price_override")
    list_filter = ("device_type__kind", "room__building")
    search_fields = ("name", "room__name", "room__building__name", "device_type__name")
    autocomplete_fields = ("room", "device_type")
    inlines = [PortInline]


@admin.register(Port)
class PortAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "index", "device", "is_active")
    list_filter = ("is_active", "device__device_type__kind")
    search_fields = ("name", "device__name")
    autocomplete_fields = ("device",)


@admin.register(Cable)
class CableAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "length_m", "price")
    search_fields = ("name",)


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ("id", "port_a", "port_b", "cable", "created_at")
    list_filter = ("cable", "created_at")
    autocomplete_fields = ("port_a", "port_b", "cable")