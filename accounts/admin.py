"""
accounts/admin.py - Admin configuration for accounts
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from accounts.models import UserProfile, Address, UserActivity, Wishlist
from accounts.forms import UserRegistrationForm, UserProfileForm


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ('address_type', 'street_address', 'city', 'country', 'is_default')


class UserActivityInline(admin.TabularInline):
    model = UserActivity
    extra = 0
    readonly_fields = ('action', 'ip_address', 'timestamp')
    max_num = 10


@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    add_form = UserRegistrationForm
    form = UserProfileForm
    model = UserProfile
    list_display = ('email', 'first_name', 'last_name', 'is_verified', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_verified', 'date_joined')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'bio', 'avatar')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    inlines = [AddressInline, UserActivityInline]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_type', 'city', 'country', 'is_default')
    list_filter = ('address_type', 'country', 'is_default')
    search_fields = ('user__email', 'city', 'country')
    raw_id_fields = ('user',)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__email', 'action')
    readonly_fields = ('user', 'action', 'ip_address', 'user_agent', 'timestamp', 'metadata')
    ordering = ('-timestamp',)
