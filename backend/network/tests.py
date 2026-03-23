from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Building, Room, DeviceType, Device, Link, Cable, DeviceKind


class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.building = Building.objects.create(name="Campus A")
        self.room = Room.objects.create(
            building=self.building,
            name="101",
            x=0,
            y=0,
            width=100,
            height=100,
        )

        self.pc_type = DeviceType.objects.create(
            name="PC type",
            kind=DeviceKind.PC,
            ports_count=1,
            base_price=1000,
            width=10,
            height=10,
        )
        self.switch_type = DeviceType.objects.create(
            name="Switch type",
            kind=DeviceKind.SWITCH,
            ports_count=8,
            base_price=5000,
            width=20,
            height=10,
        )
        self.router_type = DeviceType.objects.create(
            name="Router type",
            kind=DeviceKind.ROUTER,
            ports_count=4,
            base_price=7000,
            width=15,
            height=10,
        )
        self.cable = Cable.objects.create(
            name="UTP Cat 5e",
            length_m=5,
            price=250,
        )

    def create_device(self, *, name, device_type, x, y, room=None):
        return Device.objects.create(
            name=name,
            room=room or self.room,
            device_type=device_type,
            x=x,
            y=y,
        )


class CatalogApiTests(BaseAPITestCase):
    def test_catalog_and_port_endpoints_are_read_only(self):
        cases = [
            ("building-list", {"name": "Campus B"}),
            (
                "room-list",
                {
                    "building": self.building.id,
                    "name": "102",
                    "x": 0,
                    "y": 0,
                    "width": 50,
                    "height": 50,
                },
            ),
            (
                "device-type-list",
                {
                    "name": "Server type",
                    "kind": DeviceKind.ROUTER,
                    "ports_count": 2,
                    "base_price": "12000.00",
                    "width": 20,
                    "height": 10,
                },
            ),
            ("cable-list", {"name": "Fiber", "length_m": "10.00", "price": "999.00"}),
            ("port-list", {"device": 1, "name": "eth99", "index": 99, "is_active": True}),
        ]

        for route_name, payload in cases:
            with self.subTest(route_name=route_name):
                list_response = self.client.get(reverse(route_name), format="json")
                self.assertEqual(list_response.status_code, status.HTTP_200_OK)

                create_response = self.client.post(reverse(route_name), payload, format="json")
                self.assertEqual(create_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class DeviceApiTests(BaseAPITestCase):
    def test_create_device_returns_201_and_creates_ports(self):
        response = self.client.post(
            reverse("device-list"),
            {
                "name": "SW-1",
                "room": self.room.id,
                "device_type": self.switch_type.id,
                "x": 10,
                "y": 10,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        device = Device.objects.get(name="SW-1")
        self.assertEqual(device.ports.count(), self.switch_type.ports_count)
        self.assertEqual(response.data["width"], self.switch_type.width)
        self.assertEqual(response.data["height"], self.switch_type.height)

    def test_device_cannot_be_outside_room(self):
        response = self.client.post(
            reverse("device-list"),
            {
                "name": "PC-out",
                "room": self.room.id,
                "device_type": self.pc_type.id,
                "x": 95,
                "y": 95,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Device.objects.count(), 0)

    def test_devices_cannot_overlap(self):
        self.create_device(name="PC-1", device_type=self.pc_type, x=10, y=10)

        response = self.client.post(
            reverse("device-list"),
            {
                "name": "PC-2",
                "room": self.room.id,
                "device_type": self.pc_type.id,
                "x": 15,
                "y": 15,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Device.objects.count(), 1)

    def test_deleting_device_removes_related_links(self):
        pc = self.create_device(name="PC-1", device_type=self.pc_type, x=10, y=10)
        switch = self.create_device(name="SW-1", device_type=self.switch_type, x=40, y=10)

        link = Link.objects.create(
            port_a=pc.ports.get(index=1),
            port_b=switch.ports.get(index=1),
            cable=self.cable,
        )

        response = self.client.delete(reverse("device-detail", args=[pc.id]), format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Device.objects.filter(pk=pc.id).exists())
        self.assertFalse(Link.objects.filter(pk=link.id).exists())


class LinkApiTests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.pc = self.create_device(name="PC-1", device_type=self.pc_type, x=10, y=10)
        self.switch = self.create_device(name="SW-1", device_type=self.switch_type, x=40, y=10)
        self.router = self.create_device(name="RTR-1", device_type=self.router_type, x=10, y=40)
        self.pc_2 = self.create_device(name="PC-2", device_type=self.pc_type, x=40, y=40)

    def test_create_link(self):
        response = self.client.post(
            reverse("link-list"),
            {
                "port_a": self.pc.ports.get(index=1).id,
                "port_b": self.switch.ports.get(index=1).id,
                "cable": self.cable.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Link.objects.count(), 1)

    def test_cannot_link_same_port(self):
        port = self.switch.ports.get(index=1)

        response = self.client.post(
            reverse("link-list"),
            {
                "port_a": port.id,
                "port_b": port.id,
                "cable": self.cable.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Link.objects.count(), 0)

    def test_cannot_link_ports_of_same_device(self):
        response = self.client.post(
            reverse("link-list"),
            {
                "port_a": self.switch.ports.get(index=1).id,
                "port_b": self.switch.ports.get(index=2).id,
                "cable": self.cable.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Link.objects.count(), 0)

    def test_cannot_link_pc_to_pc(self):
        response = self.client.post(
            reverse("link-list"),
            {
                "port_a": self.pc.ports.get(index=1).id,
                "port_b": self.pc_2.ports.get(index=1).id,
                "cable": self.cable.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Link.objects.count(), 0)

    def test_cannot_reuse_busy_port(self):
        occupied_port = self.switch.ports.get(index=1)
        Link.objects.create(
            port_a=self.pc.ports.get(index=1),
            port_b=occupied_port,
            cable=self.cable,
        )

        response = self.client.post(
            reverse("link-list"),
            {
                "port_a": occupied_port.id,
                "port_b": self.router.ports.get(index=1).id,
                "cable": self.cable.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("port_a", response.data)
        self.assertEqual(Link.objects.count(), 1)