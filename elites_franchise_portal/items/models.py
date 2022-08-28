"""Debit side item build up models."""

from django.db import models
from django.db.models import CASCADE, PROTECT
from django.core.exceptions import ValidationError

from elites_franchise_portal.common.models import AbstractBase
from elites_franchise_portal.common.code_generators import generate_elites_code
from elites_franchise_portal.franchises.models import Franchise
from elites_franchise_portal.common.validators import (
    items_elites_code_validator, units_elites_code_validator)
from elites_franchise_portal.users.models import retrieve_user_email


ITEM_ATTRIBUTE_TYPES = (
    ('SPECIAL OFFER', 'SPECIAL OFFER'),
    ('WARRANTY', 'WARRANTY'),
    ('SPECIAL FEATURE', 'SPECIAL FEATURE'),
    ('SPECIFICATION', 'SPECIFICATION'),
    ('DESCRIPTION', 'DESCRIPTION')
)


def validate_franchise_exists(object):
    """Validate franchise code."""
    franchise_exists = Franchise.objects.filter(elites_code=object.franchise).exists()
    if not franchise_exists:
        raise ValidationError([{
            'franchise': f'Franchise with franchise code {object.franchise} does not exist'
        }])


def captalize_field(field_names):
    """Capitalize field values."""
    for field_name in field_names:
        val = getattr(field_name, False)
        if val:
            setattr(field_name, val.upper())


class Category(AbstractBase):
    """Item categories eg. ELECTRONICS, UTENSILS, COOKER."""

    category_name = models.CharField(max_length=300)
    category_code = models.CharField(
        max_length=250, null=True, blank=True,
        validators=[items_elites_code_validator])
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def create_category_code(self):
        """Create a code for the category."""
        if not self.category_code:
            self.category_code = generate_elites_code(self)

    def clean(self) -> None:
        """Clean the category."""
        # validate_franchise_exists(self)
        self.create_category_code()
        return super().clean()

    def __str__(self):
        """Str representation for the section model."""
        return '{}'.format(
            self.category_name,
            )

    class Meta:
        """Meta class for category."""

        ordering = ['category_name']


class ItemType(AbstractBase):
    """Item types eg.Fridge, Cooker, Microwave."""

    category = models.ForeignKey(
        Category, null=False, blank=False, on_delete=CASCADE)
    type_name = models.CharField(max_length=250)
    type_code = models.CharField(
        max_length=250, null=True, blank=True, validators=[items_elites_code_validator])
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def create_type_code(self):
        """Create a code for the item type."""
        if not self.type_code:
            self.type_code = generate_elites_code(self)

    def clean(self) -> None:
        """Clean the item type model."""
        # validate_franchise_exists(self)
        self.create_type_code()
        return super().clean()

    def __str__(self):
        """Str representation for the item-models model."""
        return '{} -> {}'.format(
            self.type_name,
            self.category.category_name,
            )

    class Meta:
        """Meta class for section model."""

        ordering = ['-type_name']


class Brand(AbstractBase):
    """Item brand model for items eg. Samsung, LG, Sony."""

    item_types = models.ManyToManyField(
        ItemType, through='BrandItemType', related_name='branditemtypes')
    brand_name = models.CharField(max_length=250)
    brand_code = models.CharField(
        max_length=250, null=True, blank=True, validators=[items_elites_code_validator])
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def create_brand_code(self):
        """Create a code for the brand."""
        if not self.brand_code:
            self.brand_code = generate_elites_code(self)

    def clean(self) -> None:
        """Clean the brand model."""
        self.create_brand_code()
        return super().clean()

    def __str__(self):
        """Str representation for the item-models model."""
        item_types = self.item_types.all()
        type_names = [item_type.type_name for item_type in item_types if item_types]

        return '{} -> {}'.format(
            self.brand_name,
            ", ".join(type_names)
            )

    class Meta:
        """Meta class for item brands."""

        ordering = ['-brand_name']


class BrandItemType(AbstractBase):
    """Brand Item Type many to many through model."""

    brand = models.ForeignKey(
        Brand, null=False, blank=False, on_delete=CASCADE)
    item_type = models.ForeignKey(
        ItemType, null=False, blank=False, on_delete=CASCADE)
    pushed_to_edi = models.BooleanField(default=False)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def __str__(self):
        """Str representation for the category section model."""
        return '{} -> {}'.format(
            self.brand.brand_name,
            self.item_type.type_name)

    class Meta:
        """Meta class."""

        constraints = [
            models.UniqueConstraint(
                fields=['brand', 'item_type'],
                name='unique_brand_per_type')
        ]
        ordering = (
            'brand__brand_name', 'item_type__type_name',
            )


class ItemModel(AbstractBase):
    """Item models model."""

    brand = models.ForeignKey(
        Brand, null=False, blank=False, on_delete=models.PROTECT)
    item_type = models.ForeignKey(
        ItemType, null=False, blank=False, on_delete=models.PROTECT)
    model_name = models.CharField(max_length=250)
    model_code = models.CharField(
        max_length=250, null=True, blank=True, validators=[items_elites_code_validator])
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def create_model_code(self):
        """Create a code for the item model."""
        if not self.model_code:
            self.model_code = generate_elites_code(self)

    def clean(self) -> None:
        """Clean the ItemModel model."""
        # validate_franchise_exists(self)
        self.create_model_code()
        return super().clean()

    def __str__(self):
        """Str representation for the item-models model."""
        return '{} -> {} {}'.format(
            self.model_name, self.brand.brand_name,
            self.item_type.type_name)

    class Meta:
        """Meta class for item models."""

        ordering = ['-model_name']


class Item(AbstractBase):
    """Item model."""

    item_model = models.OneToOneField(
        ItemModel, null=False, blank=False, on_delete=PROTECT)
    barcode = models.CharField(
        null=False, blank=False, max_length=250)
    item_name = models.CharField(
        null=True, blank=True, max_length=250)
    item_code = models.CharField(
        null=True, blank=True, max_length=250,
        validators=[items_elites_code_validator])
    make_year = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    pushed_to_edi = models.BooleanField(default=False)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def get_item_name(self):
        """Get the item's name."""
        type = self.item_model.item_type.type_name
        brand = self.item_model.brand.brand_name
        model = self.item_model.model_name
        self.item_name = brand + ' ' + model + ' ' + type

    def create_item_code(self):
        """Create a code for the item."""
        if not self.item_code:
            self.item_code = generate_elites_code(self)

    def clean(self) -> None:
        """Clean the item model."""
        # validate_franchise_exists(self)
        self.get_item_name()
        self.create_item_code()
        return super().clean()

    def __str__(self):
        """Str representation for item model."""
        return f'{self.item_name}'

    def activate(self):
        """Activate a product by setting it up in inventory and catalog."""
        from elites_franchise_portal.debit.models import (
            Inventory, InventoryItem, InventoryInventoryItem)
        from elites_franchise_portal.debit.models import (
            Warehouse, WarehouseItem, WarehouseWarehouseItem)
        from elites_franchise_portal.catalog.models import Catalog

        private_warehouse = Warehouse.objects.filter(
            is_active=True, warehouse_type='PRIVATE', franchise=self.franchise)
        master_inventory = Inventory.objects.filter(
            is_master=True, is_active=True, franchise=self.franchise)
        audit_fields = {
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'franchise': self.franchise,
            }

        if not private_warehouse.exists():
            raise ValidationError(
                {'private_warehouse': 'You do not have an activate private warehouse set up. '
                 'Please set that up to activate your products'})

        if not master_inventory.exists():
            raise ValidationError(
                {'master_inventory': 'You do not have an active master inventory for your entity.'
                 ' Please set that up to activate your products'})

        available_inventory = Inventory.objects.filter(
            inventory_type='AVAILABLE', is_active=True, franchise=self.franchise)
        if not available_inventory.exists():
            raise ValidationError(
                {'available inventory': 'You do not have an active available inventory set up. '
                 'Please set that up to activate your products'})

        catalog = Catalog.objects.filter(
            is_active=True, is_standard=True, franchise=self.franchise)
        if not catalog.exists():
            raise ValidationError(
                {'catalog': 'You do not have an active standard catalog set up. '
                 'Please set that up to activate your products'})

        private_warehouse = private_warehouse.first()
        master_inventory = master_inventory.first()
        available_inventory = available_inventory.first()
        catalog = catalog.first()

        if not WarehouseItem.objects.filter(item=self).exists():
            payload = {
                'item': self,
                'description': self.item_name,
            }
            warehouse_item = WarehouseItem.objects.create(**payload, **audit_fields)
            WarehouseWarehouseItem.objects.create(
                warehouse=private_warehouse, warehouse_item=warehouse_item, **audit_fields)

        else:
            defaults = {'warehouse': private_warehouse}
            warehouse_item = WarehouseItem.objects.get(item=self)
            WarehouseWarehouseItem.objects.update_or_create(
                defaults=defaults, warehouse_item=warehouse_item, **audit_fields)

        if not InventoryItem.objects.filter(item=self).exists():
            payload = {
                'item': self,
                'description': self.item_name,
                }
            inventory_item = InventoryItem.objects.create(**payload, **audit_fields)
            InventoryInventoryItem.objects.create(
                inventory=master_inventory, inventory_item=inventory_item, **audit_fields)
            InventoryInventoryItem.objects.create(
                inventory=available_inventory, inventory_item=inventory_item, **audit_fields)

        else:
            inventory_item = InventoryItem.objects.get(item=self)
            master_payload = {
                'inventory': master_inventory,
                'inventory_item': inventory_item,
                }
            available_payload = {
                'inventory': available_inventory,
                'inventory_item': inventory_item,
                }

            if not InventoryInventoryItem.objects.filter(**master_payload).exists():
                InventoryInventoryItem.objects.create(**master_payload, **audit_fields)

            if not InventoryInventoryItem.objects.filter(**available_payload).exists():
                InventoryInventoryItem.objects.create(**available_payload, **audit_fields)

        self.is_active = True
        self.save()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions on the Item model."""
        super().save(*args, **kwargs)

    class Meta:
        """Meta class for items."""

        ordering = ['-item_name']


class ItemAttribute(AbstractBase):
    """Item attribues model."""

    item = models.ForeignKey(
        Item, null=False, blank=False, on_delete=CASCADE)
    attribute_type = models.CharField(
        max_length=300, choices=ITEM_ATTRIBUTE_TYPES)
    attribute_value = models.TextField()
    is_active = models.BooleanField(default=True)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    @property
    def special_features(self):
        """Get a list of all speacial features as attributes."""
        attributes = self.__class__.objects.filter(
            item=self.item, attribute_type='SPECIAL FEATURE')
        special_features = []

        for attribute in attributes:
            special_features.append(attribute.attribute_value)

        return special_features

    @property
    def special_offers(self):
        """Get a list of special_offers linked to an item."""
        attributes = self.__class__.objects.filter(
            item=self.item, attribute_type='SPECIAL OFFER')
        special_offers = []

        for attribute in attributes:
            special_offers.append(attribute.attribute_value)

        return special_offers

    @property
    def specifications(self):
        """Get a list of specifications linked to a project."""
        attributes = self.__class__.objects.filter(
            item=self.item, attribute_type='SPECIFICATION')
        specifications = []

        for attribute in attributes:
            specifications.append(attribute.attribute_value)

        return specifications

    @property
    def description(self):
        """Get a list of descriptive statements used for an item."""
        attributes = self.__class__.objects.filter(
            item=self.item, attribute_type='DESCRIPTION')
        description = []

        for attribute in attributes:
            description.append(attribute.attribute_value)

        return description

    def clean(self) -> None:
        """Add excel uploads for item attributes."""
        # validate_franchise_exists(self)
        return super().clean()

    class Meta:
        """Meta class for Item attributes."""

        ordering = ['-attribute_type', '-attribute_value']


class Units(AbstractBase):
    """Units mode."""

    item_types = models.ManyToManyField(
        ItemType, through='UnitsItemType', related_name='itemtype')  # eg. TV, Fridge
    units_name = models.CharField(
        null=False, blank=False, max_length=300)
    units_code = models.CharField(
        null=True, blank=True, max_length=250, validators=[units_elites_code_validator])
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def create_units_code(self):
        """Create a code for the units."""
        if not self.units_code:
            self.units_code = generate_elites_code(self)

    def clean(self) -> None:
        """Clean the units model."""
        # validate_franchise_exists(self)
        self.create_units_code()
        return super().clean()

    def __str__(self):
        """Str representation for the item-models model."""
        item_types = self.item_types.all()
        type_names = [item_type.type_name for item_type in item_types]
        return '{} -> {}'.format(
            self.units_name,
            ", ".join(type_names),)

    class Meta:
        """Meta class dor item measure units."""

        ordering = ['-units_name']


class UnitsItemType(AbstractBase):
    """Units Item type many to many model."""

    units = models.ForeignKey(
        Units,
        on_delete=models.CASCADE,
        related_name='itemtype_units')
    item_type = models.ForeignKey(
        ItemType,
        on_delete=models.CASCADE,
        related_name='units_itemtype')
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def __str__(self):
        """Str representation for the item type units model."""
        return '{} -> {}'.format(
            self.units.units_name,
            self.type.type_name)

    class Meta:
        """Meta class."""

        constraints = [
            models.UniqueConstraint(
                fields=['units', 'item_type'],
                name='unique_units_per_item_type')
        ]
        ordering = (
            'item_type__category__category_name',
            'item_type__type_name', 'units__units_name')


class ItemUnits(AbstractBase):
    """ItemUnits model."""

    item = models.ForeignKey(
        Item, null=False, blank=False, on_delete=CASCADE)
    sales_units = models.ForeignKey(
        Units, null=False, blank=False,
        related_name='selling_units', on_delete=PROTECT)  # eg Dozen
    purchases_units = models.ForeignKey(
        Units, null=False, blank=False,
        related_name='purchasing_units', on_delete=PROTECT)  # eg Pieces
    items_per_purchase_unit = models.FloatField()           # eg 12
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def clean(self) -> None:
        """Clean Item Units model."""
        return super().clean()


def get_directory(instance, filename):
    """Determine the upload path for a file."""
    return "{}/{}_{}".format(
        instance.created_on.strftime("%Y/%m/%d"), instance.id, filename)


class ItemImage(AbstractBase):
    """Item Image model."""

    item = models.ForeignKey(
        Item, null=False, blank=False, on_delete=CASCADE)
    image = models.ImageField(upload_to=get_directory)
    is_hero_image = models.BooleanField(default=False)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    # edit path item_image.image.path to use mediafiles folder
    # clean to check if no item image has been selected
    # set the first image to be the hero image

    def update_hero_product_image(self):
        """The newly selected image as the hero image will be the default hero image."""    # noqa
        if self.is_hero_image:  # check if its calid during test
            item_images = self.__class__.objects.filter(item=self.item)

            if item_images.exists():
                item_images.exclude(id=self.id).update(is_hero_image=False)

    def clean(self) -> None:
        """Clean the item image model."""
        return super().clean()

    def save(self, *args, **kwargs):
        """Perform post save and pre save actions."""
        super().save(*args, **kwargs)
        self.update_hero_product_image()
