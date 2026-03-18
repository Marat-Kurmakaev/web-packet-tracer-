from rest_framework import viewsets
from .models import Building, Room, DeviceType, Device, Port, Cable, Link
from .serializers import (
    BuildingSerializer,
    RoomSerializer,
    DeviceTypeSerializer,
    DeviceSerializer,
    PortSerializer,
    CableSerializer,
    LinkSerializer,
)


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all().order_by("id")
    serializer_class = BuildingSerializer


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.select_related("building").all().order_by("id")
    serializer_class = RoomSerializer


class DeviceTypeViewSet(viewsets.ModelViewSet):
    queryset = DeviceType.objects.all().order_by("id")
    serializer_class = DeviceTypeSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = (
        Device.objects.select_related("room", "room__building", "device_type")
        .prefetch_related("ports")
        .all()
        .order_by("id")
    )
    serializer_class = DeviceSerializer


class PortViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Port.objects.select_related("device", "device__device_type", "device__room").all().order_by("id")
    serializer_class = PortSerializer


class CableViewSet(viewsets.ModelViewSet):
    queryset = Cable.objects.all().order_by("id")
    serializer_class = CableSerializer


class LinkViewSet(viewsets.ModelViewSet):
    queryset = (
        Link.objects.select_related(
            "port_a",
            "port_a__device",
            "port_a__device__device_type",
            "port_b",
            "port_b__device",
            "port_b__device__device_type",
            "cable",
        )
        .all()
        .order_by("-created_at")
    )
    serializer_class = LinkSerializer