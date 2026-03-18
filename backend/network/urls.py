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

router = DefaultRouter()
router.register(r"buildings", BuildingViewSet, basename="building")
router.register(r"rooms", RoomViewSet, basename="room")
router.register(r"device-types", DeviceTypeViewSet, basename="device-type")
router.register(r"devices", DeviceViewSet, basename="device")
router.register(r"ports", PortViewSet, basename="port")
router.register(r"cables", CableViewSet, basename="cable")
router.register(r"links", LinkViewSet, basename="link")

urlpatterns = router.urls