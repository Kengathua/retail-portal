"""Common serializers."""

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.fields import SerializerMethodField, CharField

from django.db.models import ForeignKey, ManyToManyField
from django.core.exceptions import ValidationError


class AuditFieldsMixin(ModelSerializer):
    """Handle audit fields.

    * Audit field are `id`, `created_by`, `updated_by`, `created_on`,
    *`updated_on` and `franchise`.
    * When creating a new record, an `id` should not be supplied
    * `created_by`, `franchise` and `updated_by` are
      auto-filled when creating new records
    * `updated_by` is auto-filled when updating new records
    * `franchise` is stripped from all requests
    * when creating or updating records, supplied audit fields
      (`created_by`, `updated_by`, `created`, `updated`) are ignored
    """

    def __init__(self, *args, **kwargs):
        """Initialize an audit fields and business partner aware serializer."""
        super().__init__(*args, **kwargs)
        exclude_fields = ['created', 'created_by', 'updated', 'updated_by']
        exclude_fields_all_methods = ['franchise']
        context = getattr(self, 'context', {})
        self.request = context.get('request', {})
        include_in_methods = ['get', 'head', 'options']
        request_method = getattr(self.request, "method", '').lower()

        if request_method not in include_in_methods:
            for i in exclude_fields:
                if i in self.fields:
                    self.fields.pop(i)

        # remove the fields on all views
        for i in exclude_fields_all_methods:
            if i in self.fields:
                self.fields.pop(i)

    def _populate_audit_fields(self, data, is_create):
        """Auto update the audit fields with the user data."""
        # request = self.context['request']
        self.user = self.request.user
        data['updated_by'] = self.user.pk

        if is_create:
            data['created_by'] = self.user.pk
            if not self.__class__.__name__ == 'FranchiseSerializer':
                data['franchise'] = self.user.franchise

        return data

    def create(self, cleaned_data):
        """Ensure that audit fields are filled for new records."""
        initial_data_id = (
            isinstance(self.initial_data, dict) and self.initial_data.get('id'))
        if initial_data_id or cleaned_data.get('id'):
            raise ValidationError(
                {"id": "You are not allowed to pass object with an id"})
        self._populate_audit_fields(cleaned_data, True)
        return super().create(cleaned_data)

    def update(self, instance, cleaned_data):
        """Ensure that update tracking fields are filled in."""
        self._populate_audit_fields(cleaned_data, False)
        return super().update(instance, cleaned_data)


class BaseSerializerMixin(AuditFieldsMixin):
    """Base Serializer class."""

    created_by = serializers.UUIDField()
    creator = CharField(read_only=True)
    updater = CharField(read_only=True)

    def serialize_instance(self, instance, ignore_fields=[]):
        """Serialize a model instance."""
        ignore_fields += [
            'created_by', 'updated_by', 'created_on',
            'updated_on', 'franchise', 'pushed_to_edi',
        ]

        fields = instance._meta.get_fields(include_hidden=True)
        data = {}

        for field in fields:
            if field.name not in ignore_fields:
                if isinstance(field, ForeignKey):
                    related_model = field.related_model
                    result = None
                    if not field.null:
                        source_instance = related_model.objects.get(
                            id=field.value_from_object(instance))
                        result = self.serialize_instance(source_instance)

                    data[field.name] = result

                if isinstance(field, ManyToManyField):
                    fields = instance._meta.many_to_many
                    data = {}
                    for f in instance._meta.many_to_many:
                        many_instances = f.value_from_object(instance)
                        results = []
                        for one_instance in many_instances:
                            result = self.serialize_instance(one_instance)
                            results.append(result)
                        data[f.name] = results

                try:
                    data[field.name] = instance.__dict__[field.name]
                    # data[field.name] = field.value_from_object(instance)
                # except AttributeError:
                #     pass

                except KeyError:
                    pass

        return data

    all_data = SerializerMethodField()

    def get_all_data(self, instance):
        """Get all data."""
        data = self.serialize_instance(instance)
        return data


class PartialUpdateSerializer(serializers.Serializer):
    """Partial Updates serializer file."""

    def partial_update(self, instance, validated_data):
        """Perform partial updates."""
        return super().update(instance, validated_data)
