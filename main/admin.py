from django.contrib import admin
import datetime

from .models import AdvUser
from .utilities import send_activation_notification
from .models import SuperCategory, SubCategory
from .forms import SubCategoryForm
from .models import Ad, AdditionalImage
from django import forms
from .widgets import StatusSelectWidget
from django.utils.html import format_html
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
class SubCategoryInline(admin.TabularInline):
    model = SubCategory
class SuperCategoryAdmin(admin.ModelAdmin):
    exclude = ('parent',)
    inlines = (SubCategoryInline,)
admin.site.register(SuperCategory, SuperCategoryAdmin)
class SubCategoryAdmin(admin.ModelAdmin):
    form = SubCategoryForm
admin.site.register(SubCategory, SubCategoryAdmin)

#Ads
class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage

class AdAdminForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=[
            ('is_active', 'Active'),
            ('is_sold', 'Sold'),
            ('is_hold', 'On hold')
        ],
        widget=StatusSelectWidget(),
        required=False
    )

    class Meta:
        model = Ad
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        if status:
            cleaned_data['is_active'] = (status == 'is_active')
            cleaned_data['is_sold'] = (status == 'is_sold')
            cleaned_data['is_hold'] = (status == 'is_hold')
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        status = self.cleaned_data.get('status')
        if status:
            instance.is_active = (status == 'is_active')
            instance.is_sold = (status == 'is_sold')
            instance.is_hold = (status == 'is_hold')
        if commit:
            instance.save()
        return instance
class AdAdmin(admin.ModelAdmin):
    form = AdAdminForm
    list_display = ('category', 'title','status_display', 'content', 'author', 'created_at', 'price', 'postal_code', 'created_at')
    fields = (('category', 'author'), 'title', 'status', 'content', 'price', 'postal_code', 'contacts', 'image')
    inlines = (AdditionalImageInline,)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            if obj.is_active:
                form.base_fields['status'].initial = 'is_active'
            elif obj.is_sold:
                form.base_fields['status'].initial = 'is_sold'
            elif obj.is_hold:
                form.base_fields['status'].initial = 'is_hold'
        return form
    
    def status_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">{}</span>', 'Active')
        elif obj.is_sold:
            return format_html('<span style="color: red;">{}</span>', 'Sold')
        elif obj.is_hold:
            return format_html('<span style="color: orange;">{}</span>', 'On hold')
        return format_html('<span style="color: gray;">{}</span>', 'Unknown')
    status_display.short_description = 'Status'
admin.site.register(Ad, AdAdmin)


