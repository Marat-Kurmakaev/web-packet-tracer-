from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Building, Room, DeviceType, Device, Port, Link, Cable, DeviceKind


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


class DeviceApiTests(BaseAPITestCase):
    def test_create_device(self):
        url = reverse("device-list")
        data = {
            "name": "PC-1",
            "room": self.room.id,
            "device_type": self.pc_type.id,
            "x": 10,
            "y": 10,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Device.objects.count(), 1)
        self.assertEqual(Device.objects.first().name, "PC-1")

    def test_device_cannot_be_outside_room(self):
        url = reverse("device-list")
        data = {
            "name": "PC-out",
            "room": self.room.id,
            "device_type": self.pc_type.id,
            "x": 95,
            "y": 95,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Device.objects.count(), 0)

    def test_devices_cannot_overlap(self):
        Device.objects.create(
            name="PC-1",
            room=self.room,
            device_type=self.pc_type,
            x=10,
            y=10,
        )

        url = reverse("device-list")
        data = {
            "name": "PC-2",
            "room": self.room.id,
            "device_type": self.pc_type.id,
            "x": 15,
            "y": 15,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Device.objects.count(), 1)

    def test_ports_are_created_automatically_for_device(self):
        url = reverse("device-list")
        data = {
            "name": "SW-1",
            "room": self.room.id,
            "device_type": self.switch_type.id,
            "x": 10,
            "y": 10,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        device = Device.objects.get(name="SW-1")
        self.assertEqual(device.ports.count(), self.switch_type.ports_count)