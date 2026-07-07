from django.contrib import admin

from .models import (
	AuthenticationChallenge,
	AuthenticationFactor,
	AuthenticationSession,
	AuditLog,
	BiometricTemplate,
	Identity,
	IdentityKeyPair,
	IdentityVerification,
	PairingSession,
	PermissionRole,
	Session,
	User,
	UserDevice,
	UserRole,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ('username', 'email', 'is_verified', 'is_mfa_enabled', 'is_active', 'created_at')
	search_fields = ('username', 'email', 'phone_number')
	list_filter = ('is_verified', 'is_mfa_enabled', 'is_active', 'is_staff', 'is_superuser')
	ordering = ('-created_at',)


@admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
	list_display = ('display_name', 'user', 'identity_type', 'is_verified', 'verification_level', 'created_at')
	search_fields = ('display_name', 'unique_identifier', 'user__username', 'user__email')
	list_filter = ('identity_type', 'is_verified', 'verification_level')
	raw_id_fields = ('user',)


@admin.register(IdentityKeyPair)
class IdentityKeyPairAdmin(admin.ModelAdmin):
	list_display = ('user', 'key_algorithm', 'is_active', 'created_at', 'rotated_at')
	search_fields = ('user__username', 'key_fingerprint')
	list_filter = ('key_algorithm', 'is_active')
	raw_id_fields = ('user',)


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
	list_display = ('device_name', 'user', 'platform', 'trust_level', 'is_trusted', 'is_active', 'last_seen_at')
	search_fields = ('device_name', 'device_identifier', 'user__username', 'user__email')
	list_filter = ('platform', 'trust_level', 'is_trusted', 'is_active')
	raw_id_fields = ('user',)


@admin.register(PairingSession)
class PairingSessionAdmin(admin.ModelAdmin):
	list_display = ('session_token', 'user', 'status', 'requested_device_name', 'expires_at', 'completed_at')
	search_fields = ('session_token', 'user__username', 'user__email', 'requested_device_name')
	list_filter = ('status',)
	raw_id_fields = ('user', 'paired_device')


@admin.register(AuthenticationChallenge)
class AuthenticationChallengeAdmin(admin.ModelAdmin):
	list_display = ('challenge_token', 'user', 'challenge_type', 'status', 'expires_at', 'verified_at')
	search_fields = ('challenge_token', 'user__username', 'user__email')
	list_filter = ('challenge_type', 'status')
	raw_id_fields = ('user', 'device', 'pairing_session')


@admin.register(AuthenticationSession)
class AuthenticationSessionAdmin(admin.ModelAdmin):
	list_display = ('session_token', 'user', 'status', 'ip_address', 'expires_at', 'last_activity')
	search_fields = ('session_token', 'user__username', 'user__email', 'ip_address')
	list_filter = ('status', 'is_mfa_verified')
	raw_id_fields = ('user', 'device', 'challenge')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
	list_display = ('session_token', 'user', 'status', 'ip_address', 'expires_at', 'last_activity')
	search_fields = ('session_token', 'user__username', 'user__email', 'ip_address')
	list_filter = ('status', 'is_mfa_verified')
	raw_id_fields = ('user',)


@admin.register(BiometricTemplate)
class BiometricTemplateAdmin(admin.ModelAdmin):
	list_display = ('user', 'biometric_type', 'is_primary', 'is_active', 'quality_score', 'created_at')
	search_fields = ('user__username', 'user__email', 'template_hash')
	list_filter = ('biometric_type', 'is_primary', 'is_active')
	raw_id_fields = ('user',)


@admin.register(AuthenticationFactor)
class AuthenticationFactorAdmin(admin.ModelAdmin):
	list_display = ('user', 'factor_type', 'is_verified', 'is_active', 'created_at')
	search_fields = ('user__username', 'user__email', 'factor_type')
	list_filter = ('factor_type', 'is_verified', 'is_active')
	raw_id_fields = ('user',)


@admin.register(IdentityVerification)
class IdentityVerificationAdmin(admin.ModelAdmin):
	list_display = ('user', 'verification_type', 'status', 'attempts', 'expires_at', 'completed_at')
	search_fields = ('user__username', 'user__email', 'verification_code')
	list_filter = ('verification_type', 'status')
	raw_id_fields = ('user',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
	list_display = ('category', 'action', 'status', 'user', 'created_at')
	search_fields = ('action', 'user__username', 'user__email', 'error_message')
	list_filter = ('category', 'status')
	raw_id_fields = ('user',)


@admin.register(PermissionRole)
class PermissionRoleAdmin(admin.ModelAdmin):
	list_display = ('name', 'is_system_role', 'created_at', 'updated_at')
	search_fields = ('name',)
	list_filter = ('is_system_role',)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
	list_display = ('user', 'role', 'assigned_by', 'assigned_at', 'expires_at')
	search_fields = ('user__username', 'user__email', 'role__name')
	list_filter = ('role',)
	raw_id_fields = ('user', 'role', 'assigned_by')