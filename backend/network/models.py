from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F, Q


class DeviceCatalogItem(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to="devices/", null=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_connected_devices = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(check=Q(price__gte=0), name="%(app_label)s_%(class)s_price_gte_0"),
            models.CheckConstraint(
                check=Q(max_connected_devices__isnull=True) | Q(max_connected_devices__gte=1),
                name="%(app_label)s_%(class)s_max_connected_devices_gte_1",
            ),
        ]
        ordering = ["id"]

    def __str__(self):
        return self.name


class Computer(DeviceCatalogItem):
    class Meta(DeviceCatalogItem.Meta):
        verbose_name = "computer"
        verbose_name_plural = "computers"


class Switch(DeviceCatalogItem):
    class Meta(DeviceCatalogItem.Meta):
        verbose_name = "switch"
        verbose_name_plural = "switches"


class Router(DeviceCatalogItem):
    class Meta(DeviceCatalogItem.Meta):
        verbose_name = "router"
        verbose_name_plural = "routers"


class Cable(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to="cables/", null=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(price__gte=0), name="cable_price_gte_0"),
        ]
        ordering = ["id"]

    def __str__(self):
        return self.name


class TopologyDevice(models.Model):
    name = models.CharField(max_length=255, unique=True)
    computer = models.ForeignKey(
        Computer,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="topology_devices",
    )
    switch = models.ForeignKey(
        Switch,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="topology_devices",
    )
    router = models.ForeignKey(
        Router,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="topology_devices",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(computer__isnull=False, switch__isnull=True, router__isnull=True)
                    | Q(computer__isnull=True, switch__isnull=False, router__isnull=True)
                    | Q(computer__isnull=True, switch__isnull=True, router__isnull=False)
                ),
                name="topology_device_exactly_one_catalog_item",
            ),
        ]
        ordering = ["id"]

    def __str__(self):
        return self.name

    @property
    def catalog_item(self):
        if self.computer_id:
            return self.computer
        if self.switch_id:
            return self.switch
        if self.router_id:
            return self.router
        return None

    def clean(self):
        selected_count = sum(
            value is not None
            for value in [self.computer_id, self.switch_id, self.router_id]
        )

        if selected_count != 1:
            raise ValidationError("Нужно выбрать ровно одну модель устройства: computer, switch или router.")

    def ensure_ports(self):
        catalog_item = self.catalog_item
        if catalog_item is None or catalog_item.max_connected_devices is None:
            return

        existing_indexes = set(self.ports.values_list("index", flat=True))
        new_ports = []

        for index in range(1, catalog_item.max_connected_devices + 1):
            if index in existing_indexes:
                continue

            new_ports.append(
                Port(
                    device=self,
                    index=index,
                    name=f"eth{index}",
                    is_active=True,
                )
            )

        if new_ports:
            Port.objects.bulk_create(new_ports)

    def delete_related_links(self):
        Link.objects.filter(Q(port_a__device=self) | Q(port_b__device=self)).delete()

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.full_clean()
            super().save(*args, **kwargs)
            self.ensure_ports()

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            self.delete_related_links()
            return super().delete(*args, **kwargs)


class Port(models.Model):
    device = models.ForeignKey(TopologyDevice, on_delete=models.CASCADE, related_name="ports")
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


class Link(models.Model):
    port_a = models.OneToOneField(Port, on_delete=models.CASCADE, related_name="link_as_a")
    port_b = models.OneToOneField(Port, on_delete=models.CASCADE, related_name="link_as_b")
    cable = models.ForeignKey(Cable, on_delete=models.SET_NULL, null=True, blank=True, related_name="links")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=~Q(port_a=F("port_b")), name="link_ports_must_differ"),
        ]
        ordering = ["-created_at"]

    def clean(self):
        if not self.port_a_id or not self.port_b_id:
            return

        if self.port_a_id == self.port_b_id:
            raise ValidationError("Нельзя соединять порт сам с собой.")

        if self.port_a.device_id == self.port_b.device_id:
            raise ValidationError("Нельзя соединять устройство само с собой.")

        busy_links = Link.objects.exclude(pk=self.pk).filter(
            Q(port_a_id=self.port_a_id)
            | Q(port_b_id=self.port_a_id)
            | Q(port_a_id=self.port_b_id)
            | Q(port_b_id=self.port_b_id)
        )
        if busy_links.exists():
            raise ValidationError("Один из портов уже занят.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.full_clean()
            super().save(*args, **kwargs)
