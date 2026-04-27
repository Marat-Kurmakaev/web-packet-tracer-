from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.db.models import Q
from rest_framework import serializers

from .models import Computer, Switch, Router, Cable, TopologyDevice, Port, Link


CATALOG_ITEM_FIELDS = [
    "id",
    "name",
    "image",
    "description",
    "price",
    "max_connected_devices",
]


def _normalize_validation_error(exc):
    if hasattr(exc, "message_dict"):
        return {
            ("non_field_errors" if field == "__all__" else field): messages
            for field, messages in exc.message_dict.items()
        }

    if hasattr(exc, "messages"):
        return {"non_field_errors": list(exc.messages)}

    return {"non_field_errors": [str(exc)]}


def _raise_as_drf_validation_error(exc):
    raise serializers.ValidationError(_normalize_validation_error(exc))


class SafeModelSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except DjangoValidationError as exc:
            _raise_as_drf_validation_error(exc)
        except IntegrityError:
            raise serializers.ValidationError(
                {"non_field_errors": ["Не удалось сохранить объект из-за конфликта данных."]}
            )

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except DjangoValidationError as exc:
            _raise_as_drf_validation_error(exc)
        except IntegrityError:
            raise serializers.ValidationError(
                {"non_field_errors": ["Не удалось обновить объект из-за конфликта данных."]}
            )


class ComputerSerializer(SafeModelSerializer):
    class Meta:
        model = Computer
        fields = CATALOG_ITEM_FIELDS


class SwitchSerializer(SafeModelSerializer):
    class Meta:
        model = Switch
        fields = CATALOG_ITEM_FIELDS


class RouterSerializer(SafeModelSerializer):
    class Meta:
        model = Router
        fields = CATALOG_ITEM_FIELDS


class CableSerializer(SafeModelSerializer):
    class Meta:
        model = Cable
        fields = ["id", "name", "image", "description", "price"]


class PortSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source="device.name", read_only=True)

    class Meta:
        model = Port
        fields = ["id", "device", "device_name", "name", "index", "is_active"]
        read_only_fields = ["name", "index", "is_active"]


class TopologyDeviceSerializer(SafeModelSerializer):
    computer = serializers.PrimaryKeyRelatedField(
        queryset=Computer.objects.all(),
        required=False,
        allow_null=True,
    )
    switch = serializers.PrimaryKeyRelatedField(
        queryset=Switch.objects.all(),
        required=False,
        allow_null=True,
    )
    router = serializers.PrimaryKeyRelatedField(
        queryset=Router.objects.all(),
        required=False,
        allow_null=True,
    )
    catalog_type = serializers.SerializerMethodField()
    catalog_item = serializers.SerializerMethodField()
    ports = PortSerializer(many=True, read_only=True)

    class Meta:
        model = TopologyDevice
        fields = [
            "id",
            "name",
            "computer",
            "switch",
            "router",
            "catalog_type",
            "catalog_item",
            "ports",
        ]

    def validate(self, attrs):
        computer = attrs.get("computer", getattr(self.instance, "computer", None))
        switch = attrs.get("switch", getattr(self.instance, "switch", None))
        router = attrs.get("router", getattr(self.instance, "router", None))

        selected_count = sum(value is not None for value in [computer, switch, router])
        if selected_count != 1:
            raise serializers.ValidationError(
                {"non_field_errors": ["Нужно выбрать ровно одну модель устройства: computer, switch или router."]}
            )

        return attrs

    def get_catalog_type(self, obj):
        if obj.computer_id:
            return "computer"
        if obj.switch_id:
            return "switch"
        if obj.router_id:
            return "router"
        return None

    def get_catalog_item(self, obj):
        if obj.computer_id:
            return ComputerSerializer(obj.computer, context=self.context).data
        if obj.switch_id:
            return SwitchSerializer(obj.switch, context=self.context).data
        if obj.router_id:
            return RouterSerializer(obj.router, context=self.context).data
        return None


class LinkSerializer(SafeModelSerializer):
    port_a_name = serializers.CharField(source="port_a.name", read_only=True)
    port_b_name = serializers.CharField(source="port_b.name", read_only=True)
    device_a_name = serializers.CharField(source="port_a.device.name", read_only=True)
    device_b_name = serializers.CharField(source="port_b.device.name", read_only=True)
    cable_name = serializers.CharField(source="cable.name", read_only=True)
    cable_data = CableSerializer(source="cable", read_only=True)

    class Meta:
        model = Link
        fields = [
            "id",
            "port_a",
            "port_a_name",
            "device_a_name",
            "port_b",
            "port_b_name",
            "device_b_name",
            "cable",
            "cable_name",
            "cable_data",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate(self, attrs):
        port_a = attrs.get("port_a", getattr(self.instance, "port_a", None))
        port_b = attrs.get("port_b", getattr(self.instance, "port_b", None))

        if port_a is None or port_b is None:
            return attrs

        if port_a == port_b:
            raise serializers.ValidationError({"non_field_errors": ["Нельзя соединять порт сам с собой."]})

        if port_a.device_id == port_b.device_id:
            raise serializers.ValidationError({"non_field_errors": ["Нельзя соединять устройство само с собой."]})

        qs = Link.objects.all()
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.filter(Q(port_a=port_a) | Q(port_b=port_a)).exists():
            raise serializers.ValidationError({"port_a": ["Этот порт уже занят."]})

        if qs.filter(Q(port_a=port_b) | Q(port_b=port_b)).exists():
            raise serializers.ValidationError({"port_b": ["Этот порт уже занят."]})

        return attrs
