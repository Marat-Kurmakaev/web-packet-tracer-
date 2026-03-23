from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BuildingViewSet,
    RoomViewSet,
    DeviceTypeViewSet,
    DeviceViewSet,
    PortViewSet,
    CableViewSet,
    LinkViewSet,
)

catalog_router = DefaultRouter()
catalog_router.register(r"buildings", BuildingViewSet, basename="building")
catalog_router.register(r"rooms", RoomViewSet, basename="room")
catalog_router.register(r"device-types", DeviceTypeViewSet, basename="device-type")
catalog_router.register(r"cables", CableViewSet, basename="cable")

topology_router = DefaultRouter()
topology_router.register(r"devices", DeviceViewSet, basename="device")
topology_router.register(r"ports", PortViewSet, basename="port")
topology_router.register(r"links", LinkViewSet, basename="link")

urlpatterns = [
    path("catalog/", include(catalog_router.urls)),
    path("topology/", include(topology_router.urls)),
]
