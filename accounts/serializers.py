"""
accounts/serializers.py - DRF serializers for accounts
"""
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from accounts.models import UserProfile, Address, UserActivity, Wishlist


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'date_of_birth', 'avatar', 'bio',
            'is_verified', 'date_joined'
        )
        read_only_fields = ('id', 'email', 'date_joined', 'is_verified')

    def get_full_name(self, obj):
        return force_text(obj.get_full_name())


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ('email', 'first_name', 'last_name', 'password', 'confirm_password')

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {'confirm_password': force_text(_('Passwords do not match'))}
            )
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = UserProfile.objects.create_user(**validated_data)
        return user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            'id', 'address_type', 'street_address', 'apartment',
            'city', 'state', 'country', 'zip_code', 'is_default', 'created_at'
        )
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        user = self.context['request'].user
        # If this is set as default, unset all other defaults
        if validated_data.get('is_default'):
            Address.objects.filter(
                user=user,
                address_type=validated_data['address_type']
            ).update(is_default=False)
        return super(AddressSerializer, self).create(validated_data)


class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = ('id', 'action', 'ip_address', 'timestamp', 'metadata')
        read_only_fields = fields


class UserPublicSerializer(serializers.ModelSerializer):
    """Minimal public user info for use in other apps."""
    class Meta:
        model = UserProfile
        fields = ('id', 'first_name', 'last_name', 'avatar')
