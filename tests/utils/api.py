"""."""

import uuid
from decimal import Decimal
from dateutil.parser import parse
from datetime import date, datetime, timedelta

from django.urls import reverse
from django.db.models import ForeignKey, OneToOneField
from django.db.models import CharField, DecimalField, FloatField, IntegerField
from django.db.models.fields.files import FieldFile
from .login_mixins import LoggedInMixin, authenticate_test_user

from model_bakery import baker


class APITests(LoggedInMixin, object):
    """."""

    id_field = 'pk'
    result_id_field = 'id'
    ignore_fields = [
        'updated_by', 'created_by', 'created_on', 'updated_on',
        'deleted', 'id', 'enterprise'
    ]
    write_only_fields = []
    post_ignore_fields = []
    patch_ignore_fields = []

    def setUp(self):
        # self.client = authenticate_test_user()
        return super().setUp()

    def get_enterprise_code(self):
        """."""
        prep = self.recipe.prepare()
        return prep.enterprise

    def process_date(self, date):
        """Process date to the correct format."""
        try:
            d_date = parse(date, dayfirst=True)
            return d_date.date()
    
        except TypeError:
            d_date = self.process_date(date.strftime('%m/%d/%Y'))
            return d_date

    def make(self, **kwargs):
        """."""
        if getattr(self, 'recipe', None):
            return self.recipe.make()

        return baker.make(self.model, **kwargs)

    def handle_fk(self, field):
        """."""
        if getattr(self, 'fk_recipes', None) and field.name in self.fk_recipes:
            recipe = self.fk_recipes[field.name]
            instance = recipe.make()
            return instance

        return baker.make(field.remote_field.model)

    def make_data(self, ignore_fields=[]):
        """."""
        if getattr(self, 'recipe', None):
            prepped = self.recipe.prepare()
            model = self.recipe._model
        else:
            prepped = baker.prepare(self.model)
            model = self.model

        data = {}
        for field in model._meta.fields:
            if field.name in ignore_fields:
                continue

            if field.null:
                # handle nullable fk fields that have recipes
                if getattr(self, 'fk_recipes', None) and field.name in self.fk_recipes:
                    instance = self.handle_fk(field)
                    data[field.name] = getattr(instance, self.id_field)
                else:
                    # handle nullable fields specified in recipe
                    value = getattr(prepped, field.name, None)
                    if value and not isinstance(field, ForeignKey):
                        data[field.name] = value
                continue

            if isinstance(field, ForeignKey):
                instance = self.handle_fk(field)
                data[field.name] = getattr(instance, self.id_field)
                continue

            data[field.name] = getattr(prepped, field.name)
        return data


    def get_model(self):
        """."""
        if getattr(self, 'recipe', None):
            model = self.recipe._model
        else:
            model = self.model
        return model


    def patch_data(self):
        """."""
        return self.make_data(self.ignore_fields + self.patch_ignore_fields)


    def compare_dicts(self, test_dict, candidate_dict):
        """."""
        for key in test_dict:
            if key in self.write_only_fields:
                assert key not in candidate_dict
                continue

            assert key in test_dict, (key, test_dict)
            assert key in candidate_dict, (key, candidate_dict)

            val1 = test_dict[key]
            val2 = candidate_dict[key]

            if (isinstance(val2, (dict,)) and 'id' in val2) or (
                    isinstance(val1, dict) and 'id' in val1):
                if isinstance(val2, (dict,)) and 'id' in val2:
                    val2 = val2['id']

                if isinstance(val1, (dict,)) and 'id' in val1:
                    val1 = val1['id']

                assert str(val1) == str(val2)
                continue

            if isinstance(val1, uuid.UUID) or isinstance(val2, uuid.UUID):
                assert str(val1) == str(val2), '{}:{}'.format(str(val1), str(val2))
                continue

            if isinstance(val2, (dict,)) or isinstance(val1, (dict,)):
                self.compare_dicts(dict(val1), dict(val2))
                # also take care of collections.OrderedDict
                continue

            if isinstance(val1, list) or isinstance(val2, list):
                for cmp1, cmp2 in zip(val1, val2):
                    self.compare_dicts(cmp1, cmp2)

                continue

            if isinstance(val1, (Decimal, int, float)) or isinstance(val2, (Decimal, int, float)):
                assert Decimal(float(val1)) == Decimal(float(val2))
                continue

            if isinstance(val1, datetime) or isinstance(val2, datetime):
                if not isinstance(val2, datetime):
                    dt2 = parse(val2)
                else:
                    dt2 = val2

                if not isinstance(val1, datetime):
                    dt1 = parse(val1)
                else:
                    dt1 = val1

                assert dt1 - dt2 < timedelta(seconds=1)
                continue

            if isinstance(val1, date) or isinstance(val2, date):
                val1 = self.process_date(val1)
                val2 = self.process_date(val2)
                assert str(val1) == str(val2)
                continue

            test_value = test_dict[key] or ''
            candidate_value = candidate_dict[key] or ''
            if not type(test_value) == FieldFile:
                assert candidate_value.title() == test_value.title(), '{}  should equal -> {}, key {}'.format(  # noqa
                    candidate_dict[key], test_dict[key], key)

    def get_test_data(self, instance):
        data = {}
        for field in self.recipe._model._meta.fields:
            if not field.name in self.ignore_fields:
                data[field.name] = getattr(instance, field.name)
                if field.null:
                    value = getattr(instance, field.name, None)
                    data[field.name] = value if value else ''
                    if isinstance(field, CharField):
                        data[field.name] = value or ''

                    if isinstance(
                            field, FloatField) or isinstance(
                                field, DecimalField) or isinstance(
                                    field, IntegerField):
                        data[field.name] = value if value else 0

                    if value and not isinstance(field, ForeignKey) and not isinstance(field, OneToOneField):
                        data[field.name] = value if value else ''
                    continue

                if isinstance(field, OneToOneField):
                    f_instance = getattr(instance, field.name)
                    data[field.name] = getattr(f_instance, self.id_field)
                    if self._testMethodName == 'test_post':
                        self.recipe._model.objects.filter(id=instance.id).delete()

                if isinstance(field, ForeignKey):
                    f_instance = getattr(instance, field.name)
                    data[field.name] = getattr(f_instance, self.id_field)
                    continue

        return data

    def post_data(self):
        """."""
        return self.make_data(self.ignore_fields + self.post_ignore_fields)

    def test_list_specific_fields(self, status_code=200):
        """."""
        self.client = authenticate_test_user()

        for model in self.get_model()._meta.related_objects:
            model.related_model.objects.all().delete()
        self.get_model().objects.all().delete()
        instance = self.make()

        model_meta = self.get_model()._meta
        model_field_names = [
            f.name
            for f in model_meta.get_fields(include_parents=False, include_hidden=False)
            if f.name not in self.ignore_fields
        ]
        url = reverse(self.url + '-list') + '?fields={}'.format(','.join(model_field_names))
        resp = self.client.get(url)
        assert resp.status_code == status_code, '{}, {}'.format(resp.content, url)
        if resp.status_code != 200:
            return resp
        assert len(resp.data['results']) == 1

        return instance, resp

    def test_list(self, status_code=200):
        """."""
        self.client = authenticate_test_user()
        for model in self.get_model()._meta.related_objects:
            model.related_model.objects.all().delete()
        self.get_model().objects.all().delete()
        instance = self.make()
        url = reverse(self.url + '-list')
        resp = self.client.get(url)
        assert resp.status_code == status_code, '{}, {}'.format(resp.content, url)
        if resp.status_code != 200:
            return resp

        assert resp.data['count'] == 1
        assert len(resp.data['results']) == 1
        return instance, resp

    def test_get(self, status_code=200):
        """."""
        self.client = authenticate_test_user()

        instance = self.make()
        test_id = getattr(instance, self.id_field)
        assert test_id, test_id
        assert instance.__class__.objects.get(pk=test_id), \
            'unable to get instance with PK {}'.format(test_id)
        url = reverse(self.url + '-detail', kwargs={self.id_field: test_id})
        resp = self.client.get(url)
        assert resp.status_code == status_code, '{}, {}'.format(resp.content, url)
        if resp.status_code != 200:
            return resp
        assert resp.data[self.result_id_field] == str(test_id)
        return instance, resp

    def test_post(self, status_code=201):
        """."""
        self.client = authenticate_test_user()

        test_post_data = self.post_data()
        url = reverse(self.url + '-list')
        resp = self.client.post(url, test_post_data)
        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, test_post_data)  # noqa
        if resp.status_code != 201:
            return resp

        self.compare_dicts(test_post_data, resp.data)

        return test_post_data, resp

    def test_put(self, status_code=200):
        """."""
        self.client = authenticate_test_user()

        instance = self.make()
        test_data = self.patch_data()
        test_id = getattr(instance, self.id_field)
        url = reverse(
            self.url + '-detail', kwargs={self.id_field: test_id}
        )

        resp = self.client.put(url, test_data)
        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, test_data)
        return resp

    def test_patch(self, status_code=200):
        """."""
        self.client = authenticate_test_user()

        instance = self.make()
        test_data = self.patch_data()
        test_id = getattr(instance, self.id_field)
        assert test_id, test_id
        assert instance.__class__.objects.get(pk=test_id), \
            'unable to get instance with PK {}'.format(test_id)
        url = reverse(
            self.url + '-detail', kwargs={self.id_field: test_id}
        )
        resp = self.client.patch(url, test_data)
        assert resp.status_code == status_code, '{}, {}, {}'.format(resp.content, url, test_data)
        return resp

    def test_delete(self, status_code=204):
        self.client = authenticate_test_user()

        instance = self.make()
        test_id = getattr(instance, self.id_field)
        assert test_id, test_id
        assert instance.__class__.objects.get(pk=test_id), \
            'unable to get instance with PK {}'.format(test_id)
        url = reverse(self.url + '-detail', kwargs={self.id_field: test_id})
        resp = self.client.delete(url)
        assert resp.status_code == status_code, '{}, {}'.format(resp.content, url)
        return instance, resp
