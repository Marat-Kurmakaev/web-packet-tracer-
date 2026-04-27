from django.contrib import admin
from django.utils.html import format_html

from .models import Computer, Switch, Router, Cable, TopologyDevice, Port, Link


class CatalogItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "max_connected_devices",
        "image_preview",
    )
    search_fields = ("name", "description")
    list_filter = ("price",)
    readonly_fields = ("image_preview",)
    fields = (
        "name",
        "image",
        "image_preview",
        "description",
        "price",
        "max_connected_devices",
    )

    @admin.display(description="Картинка")
    def image_preview(self, obj):
        if not obj.image:
            return "—"

        return format_html(
            '<img src="{}" style="max-height: 80px; max-width: 120px; object-fit: contain;" />',
            obj.image.url,
        )


@admin.register(Computer)
class ComputerAdmin(CatalogItemAdmin):
    pass


@admin.register(Switch)
class SwitchAdmin(CatalogItemAdmin):
    pass


@admin.register(Router)
class RouterAdmin(CatalogItemAdmin):
    pass


@admin.register(Cable)
class CableAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "image_preview")
    search_fields = ("name", "description")
    list_filter = ("price",)
    readonly_fields = ("image_preview",)
    fields = ("name", "image", "image_preview", "description", "price")

    @admin.display(description="Картинка")
    def image_preview(self, obj):
        if not obj.image:
            return "—"

        return format_html(
            '<img src="{}" style="max-height: 80px; max-width: 120px; object-fit: contain;" />',
            obj.image.url,
        )


class PortInline(admin.TabularInline):
    model = Port
    extra = 0
    can_delete = False
    fields = ("id", "name", "index", "is_active")
    readonly_fields = ("id", "name", "index")

    def has_add_permission(self, request, obj=None):
        return False


class TopologyDeviceTypeFilter(admin.SimpleListFilter):
    title = "тип устройства"
    parameter_name = "device_type"

    def lookups(self, request, model_admin):
        return (
            ("computer", "Компьютер"),
            ("switch", "Коммутатор"),
            ("router", "Роутер"),
        )

    def queryset(self, request, queryset):
        if self.value() == "computer":
            return queryset.filter(computer__isnull=False)
        if self.value() == "switch":
            return queryset.filter(switch__isnull=False)
        if self.value() == "router":
            return queryset.filter(router__isnull=False)
        return queryset


@admin.register(TopologyDevice)
class TopologyDeviceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "catalog_type",
        "catalog_item_name",
        "ports_count",
    )
    list_filter = (TopologyDeviceTypeFilter,)
    search_fields = (
        "name",
        "computer__name",
        "switch__name",
        "router__name",
    )
    autocomplete_fields = ("computer", "switch", "router")
    inlines = [PortInline]
    fields = ("name", "computer", "switch", "router")

    @admin.display(description="Тип")
    def catalog_type(self, obj):
        if obj.computer_id:
            return "Компьютер"
        if obj.switch_id:
            return "Коммутатор"
        if obj.router_id:
            return "Роутер"
        return "—"

    @admin.display(description="Модель")
    def catalog_item_name(self, obj):
        catalog_item = obj.catalog_item
        if catalog_item is None:
            return "—"
        return catalog_item.name

    @admin.display(description="Портов")
    def ports_count(self, obj):
        return obj.ports.count()


@admin.register(Port)
class PortAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "index", "device", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "device__name")
    autocomplete_fields = ("device",)
    readonly_fields = ("name", "index", "device")

    def has_add_permission(self, request):
        return False


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "device_a_name",
        "port_a",
        "device_b_name",
        "port_b",
        "cable",
        "created_at",
    )
    list_filter = ("cable", "created_at")
    search_fields = (
        "port_a__name",
        "port_a__device__name",
        "port_b__name",
        "port_b__device__name",
        "cable__name",
    )
    autocomplete_fields = ("port_a", "port_b", "cable")
    readonly_fields = ("created_at",)

    @admin.display(description="Устройство A")
    def device_a_name(self, obj):
        return obj.port_a.device.name

    @admin.display(description="Устройство B")
    def device_b_name(self, obj):
        return obj.port_b.device.name
