from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.sites.models import Site
from django.conf import settings
from .base32 import base32_encode
from .middleware import _thread_locals

User = settings.AUTH_USER_MODEL
CREATED_BY_RELATED_NAME = '%(app_label)s_%(class)s_created_by'


class SoftDeletableManager(models.Manager):
    """
    Manager that filters out soft-deleted records by default.
    """

    def get_queryset(self):
        """
        Override the default queryset to exclude soft-deleted records.
        """
        return super().get_queryset().filter(deleted_at__isnull=True)


class AllObjectsManager(models.Manager):
    """
    Manager that includes soft-deleted records.
    """

    def get_queryset(self):
        """
        Get the default queryset without any additional filtering.
        """
        return super().get_queryset()


class _BaseAbstract(models.Model):
    site = models.ForeignKey(Site, related_name="%(app_label)s_%(class)s_site",
                             blank=True, null=True, on_delete=models.CASCADE,)
    nonce = models.CharField(max_length=128, blank=True, null=True)
    id32 = models.CharField(
        max_length=100,
        db_index=True,
        blank=True,
        null=True)

    created_at = models.DateTimeField(db_index=True)
    created_at_timestamp = models.PositiveIntegerField(db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name=CREATED_BY_RELATED_NAME)

    owned_at = models.DateTimeField(db_index=True, blank=True, null=True)
    owned_at_timestamp = models.PositiveIntegerField(
        db_index=True, blank=True, null=True)
    owned_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE,
                                 related_name="%(app_label)s_%(class)s_owner")

    updated_at = models.DateTimeField(db_index=True, blank=True, null=True)
    updated_at_timestamp = models.PositiveIntegerField(
        db_index=True, blank=True, null=True)
    updated_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE,
                                   related_name="%(app_label)s_%(class)s_updated_by")

    published_at = models.DateTimeField(blank=True, null=True)
    published_at_timestamp = models.PositiveIntegerField(
        db_index=True, blank=True, null=True)
    published_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE,
                                     related_name="%(app_label)s_%(class)s_published_by")

    unpublished_at = models.DateTimeField(blank=True, null=True)
    unpublished_at_timestamp = models.PositiveIntegerField(
        db_index=True, blank=True, null=True)
    unpublished_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE,
                                       related_name="%(app_label)s_%(class)s_unpublished_by")

    approved_at = models.DateTimeField(blank=True, null=True)
    approved_at_timestamp = models.PositiveIntegerField(
        db_index=True, blank=True, null=True)
    approved_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE,
                                    related_name="%(app_label)s_%(class)s_approved_by")

    unapproved_at = models.DateTimeField(blank=True, null=True)
    unapproved_at_timestamp = models.PositiveIntegerField(
        db_index=True, blank=True, null=True)
    unapproved_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE,
                                      related_name="%(app_label)s_%(class)s_unapproved_by")

    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_at_timestamp = models.PositiveIntegerField(
        db_index=True, blank=True, null=True)
    deleted_by = models.ForeignKey(User, db_index=True, blank=True,
                                   null=True, on_delete=models.CASCADE,
                                   related_name="%(app_label)s_%(class)s_deleted_by")

    # Add the custom manager
    objects = SoftDeletableManager()
    all_objects = AllObjectsManager()

    @property
    def _current_user(self):
        """Retrieve the current user from thread-local storage."""
        return getattr(_thread_locals, 'user', None)

    # =========================
    # Helper Methods
    # =========================
    def _set_timestamp(self, field_name):
        now = timezone.now()
        setattr(self, field_name, now)
        setattr(self, f"{field_name}_timestamp", int(now.timestamp()))

    def _set_user_action(self, action, user):
        if user:
            self._set_timestamp(f"{action}_at")
            setattr(self, f"{action}_by", user)

    def _nullify_user_action(self, action):
        setattr(self, f"{action}_at", None)
        setattr(self, f"{action}_at_timestamp", None)
        setattr(self, f"{action}_by", None)

    # =========================
    # Main Methods
    # =========================
    def save(self, *args, **kwargs):
        """Overwrite the save method to incorporate custom logic."""
        if self.created_at is None:
            self._set_user_action('created', self._current_user)

        if not self.site:
            self.site = Site.objects.get_current()

        self._set_user_action('updated', self._current_user)

        if not self.id32:
            prev = self.__class__.all_objects.last()
            obj_id = prev.id + 1 if prev else 1
            self.id32 = base32_encode(obj_id)

        super(_BaseAbstract, self).save(*args, **kwargs)

    def approve(self, user=None):
        self._set_user_action(
            'approved',  user if user else self._current_user)
        self._nullify_user_action('unapproved')
        self.save()

    def unapprove(self, user=None):
        self._set_user_action(
            'unapproved',  user if user else self._current_user)
        self._nullify_user_action('approved')
        self.save()

    def reject(self, user=None):
        self.unapprove(user)

    def publish(self, user=None):
        self._set_user_action(
            'published', user if user else self._current_user)
        self._nullify_user_action('unpublished')
        self.save()

    def unpublish(self, user=None):
        self._set_user_action(
            'unpublished', user if user else self._current_user)
        self._nullify_user_action('published')
        self.save()

        # Soft delete method
    def delete(self, user=None, *args, **kwargs):
        """
        Overridden delete method to perform a soft delete. Instead of removing 
        the instance from the database, it sets deleted_at and deleted_by fields.
        """
        # Mark when the record was deleted
        self._set_user_action('deleted', user if user else self._current_user)

        # Instead of hard deleting the record, we update the fields
        self.save()

    def permanent_delete(self, *args, **kwargs):
        super(_BaseAbstract, self).delete(*args, **kwargs)

    def undelete(self, user=None):
        self._nullify_user_action('deleted')
        self._set_user_action('updated', user if user else self._current_user)
        self.save()

    # =========================
    # Property Methods
    # =========================
    @property
    def creator(self):
        return self.created_by

    @property
    def owner(self):
        return self.owned_by
    
    @property
    def approval(self):
        if self.approved_at:
            return 'approved'
        elif self.unapproved_at:
            return 'rejected'
        else:
            return 'requested'

    # ... Add other property methods

    # =========================
    # Status Method
    # =========================
    def get_status(self):
        if not self.approved_by and self.unapproved_by:
            approve_message = "REJECTED"
        elif self.approved_by and not self.unapproved_by:
            approve_message = "APPROVED"
        else:
            approve_message = "waiting to be approved"

        if not self.published_by and self.unpublished_by:
            publish_message = "UNPUBLISHED"
        elif self.published_by and not self.unpublished_by:
            publish_message = "PUBLISHED"
        else:
            publish_message = "waiting to be published"

        return f"Approval status: ({approve_message}), Publish status: ({publish_message})"

    class Meta:
        abstract = True


class BaseModelGeneric(_BaseAbstract):
    created_by = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE,
                                   related_name=CREATED_BY_RELATED_NAME)

    class Meta:
        abstract = True


class BaseModelUnique(_BaseAbstract):
    created_by = models.OneToOneField(User, db_index=True, on_delete=models.CASCADE,
                                      related_name=CREATED_BY_RELATED_NAME)

    class Meta:
        abstract = True


class NonceObject(object):
    """
    Utility object for models using nonce for retrieval or creation.

    Initialize with a model and nonce. If an object with that nonce exists,
    it's retrieved, otherwise a new object (without saving) is created.
    """

    def __init__(self, *args, **kwargs):
        self.MODEL = kwargs.get("model")
        self.NONCE = kwargs.get("nonce")
        obj = self.MODEL.objects.filter(
            nonce=self.NONCE).first() or self.MODEL(nonce=self.NONCE)
        self.OBJ = obj

    def get_object(self):
        """Return the associated model object."""
        return self.OBJ

    def is_exist(self):
        """Check if the associated model object exists in the database."""
        return bool(self.OBJ.id)
