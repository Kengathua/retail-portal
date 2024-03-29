"""Debit side item build up models."""

from django.db import models
from django.db.models import CASCADE, PROTECT
from django.core.exceptions import ValidationError

from elites_retail_portal.common.models import AbstractBase
from elites_retail_portal.common.code_generators import generate_enterprise_code
from elites_retail_portal.users.models import retrieve_user_email

ITEM_ATTRIBUTE_TYPES = (
    ('SPECIAL OFFER', 'SPECIAL OFFER'),
    ('WARRANTY', 'WARRANTY'),
    ('SPECIAL FEATURE', 'SPECIAL FEATURE'),
    ('SPECIFICATION', 'SPECIFICATION'),
    ('DESCRIPTION', 'DESCRIPTION')
)

UNITS_TYPES_CHOICES = (
    ("LITRES", "LITRES"),
    ("MILILITRES", "MILILITRES"),
    ("KILOGRAMS", "KILOGRAMS"),
    ("POUNDS", "POUNDS"),
    ("OUNCES", "OUNCES"),
    ("GRAMS", "GRAMS"),
    ("CARTONS", "CARTONS"),
    ("PACKETS", "PACKETS"),
    ("SACHETS", "SACHETS"),
    ("PIECES", "PIECES"),
    ("SACKS", "SACKS"),
    ("BALES", "BALES"),
    ("INCHES", "INCHES"),
    ("METRES", "METRES"),
    ("CENTIMETRES", "CENTIMETRES"),
    ("DOZENS", "DOZENS")
)

PIECES = "PIECES"

PRODUCT_STATUS_CHOICES = (
    ("SOLD", "SOLD"),
    ("ON SALE", "ON SALE"),
    ("RETURNED TO SUPPLIER", "RETURNED TO SUPPLIER"),
)

ON_SALE = "ON SALE"


class Category(AbstractBase):
    """Item categories eg. ELECTRONICS, UTENSILS, COOKER."""

    category_name = models.CharField(max_length=300)
    category_code = models.CharField(
        max_length=250, null=True, blank=True)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def create_category_code(self):
        """Create a code for the category."""
        if not self.category_code:
            self.category_code = generate_enterprise_code(self)

    def validate_unique_category_name(self):
        """Validate the category is unique for the business."""
        if self.__class__.objects.filter(
                category_name=self.category_name,
                enterprise=self.enterprise).exclude(id=self.id).exists():
            msg = 'A category with this category name already exists'
            raise ValidationError({'category': msg})

    def clean(self) -> None:
        """Clean the category."""
        self.validate_unique_category_name()
        return super().clean()

    def __str__(self):
        """Str representation for the section model."""
        return '{}'.format(self.category_name)

    def save(self, *args, **kwargs):
        """Pre save and post save action."""
        self.create_category_code()
        self.category_name = self.category_name.upper()
        return super().save(*args, **kwargs)

    class Meta:
        """Meta class for category."""

        ordering = ['category_name']


class ItemType(AbstractBase):
    """Item types eg.Fridge, Cooker, Microwave."""

    category = models.ForeignKey(
        Category, null=False, blank=False, on_delete=CASCADE)
    type_name = models.CharField(max_length=250)
    type_code = models.CharField(
        max_length=250, null=True, blank=True)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def create_type_code(self):
        """Create a code for the item type."""
        if not self.type_code:
            self.type_code = generate_enterprise_code(self)

    def validate_unique_type_name(self):
        """Validate unique type name."""
        if self.__class__.objects.filter(
                type_name=self.type_name, category=self.category,
                enterprise=self.enterprise).exclude(id=self.id).exists():
            msg = 'An item type with this type name already exists'
            raise ValidationError({'category': msg})

    def clean(self) -> None:
        """Clean the item type model."""
        self.validate_unique_type_name()
        return super().clean()

    def save(self, *args, **kwargs):
        """Perform presave and post save actions."""
        self.type_name = self.type_name.upper()
        self.create_type_code()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Str representation for the item-models model."""
        return '{} -> {}'.format(self.type_name, self.category.category_name)

    class Meta:
        """Meta class for section model."""

        ordering = ['-type_name']


class Brand(AbstractBase):
    """Item brand model for items eg. Samsung, LG, Sony."""

    item_types = models.ManyToManyField(
        ItemType, through='BrandItemType', related_name='branditemtypes')
    brand_name = models.CharField(max_length=250)
    brand_code = models.CharField(
        max_length=250, null=True, blank=True)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def create_brand_code(self):
        """Create a code for the brand."""
        if not self.brand_code:
            self.brand_code = generate_enterprise_code(self)

    def validate_unique_brand_name(self):
        """Validate the brand name is unique for the business."""
        if self.__class__.objects.filter(
                brand_name=self.brand_name,
                enterprise=self.enterprise).exclude(id=self.id).exists():
            msg = 'A brand with this brand name already exists'
            raise ValidationError({'brand_name': msg})

    def clean(self) -> None:
        """Clean the brand model."""
        self.validate_unique_brand_name()
        return super().clean()

    def save(self, *args, **kwargs):
        """Pre save and post save actions."""
        self.brand_name = self.brand_name.upper()
        self.create_brand_code()
        return super().save(*args, **kwargs)

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

    def validate_unique_brand_and_item_type(self):
        """Validate unique brand and item type."""
        if self.__class__.objects.filter(
                brand=self.brand,
                item_type=self.item_type).exclude(id=self.id).exists():
            msg = 'The item type {} is already hooked up to the brand {}'.format(
                self.item_type.type_name, self.brand.brand_name)
            raise ValidationError({'brand_item_type': msg})

    def clean(self) -> None:
        """Clean brand item type."""
        self.validate_unique_brand_and_item_type()
        return super().clean()

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
        max_length=250, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    @property
    def heading(self):
        """Get the model heading."""
        model_name = self.model_name
        brand_name = self.brand.brand_name
        type_name = self.item_type.type_name
        return f'{model_name} {brand_name} {type_name}'

    def check_item_type_is_hooked_up_to_the_brand(self):
        """Validate the item type is hooked to the brand."""
        if not BrandItemType.objects.filter(
                brand=self.brand, item_type=self.item_type, enterprise=self.enterprise).exists():
            BrandItemType.objects.create(
                brand=self.brand, item_type=self.item_type, created_by=self.created_by,
                updated_by=self.updated_by, enterprise=self.enterprise)

    def validate_unique_model_name(self):
        """Validate that the model name is uniques for the enterprise."""
        if self.__class__.objects.filter(
                model_name=self.model_name,
                brand=self.brand, item_type=self.item_type,
                enterprise=self.enterprise).exclude(id=self.id).exists():
            msg = 'The {} {} {} model number already exists. '\
                'Please enter a new model number'.format(
                    self.model_name, self.brand.brand_name, self.item_type.type_name)
            raise ValidationError({"model_name": msg})

    def create_model_code(self):
        """Create a code for the item model."""
        if not self.model_code:
            self.model_code = generate_enterprise_code(self)

    def clean(self) -> None:
        """Clean the ItemModel model."""
        self.validate_unique_model_name()
        return super().clean()

    def save(self, *args, **kwargs):
        """Perform pre save and post save actions."""
        self.create_model_code()
        self.check_item_type_is_hooked_up_to_the_brand()
        return super().save(*args, **kwargs)

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
        null=True, blank=True, max_length=250)
    item_name = models.CharField(
        null=True, blank=True, max_length=250)
    item_code = models.CharField(
        null=True, blank=True, max_length=250)
    make_year = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    pushed_to_edi = models.BooleanField(default=False)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def validate_active_item_has_units(self):
        """Validate active item has units assigned to it."""
        if self.is_active:
            if not ItemUnits.objects.filter(item=self, is_active=True).exists():
                msg = '{} does not have Units assigned to it. ' \
                    'Please hook that up first'.format(
                        self.item_name)

                raise ValidationError(
                    {'item_units': msg})

    def get_item_name(self):
        """Get the item's name."""
        type = self.item_model.item_type.type_name
        brand = self.item_model.brand.brand_name
        model = self.item_model.model_name
        self.item_name = brand + ' ' + model + ' ' + type

    def create_item_code(self):
        """Create a code for the item."""
        if not self.item_code:
            self.item_code = generate_enterprise_code(self)

    def clean(self) -> None:
        """Clean the item model."""
        self.validate_active_item_has_units()
        self.get_item_name()
        self.create_item_code()
        return super().clean()

    def __str__(self):
        """Str representation for item model."""
        return f'{self.item_name}'

    def activate(self, user=None):
        """Activate a product by setting it up in inventory and catalog."""
        from elites_retail_portal.catalog.models import CatalogItem, CatalogCatalogItem
        from elites_retail_portal.enterprise_mgt.helpers import (
            get_valid_enterprise_setup_rules)
        from elites_retail_portal.items.helpers import (
            activate_warehouse_item, activate_inventory_item)

        enterprise_setup_rules = get_valid_enterprise_setup_rules(self.enterprise)
        if not enterprise_setup_rules:
            msg = 'You do not have rules for your enterprise. Please set that up first'
            raise ValidationError({'enterprise_setup_rules': msg})

        audit_fields = {
            'created_by': user.id if user else self.created_by,
            'updated_by': user.id if user else self.updated_by,
            'enterprise': user.enterprise if user else self.enterprise,
        }

        inventories = enterprise_setup_rules.inventories.all()
        activate_inventory_item(self, audit_fields, inventories)

        warehouses = enterprise_setup_rules.warehouses.all()
        activate_warehouse_item(self, audit_fields, warehouses)

        catalog_item = CatalogItem.objects.filter(
            inventory_item__item=self, is_active=True).first()
        if catalog_item:
            catalog = enterprise_setup_rules.standard_catalog
            if not CatalogCatalogItem.objects.filter(
                    catalog=catalog, catalog_item=catalog_item).exists():
                CatalogCatalogItem.objects.create(
                    catalog=catalog, catalog_item=catalog_item, **audit_fields)

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
        return super().clean()

    class Meta:
        """Meta class for Item attributes."""

        ordering = ['-attribute_type', '-attribute_value']


class Units(AbstractBase):
    """Units mode."""

    item_types = models.ManyToManyField(
        ItemType, through='UnitsItemType', related_name='itemtype')  # eg. TV, Fridge
    units_name = models.CharField(
        null=True, blank=True, max_length=300)
    units_type = models.CharField(
        null=False, blank=False, max_length=300, choices=UNITS_TYPES_CHOICES, default=PIECES)
    units_quantity = models.FloatField(null=True, blank=True, default=1)
    units_code = models.CharField(
        null=True, blank=True, max_length=250)
    is_active = models.BooleanField(default=True)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def create_units_code(self):
        """Create a code for the units."""
        if not self.units_code:
            self.units_code = generate_enterprise_code(self)

    def get_units_name(self):
        """Get units name."""
        if not self.units_name:
            self.units_name = "{} {}".format(self.units_quantity, self.units_type)
            if self.units_quantity == 1:
                self.units_name = self.units_type

    def validate_unique_units_name(self):
        """Validate the created units is unique."""
        if self.__class__.objects.filter(
                units_name=self.units_name, is_active=True,
                enterprise=self.enterprise).exclude(id=self.id).exists():
            msg = "Units with this units name already exists. "\
                "Please enter new units or edit the existing record"
            raise ValidationError({"units": msg})

    def clean(self) -> None:
        """Clean the units model."""
        self.validate_unique_units_name()
        return super().clean()

    def __str__(self):
        """Str representation for the item-models model."""
        item_types = self.item_types.all()
        type_names = [item_type.type_name for item_type in item_types]
        return '{} -> {}'.format(
            self.units_name,
            ", ".join(type_names),)

    def save(self, *args, **kwargs):
        """Post save and pre save actions."""
        self.units_quantity = self.units_quantity or 1
        self.get_units_name()
        self.create_units_code()
        return super().save(*args, **kwargs)

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
            self.item_type.type_name)

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
    quantity_of_sale_units_per_purchase_unit = models.FloatField(default=1)  # eg 12
    is_active = models.BooleanField(default=True)
    creator = retrieve_user_email('created_by')
    updater = retrieve_user_email('updated_by')

    def validate_unique_active_item_units_for_item(self):
        """Vaidate item units are unique for the item."""
        if self.__class__.objects.filter(
                item=self.item, is_active=True).exclude(id=self.id).exists():
            raise ValidationError(
                {'item': 'This item already has an active units instance registered to it. '
                    'Kindly deactivate the existing units registered to it or '
                    'select a different item'})

    def validate_selected_units_are_active(self):
        """Validate that the unit used are active."""
        if not self.sales_units.is_active:
            units_name = self.sales_units.units_name
            raise ValidationError(
                {'sales_units': 'Sales Units {} has been deactivated. '
                 'Kindly activate it or select the correct units to register'.format(
                     units_name)})

        if not self.purchases_units.is_active:
            units_name = self.purchases_units.units_name
            raise ValidationError(
                {'purchases_units': 'Purchases Units {} has been deactivated. '
                 'Kindly activate it or select the correct units to register'.format(
                     units_name)})

    def clean(self) -> None:
        """Clean Item Units model."""
        self.validate_unique_active_item_units_for_item()
        self.validate_selected_units_are_active()
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


class Product(AbstractBase):
    """Products model."""

    item = models.ForeignKey(
        Item, null=False, blank=False, on_delete=CASCADE)
    serial_number = models.CharField(max_length=300, null=True, blank=True)
    product_name = models.CharField(max_length=300, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=300, null=True, blank=True, choices=PRODUCT_STATUS_CHOICES, default=ON_SALE)

    @property
    def catalog_item(self):
        """Get catalog item."""
        from elites_retail_portal.catalog.models import CatalogItem
        return CatalogItem.objects.filter(inventory_item__item=self.item).first()

    def validate_unique_serial_number(self):
        """Validate unique serial number."""
        if not self.serial_number:
            return

        if self.__class__.objects.filter(
                serial_number=self.serial_number,
                enterprise=self.enterprise).exclude(id=self.id).exists():
            msg = "A product with this serial number already exists. Please query that to proceed"
            raise ValidationError({'serial_number': msg})

    def validate_serial_number(self):
        """Validate serial numbers."""
        if not self.serial_number:
            msg = "Please provide a valid serial number"
            raise ValidationError({'serial_number': msg})

    def clean(self) -> None:
        """Clean products model."""
        self.validate_unique_serial_number()
        return super().clean()

    def save(self, *args, **kwargs):
        """Save action."""
        if not self.product_name:
            self.product_name = self.item.item_name

        return super().save(*args, **kwargs)
