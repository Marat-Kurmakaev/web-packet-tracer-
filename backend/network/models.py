from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, F


class DeviceKind(models.TextChoices):
    SWITCH = "SWITCH", "Коммутатор"
    PC = "PC", "ПК"
    ROUTER = "ROUTER", "Роутер"


class Building(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name="rooms",
    )
    name = models.CharField(max_length=255)
    x = models.PositiveIntegerField()
    y = models.PositiveIntegerField()
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["building", "name"], name="unique_room_name_in_building"),
            models.CheckConstraint(check=Q(width__gt=0), name="room_width_gt_0"),
            models.CheckConstraint(check=Q(height__gt=0), name="room_height_gt_0"),
        ]

    def __str__(self):
        return f"{self.building.name} / {self.name}"


class DeviceType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    kind = models.CharField(max_length=16, choices=DeviceKind.choices)
    ports_count = models.PositiveIntegerField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    width = models.PositiveIntegerField(default=1)
    height = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(ports_count__gte=1), name="device_type_ports_gte_1"),
            models.CheckConstraint(check=Q(width__gt=0), name="device_type_width_gt_0"),
            models.CheckConstraint(check=Q(height__gt=0), name="device_type_height_gt_0"),
        ]

    def __str__(self):
        return self.name


class Device(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="devices")
    device_type = models.ForeignKey(DeviceType, on_delete=models.PROTECT, related_name="devices")
    name = models.CharField(max_length=255)
    x = models.PositiveIntegerField()
    y = models.PositiveIntegerField()
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["room", "name"], name="unique_device_name_in_room"),
        ]

    def __str__(self):
        return self.name

    @property
    def width(self):
        return self.device_type.width

    @property
    def height(self):
        return self.device_type.height

    @property
    def left(self):
        return self.x

    @property
    def top(self):
        return self.y

    @property
    def right(self):
        return self.x + self.width

    @property
    def bottom(self):
        return self.y + self.height

    def clean(self):
        room_left = self.room.x
        room_top = self.room.y
        room_right = self.room.x + self.room.width
        room_bottom = self.room.y + self.room.height

        if self.left < room_left or self.top < room_top or self.right > room_right or self.bottom > room_bottom:
            raise ValidationError("Устройство выходит за границы комнаты или попадает в стену.")

        overlaps = Device.objects.filter(room=self.room).exclude(pk=self.pk).select_related("device_type")
        for other in overlaps:
            separated = (
                self.right <= other.left or
                self.left >= other.right or
                self.bottom <= other.top or
                self.top >= other.bottom
            )
            if not separated:
                raise ValidationError(f"Устройство пересекается с '{other.name}'.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Port(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="ports")
    name = models.CharField(max_length=64)
    index = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["device", "index"], name="unique_port_index_per_device"),
            models.UniqueConstraint(fields=["device", "name"], name="unique_port_name_per_device"),
        ]
        ordering = ["device_id", "index"]

    def __str__(self):
        return f"{self.device.name}:{self.name}"


class Cable(models.Model):
    name = models.CharField(max_length=255)
    length_m = models.DecimalField(max_digits=8, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(length_m__gt=0), name="cable_length_gt_0"),
            models.CheckConstraint(check=Q(price__gte=0), name="cable_price_gte_0"),
        ]

    def __str__(self):
        return self.name


class Link(models.Model):
    port_a = models.OneToOneField(Port, on_delete=models.PROTECT, related_name="link_as_a")
    port_b = models.OneToOneField(Port, on_delete=models.PROTECT, related_name="link_as_b")
    cable = models.ForeignKey(Cable, on_delete=models.SET_NULL, null=True, blank=True, related_name="links")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=~Q(port_a=F("port_b")), name="link_ports_must_differ"),
        ]

    def clean(self):
        if self.port_a.device_id == self.port_b.device_id:
            raise ValidationError("Нельзя соединять устройство само с собой.")

        kind_a = self.port_a.device.device_type.kind
        kind_b = self.port_b.device.device_type.kind

        if kind_a == DeviceKind.PC and kind_b == DeviceKind.PC:
            raise ValidationError("Соединение PC ↔ PC запрещено.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)