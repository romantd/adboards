from django.contrib import admin
import datetime

from .models import AdvUser
from .utilities import send_activation_notification

def send_activation_notifications(modeladmin, request, queryset):
    for rec in queryset:
        if not rec.is_activated:
            send_activation_notification(rec)
    modeladmin.message_user(request, 'Activation emails sent')
send_activation_notifications.short_description = 'Send activation emails'

class NonactivatedFilter(admin.SimpleListFilter):
    title = 'Pass activation ?'
    parameter_name = 'actstate'
    
    def lookups(self, request, model_admin):
        return (
            ('activated', 'Activated'),
            ('threedays', 'Not pass withing 3 days'),
            ('week', 'Not pass withing a week'),
        )
    
    def queryset(self, request, queryset):
        val = self.value()
        if val == 'activated':
            return queryset.filter(is_active=True, is_activated=True)
        elif val == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)
        elif val == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_activee=True, is_activated=False, date_joined__date__lt=d)
        
class AdvUserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_activated', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = (NonactivatedFilter,)
    fields = (('username', 'email'), ('first_name', 'last_name'), ('send_messages', 'is_active', 'is_activated'), ('is_staff', 'is_superuser'), 'groups', 'user_permissions', 'last_login', 'date_joined',  'raiting', 'postal_code')
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notifications,)


admin.site.register(AdvUser, AdvUserAdmin)

#Cateegories
from .models import SuperCategory, SubCategory
class SubCategoryInline(admin.TabularInline):
    model = SubCategory
class SuperCategoryAdmin(admin.ModelAdmin):
    exclude = ('parent',)
    inlines = (SubCategoryInline,)
admin.site.register(SuperCategory, SuperCategoryAdmin)

from .forms import SubCategoryForm
class SubCategoryAdmin(admin.ModelAdmin):
    form = SubCategoryForm
admin.site.register(SubCategory, SubCategoryAdmin)

#Ads
from .models import Ad, AdditionalImage
class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage

class AdAdmin(admin.ModelAdmin):
    list_display = ('category', 'title', 'content', 'author', 'created_at', 'price', 'postal_code','created_at')
    fields = (('category', 'author'), 'title', 'content', 'price', 'postal_code', 'contacts', 'image', 'is_active')
    inlines = (AdditionalImageInline,)

admin.site.register(Ad, AdAdmin)