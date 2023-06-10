from rest_framework import serializers

from .. import models


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(source="get_username")
    full_name = serializers.CharField(source="get_full_name")


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    address = serializers.StringRelatedField()

    class Meta:
        model = models.Location
        fields = "__all__"


class EquipmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EquipmentType
        fields = "__all__"


class ContractNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContractNumber
        fields = "__all__"


class ObjectSerializer(serializers.ModelSerializer):
    equipment_type = serializers.StringRelatedField()

    class Meta:
        model = models.Object
        fields = ("id", "name", "short_name", "description", "equipment_type")


class HistoricalRecordField(serializers.ListField):
    child = serializers.DictField()

    def to_representation(self, data):
        return super().to_representation(data.values())


class InstanceSerializer(serializers.ModelSerializer):
    object = ObjectSerializer()
    state = serializers.StringRelatedField()
    contract_number = ContractNumberSerializer()
    owner = serializers.StringRelatedField()
    location = LocationSerializer()
    history = HistoricalRecordField()

    class Meta:
        model = models.Instance
        fields = "__all__"


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Report
        fields = "__all__"


class ReportGetSerializer(ReportSerializer):
    location = LocationSerializer()
    user = UserSerializer()


class ReportRetrieveSerializer(ReportSerializer):
    username = serializers.CharField(source="user.get_username")
    full_name = serializers.CharField(source="user.get_full_name")
    location = serializers.StringRelatedField()


class ReportScannedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReportScannedItem
        fields = "__all__"
