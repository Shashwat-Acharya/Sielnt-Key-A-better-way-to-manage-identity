from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, URLValidator
from django.utils import timezone
import uuid


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser for identity management.
    Stores core user information and identity credentials.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False, help_text="Email verification status")
    is_mfa_enabled = models.BooleanField(default=False, help_text="Multi-factor authentication enabled")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.username} ({self.email})"


class BiometricTemplate(models.Model):
    """
    Stores biometric template data for users (fingerprint, facial recognition, etc.).
    Linked to C++ biometric_template_parsing module for template processing.
    """
    BIOMETRIC_TYPES = [
        ('FINGERPRINT', 'Fingerprint'),
        ('FACIAL', 'Facial Recognition'),
        ('IRIS', 'Iris Scan'),
        ('VOICE', 'Voice Recognition'),
        ('PALM', 'Palm Vein'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='biometric_templates')
    biometric_type = models.CharField(max_length=20, choices=BIOMETRIC_TYPES, db_index=True)
    template_data = models.BinaryField(help_text="Encrypted biometric template blob")
    template_hash = models.CharField(max_length=256, unique=True, help_text="SHA-256 hash for duplicate detection")
    is_primary = models.BooleanField(default=False, help_text="Primary biometric for authentication")
    quality_score = models.FloatField(
        default=0.0,
        validators=[],
        help_text="Biometric template quality score (0-100)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'biometric_templates'
        verbose_name = 'Biometric Template'
        verbose_name_plural = 'Biometric Templates'
        unique_together = [('user', 'template_hash')]
        indexes = [
            models.Index(fields=['user', 'biometric_type']),
            models.Index(fields=['template_hash']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.biometric_type}"


class AuthenticationFactor(models.Model):
    """
    Stores multi-factor authentication credentials for users.
    Supports various MFA methods: TOTP, SMS, email, backup codes, etc.
    """
    FACTOR_TYPES = [
        ('TOTP', 'Time-based OTP (Authenticator App)'),
        ('SMS', 'SMS OTP'),
        ('EMAIL', 'Email OTP'),
        ('BACKUP_CODE', 'Backup Recovery Codes'),
        ('SECURITY_KEY', 'FIDO2 Security Key'),
        ('BIOMETRIC', 'Biometric Authentication'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_factors')
    factor_type = models.CharField(max_length=20, choices=FACTOR_TYPES, db_index=True)
    secret_key = models.CharField(max_length=255, help_text="Encrypted OTP secret or credential")
    is_verified = models.BooleanField(default=False, help_text="Verification status of this factor")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    last_used = models.DateTimeField(null=True, blank=True)
    backup_data = models.JSONField(default=dict, blank=True, help_text="Backup codes or recovery data")

    class Meta:
        db_table = 'authentication_factors'
        verbose_name = 'Authentication Factor'
        verbose_name_plural = 'Authentication Factors'
        unique_together = [('user', 'factor_type', 'secret_key')]
        indexes = [
            models.Index(fields=['user', 'factor_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.factor_type}"


class Session(models.Model):
    """
    Manages user sessions for tracking active logins and session security.
    Supports session invalidation, timeout, and device tracking.
    """
    SESSION_STATUS = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('REVOKED', 'Revoked'),
        ('INVALID', 'Invalid'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_token = models.CharField(max_length=255, unique=True, db_index=True)
    refresh_token = models.CharField(max_length=255, unique=True, null=True, blank=True)
    device_fingerprint = models.CharField(max_length=256, blank=True, help_text="Device identifier hash")
    ip_address = models.GenericIPAddressField(db_index=True)
    user_agent = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='ACTIVE', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_mfa_verified = models.BooleanField(default=False, help_text="Whether MFA was completed for this session")

    class Meta:
        db_table = 'sessions'
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['session_token']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.id}"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def revoke(self):
        self.status = 'REVOKED'
        self.revoked_at = timezone.now()
        self.save(update_fields=['status', 'revoked_at'])


class Identity(models.Model):
    """
    Represents a verified digital identity with associated credentials and metadata.
    Supports multiple identity types and federation with external providers.
    """
    IDENTITY_TYPES = [
        ('INTERNAL', 'Internal Identity'),
        ('FEDERATED', 'Federated Identity'),
        ('OAUTH', 'OAuth Provider'),
        ('SAML', 'SAML Provider'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='identity')
    identity_type = models.CharField(max_length=20, choices=IDENTITY_TYPES, default='INTERNAL')
    unique_identifier = models.CharField(max_length=255, unique=True, db_index=True)
    display_name = models.CharField(max_length=255)
    avatar_url = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False, help_text="Identity verification status")
    verification_level = models.IntegerField(
        default=0,
        choices=[(0, 'Unverified'), (1, 'Email Verified'), (2, 'Phone Verified'), (3, 'Full Verification')],
        help_text="Trust level of identity verification"
    )
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional identity attributes")
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'identities'
        verbose_name = 'Identity'
        verbose_name_plural = 'Identities'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['unique_identifier']),
        ]

    def __str__(self):
        return f"{self.display_name} ({self.identity_type})"


class IdentityVerification(models.Model):
    """
    Tracks identity verification attempts, challenges, and proof collection.
    Manages email verification, phone verification, and document verification workflows.
    """
    VERIFICATION_TYPES = [
        ('EMAIL', 'Email Verification'),
        ('PHONE', 'Phone Verification'),
        ('DOCUMENT', 'Document Verification'),
        ('BIOMETRIC', 'Biometric Verification'),
    ]

    VERIFICATION_STATUS = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('EXPIRED', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_attempts')
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPES, db_index=True)
    status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='PENDING', db_index=True)
    verification_code = models.CharField(max_length=255, db_index=True, unique=True)
    challenge_data = models.JSONField(default=dict, help_text="Challenge details (email, phone, etc.)")
    proof_data = models.JSONField(default=dict, blank=True, help_text="User's proof submission")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(default=0, help_text="Number of verification attempts")
    max_attempts = models.IntegerField(default=3)
    failure_reason = models.TextField(blank=True)

    class Meta:
        db_table = 'identity_verifications'
        verbose_name = 'Identity Verification'
        verbose_name_plural = 'Identity Verifications'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['verification_code']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.verification_type} ({self.status})"

    def is_expired(self):
        return timezone.now() > self.expires_at


class AuditLog(models.Model):
    """
    Comprehensive audit logging for identity management events.
    Tracks all authentication, verification, and identity changes for compliance.
    """
    LOG_CATEGORIES = [
        ('LOGIN', 'Login Event'),
        ('LOGOUT', 'Logout Event'),
        ('MFA', 'MFA Event'),
        ('VERIFICATION', 'Verification Event'),
        ('IDENTITY_CHANGE', 'Identity Change'),
        ('PERMISSION_CHANGE', 'Permission Change'),
        ('BIOMETRIC', 'Biometric Event'),
        ('SESSION', 'Session Event'),
        ('SECURITY', 'Security Event'),
        ('ERROR', 'Error Event'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        help_text="User involved in the event (null for system events)"
    )
    category = models.CharField(max_length=20, choices=LOG_CATEGORIES, db_index=True)
    action = models.CharField(max_length=255, help_text="Specific action performed")
    status = models.CharField(max_length=20, choices=[('SUCCESS', 'Success'), ('FAILURE', 'Failure')], db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_data = models.JSONField(default=dict, blank=True, help_text="Sanitized request details")
    response_data = models.JSONField(default=dict, blank=True, help_text="Sanitized response details")
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.category} - {self.action} ({self.status}) at {self.created_at}"


class PermissionRole(models.Model):
    """
    Role-based access control (RBAC) model for managing user permissions.
    Defines roles with associated permissions for fine-grained access control.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=list, help_text="List of permission codes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_system_role = models.BooleanField(default=False, help_text="System roles cannot be deleted")

    class Meta:
        db_table = 'permission_roles'
        verbose_name = 'Permission Role'
        verbose_name_plural = 'Permission Roles'

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """
    Links users to roles for permission assignment.
    Supports role expiration for temporary access grants.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(PermissionRole, on_delete=models.CASCADE, related_name='users')
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Optional expiration for temporary roles")
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_roles',
        help_text="Admin who assigned this role"
    )

    class Meta:
        db_table = 'user_roles'
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        unique_together = [('user', 'role')]
        indexes = [
            models.Index(fields=['user', 'role']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"