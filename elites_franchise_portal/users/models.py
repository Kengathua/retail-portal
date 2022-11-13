"""The custom user model."""
import uuid

from typing import Any, Collection, Optional, Set, Tuple, Type, TypeVar, Union

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import (
    BaseUserManager, PermissionsMixin, AbstractBaseUser,
    PermissionManager, GroupManager, AnonymousUser)
from django.db.models.base import Model

_AnyUser = Union[Model, "AnonymousUser"]


class Role(models.Model):
    """Custom roles model."""

    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=300)
    value = models.CharField(max_length=300)


class Permission(models.Model):
    """Custom permissions model."""

    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=300)
    value = models.CharField(max_length=300)

    objects: PermissionManager


class Group(models.Model):
    """Custom groups model."""

    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True, auto_created=True)
    created_on = models.DateTimeField(
        db_index=True, editable=False, default=timezone.now)
    created_by = models.UUIDField(editable=False)
    updated_on = models.DateTimeField(db_index=True, default=timezone.now)
    updated_by = models.UUIDField()
    enterprise = models.CharField(null=False, blank=False, max_length=250)
    name = models.CharField(max_length=300)
    permissions = models.ManyToManyField(
        Permission, through='GroupPermission',
        related_name='group_permissions')

    objects: GroupManager


class GroupPermission(models.Model):
    """Group Permission Model."""

    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True, auto_created=True)
    created_on = models.DateTimeField(
        db_index=True, editable=False, default=timezone.now)
    created_by = models.UUIDField(editable=False)
    updated_on = models.DateTimeField(db_index=True, default=timezone.now)
    updated_by = models.UUIDField()
    enterprise = models.CharField(null=False, blank=False, max_length=250)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    permission = models.ForeignKey(Permission, on_delete=models.PROTECT)


class UserManager(BaseUserManager):
    """The user manager."""

    def create_user(self, email, password=None, **extra_fields):
        """Create a non Django (admin) superuser."""
        if not email:
            raise ValueError(_('Email address is required'))

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **fields):
        """Create and save user as a superuser."""
        user = self.create_user(email, password=password, first_name=first_name, last_name=last_name, **fields)    # noqa
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """The custom user model."""

    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    guid = models.UUIDField(unique=True)
    date_joined = models.DateTimeField(db_index=True, verbose_name='date joined', auto_now_add=True)    # noqa
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    first_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, blank=False, null=False)
    other_names = models.CharField(max_length=255, null=True, blank=True)
    phone_no = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(verbose_name='email address', null=False, blank=False, max_length=255, unique=True)   # noqa
    password = models.CharField(max_length=255, blank=False, null=False)
    date_of_birth = models.DateField(
        null=True, blank=True, default='1900-01-01')
    updated_on = models.DateTimeField(db_index=True, default=timezone.now)
    enterprise = models.CharField(max_length=250)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    roles = models.ManyToManyField(
        Role, through='UserRole', related_name='user_roles')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    @property
    def user_roles(self):
        """User roles string."""
        roles = set(UserRole.objects.filter(user=self).values_list('role__name', flat=True))
        return roles

    @property
    def user_permissions(self):
        """."""
        perms = []
        if self.group:
            perms = set(self.group.permissions.values_list('value', flat=True).order_by('-value'))
        return perms


    def get_full_name(self):
        """Format the user's full name."""
        return '{} {}'.format(self.first_name, self.last_name)

    def get_short_name(self):
        """Use the first name as a short name for the user."""
        return '{}'.format(self.first_name)

    def __str__(self):
        """Return user first name last name and email."""
        return "{} {} ({})".format(self.first_name, self.last_name, self.email)

    class Meta(object):
        """Sort alphabetically users by their first name, last name."""

        ordering = ('first_name', 'last_name',)


class UserRole(models.Model):
    """User Role model."""

    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)


def retrieve_user_email(id_field):
    """Retrieve a user's email given the userID."""
    @property
    def user_email(self):
        """Return a user email."""
        email = None
        id = getattr(self, id_field)
        if User.objects.filter(id=id).exists():
            email = User.objects.get(
                id=getattr(self, id_field)).email
        if User.objects.filter(guid=id).exists():
            email = User.objects.get(
                guid=getattr(self, id_field)).email

        return email
    return user_email
