from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractUser

class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Pass activation ?')
    send_messages = models.BooleanField(default=True, verbose_name='Send notifications ?')
    raiting = models.IntegerField(default=0, verbose_name='Rating')
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    class Meta(AbstractUser.Meta):
        pass

    def delete(self, *args, **kwargs):
        for ad in self.ad_set.all():
            ad.delete()
        super().delete(*args, **kwargs)

#Categories and Subcategories
class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, unique=True, verbose_name='Name')
    order = models.IntegerField(default=0, db_index=True, verbose_name='Order')
    parent = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True, related_name='children', verbose_name='Parent category')

class SuperCategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(parent__isnull=True)
    

class SuperCategory(Category):
    objects = SuperCategoryManager()
    
    def __str__(self):
        return self.name
    
    class Meta:
        proxy = True
        ordering = ('order', 'name')
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class SubCategoryManageer(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(parent__isnull=False)
    
class SubCategory(Category):
    objects = SubCategoryManageer()
    
    def __str__(self):
        return '%s - %s' % (self.parent.name, self.name)
    
    class Meta:
        proxy = True
        ordering = ('parent__order', 'parent__name', 'name', 'order')
        verbose_name = 'Subcategory'
        verbose_name_plural = 'Subcategories'

#Ads
from .utilities import get_timestamp_path
class Ad(models.Model):
    category = models.ForeignKey(SubCategory, on_delete=models.PROTECT, verbose_name='Category')
    title = models.CharField(max_length=100, verbose_name='Title')
    content = models.TextField(verbose_name='Content')
    price = models.FloatField(default=0, verbose_name='Price')
    contacts = models.TextField(verbose_name='Contacts')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='Image')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Author')
    is_preorder = models.BooleanField(default=True, db_index=True, verbose_name='Preorder')
    is_sold = models.BooleanField(default=True, db_index=False, verbose_name='Sold')
    is_active = models.BooleanField(default=True, db_index=False, verbose_name='Active')
    is_hold = models.BooleanField(default=True, db_index=False, verbose_name='On hold')
    #status = models.BooleanField(default=True, db_index=True, verbose_name='Sold')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Published')
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='Postal code')
    
    def save(self, *args, **kwargs):
        if self.is_active:
            self.is_sold = False
            self.is_hold = False
        elif self.is_sold:
            self.is_active = False
            self.is_hold = False
        elif self.is_hold:
            self.is_active = False
            self.is_sold = False
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Ad'
        verbose_name_plural = 'Ads'
        ordering = ['-created_at']

class AdditionalImage(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name='Ad')
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Image')

    class Meta:
        verbose_name = 'Additional image'
        verbose_name_plural = 'Additional images'
        ordering = ['id']


#Conversation
from django.db import models
from .models import Ad, AdvUser  # Імпортуємо AdvUser

class AdditionalImage(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name='Ad')
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Image')

    class Meta:
        verbose_name = 'Additional image'
        verbose_name_plural = 'Additional images'
        ordering = ['id']


# Conversation
class Conversation(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    seller = models.ForeignKey(AdvUser, related_name='seller_conversations', on_delete=models.CASCADE)
    buyer = models.ForeignKey(AdvUser, related_name='buyer_conversations', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation about {self.ad.title} between {self.seller.username} and {self.buyer.username}"

    def can_access(self, user):
        return user == self.seller or user == self.buyer

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(AdvUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"