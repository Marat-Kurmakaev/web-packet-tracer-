from rest_framework import viewsets

from .models import Computer, Switch, Router, Cable, TopologyDevice, Port, Link
from .serializers import (
    ComputerSerializer,
    SwitchSerializer,
    RouterSerializer,
    CableSerializer,
    TopologyDeviceSerializer,
    PortSerializer,
    LinkSerializer,
)


class ComputerViewSet(viewsets.ModelViewSet):
    queryset = Computer.objects.all().order_by("id")
    serializer_class = ComputerSerializer


class SwitchViewSet(viewsets.ModelViewSet):
    queryset = Switch.objects.all().order_by("id")
    serializer_class = SwitchSerializer


class RouterViewSet(viewsets.ModelViewSet):
    queryset = Router.objects.all().order_by("id")
    serializer_class = RouterSerializer


class CableViewSet(viewsets.ModelViewSet):
    queryset = Cable.objects.all().order_by("id")
    serializer_class = CableSerializer


class TopologyDeviceViewSet(viewsets.ModelViewSet):
    queryset = (
        TopologyDevice.objects.select_related("computer", "switch", "router")
        .prefetch_related("ports")
        .all()
        .order_by("id")
    )
    serializer_class = TopologyDeviceSerializer


class PortViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Port.objects.select_related(
            "device",
            "device__computer",
            "device__switch",
            "device__router",
        )
        .all()
        .order_by("id")
    )
    serializer_class = PortSerializer


class LinkViewSet(viewsets.ModelViewSet):
    queryset = (
        Link.objects.select_related(
            "port_a",
            "port_a__device",
            "port_a__device__computer",
            "port_a__device__switch",
            "port_a__device__router",
            "port_b",
            "port_b__device",
            "port_b__device__computer",
            "port_b__device__switch",
            "port_b__device__router",
            "cable",
        )
        .all()
        .order_by("-created_at")
    )
    serializer_class = LinkSerializer