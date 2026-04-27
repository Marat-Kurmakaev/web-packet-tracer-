from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ComputerViewSet,
    SwitchViewSet,
    RouterViewSet,
    CableViewSet,
    TopologyDeviceViewSet,
    PortViewSet,
    LinkViewSet,
)


catalog_router = DefaultRouter()
catalog_router.register(r"computers", ComputerViewSet, basename="computer")
catalog_router.register(r"switches", SwitchViewSet, basename="switch")
catalog_router.register(r"routers", RouterViewSet, basename="router")
catalog_router.register(r"cables", CableViewSet, basename="cable")

topology_router = DefaultRouter()
topology_router.register(r"devices", TopologyDeviceViewSet, basename="device")
topology_router.register(r"ports", PortViewSet, basename="port")
topology_router.register(r"links", LinkViewSet, basename="link")


urlpatterns = [
    path("catalog/", include(catalog_router.urls)),
    path("topology/", include(topology_router.urls)),
]