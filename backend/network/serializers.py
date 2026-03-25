from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.db.models import Q
from rest_framework import serializers

from .models import Building, Room, DeviceType, Device, Port, Cable, Link, DeviceKind


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


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ["id", "name"]


class RoomSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source="building.name", read_only=True)

    class Meta:
        model = Room
        fields = ["id", "name", "building", "building_name", "x", "y", "width", "height"]


class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = ["id", "name", "kind", "ports_count", "base_price", "width", "height"]


class PortSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source="device.name", read_only=True)

    class Meta:
        model = Port
        fields = ["id", "device", "device_name", "name", "index", "is_active"]


class DeviceSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name", read_only=True)
    device_type_name = serializers.CharField(source="device_type.name", read_only=True)
    kind = serializers.CharField(source="device_type.kind", read_only=True)
    width = serializers.IntegerField(read_only=True)
    height = serializers.IntegerField(read_only=True)
    ports = PortSerializer(many=True, read_only=True)
    effective_price = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = [
            "id",
            "name",
            "room",
            "room_name",
            "device_type",
            "device_type_name",
            "kind",
            "x",
            "y",
            "width",
            "height",
            "price_override",
            "effective_price",
            "ports",
        ]

    def get_effective_price(self, obj):
        return obj.price_override if obj.price_override is not None else obj.device_type.base_price

    def create(self, validated_data):
        try:
            return Device.objects.create(**validated_data)
        except DjangoValidationError as exc:
            _raise_as_drf_validation_error(exc)
        except IntegrityError:
            raise serializers.ValidationError(
                {"non_field_errors": ["Не удалось сохранить устройство из-за конфликта данных."]}
            )

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        try:
            instance.save()
        except DjangoValidationError as exc:
            _raise_as_drf_validation_error(exc)
        except IntegrityError:
            raise serializers.ValidationError(
                {"non_field_errors": ["Не удалось обновить устройство из-за конфликта данных."]}
            )

        return instance


class CableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cable
        fields = ["id", "name", "length_m", "price"]


class LinkSerializer(serializers.ModelSerializer):
    port_a_name = serializers.CharField(source="port_a.name", read_only=True)
    port_b_name = serializers.CharField(source="port_b.name", read_only=True)
    device_a_name = serializers.CharField(source="port_a.device.name", read_only=True)
    device_b_name = serializers.CharField(source="port_b.device.name", read_only=True)

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

        kind_a = port_a.device.device_type.kind
        kind_b = port_b.device.device_type.kind
        if kind_a == DeviceKind.PC and kind_b == DeviceKind.PC:
            raise serializers.ValidationError({"non_field_errors": ["Соединение PC ↔ PC запрещено."]})

        qs = Link.objects.all()
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.filter(Q(port_a=port_a) | Q(port_b=port_a)).exists():
            raise serializers.ValidationError({"port_a": ["Этот порт уже занят."]})

        if qs.filter(Q(port_a=port_b) | Q(port_b=port_b)).exists():
            raise serializers.ValidationError({"port_b": ["Этот порт уже занят."]})

        return attrs

    def create(self, validated_data):
        try:
            return Link.objects.create(**validated_data)
        except DjangoValidationError as exc:
            _raise_as_drf_validation_error(exc)
        except IntegrityError:
            raise serializers.ValidationError(
                {"non_field_errors": ["Не удалось создать соединение из-за конфликта данных."]}
            )

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        try:
            instance.save()
        except DjangoValidationError as exc:
            _raise_as_drf_validation_error(exc)
        except IntegrityError:
            raise serializers.ValidationError(
                {"non_field_errors": ["Не удалось обновить соединение из-за конфликта данных."]}
            )

        return instance
