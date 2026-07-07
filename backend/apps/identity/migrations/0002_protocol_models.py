import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IdentityKeyPair',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('key_algorithm', models.CharField(choices=[('ED25519', 'Ed25519'), ('X25519', 'X25519'), ('RSA', 'RSA')], default='ED25519', max_length=20)),
                ('public_key', models.TextField(help_text='Public key material used for verification')),
                ('key_fingerprint', models.CharField(db_index=True, max_length=128, unique=True)),
                ('private_key_reference', models.CharField(blank=True, help_text='Reference to sealed private key material', max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('rotated_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='identity_keypair', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Identity Key Pair',
                'verbose_name_plural': 'Identity Key Pairs',
                'db_table': 'identity_key_pairs',
                'indexes': [
                    models.Index(fields=['user', 'is_active'], name='identity_key_user_active_idx'),
                    models.Index(fields=['key_fingerprint'], name='identity_key_fingerprint_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='UserDevice',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('device_name', models.CharField(max_length=255)),
                ('device_identifier', models.CharField(db_index=True, max_length=255, unique=True)),
                ('device_public_key', models.TextField(blank=True, help_text='Device public key or attestation material')),
                ('platform', models.CharField(blank=True, max_length=50)),
                ('trust_level', models.IntegerField(choices=[(0, 'Untrusted'), (1, 'Recognized'), (2, 'Trusted'), (3, 'High Trust')], db_index=True, default=0)),
                ('is_trusted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('last_seen_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='devices', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Device',
                'verbose_name_plural': 'User Devices',
                'db_table': 'user_devices',
                'indexes': [
                    models.Index(fields=['user', 'is_trusted'], name='user_devices_user_trusted_idx'),
                    models.Index(fields=['device_identifier'], name='user_devices_identifier_idx'),
                    models.Index(fields=['trust_level'], name='user_devices_trust_level_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='PairingSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_token', models.CharField(db_index=True, max_length=255, unique=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('SCANNED', 'Scanned'), ('VERIFIED', 'Verified'), ('COMPLETED', 'Completed'), ('EXPIRED', 'Expired'), ('REVOKED', 'Revoked')], db_index=True, default='PENDING', max_length=20)),
                ('requested_device_name', models.CharField(blank=True, max_length=255)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(db_index=True)),
                ('scanned_at', models.DateTimeField(blank=True, null=True)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('paired_device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pairing_sessions', to='identity.userdevice')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pairing_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Pairing Session',
                'verbose_name_plural': 'Pairing Sessions',
                'db_table': 'pairing_sessions',
                'indexes': [
                    models.Index(fields=['user', 'status'], name='pairing_sessions_user_status_idx'),
                    models.Index(fields=['session_token'], name='pairing_sessions_token_idx'),
                    models.Index(fields=['expires_at'], name='pairing_sessions_expires_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='AuthenticationChallenge',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('challenge_token', models.CharField(db_index=True, max_length=255, unique=True)),
                ('challenge_type', models.CharField(choices=[('SIGNATURE', 'Signature Verification'), ('QR_CONFIRMATION', 'QR Confirmation'), ('MFA_CONFIRMATION', 'MFA Confirmation')], db_index=True, max_length=20)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('ISSUED', 'Issued'), ('VERIFIED', 'Verified'), ('FAILED', 'Failed'), ('EXPIRED', 'Expired')], db_index=True, default='PENDING', max_length=20)),
                ('challenge_payload', models.JSONField(blank=True, default=dict)),
                ('expected_public_key', models.TextField(blank=True)),
                ('verification_metadata', models.JSONField(blank=True, default=dict)),
                ('issued_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(db_index=True)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='authentication_challenges', to='identity.userdevice')),
                ('pairing_session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='authentication_challenges', to='identity.pairingsession')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authentication_challenges', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Authentication Challenge',
                'verbose_name_plural': 'Authentication Challenges',
                'db_table': 'authentication_challenges',
                'indexes': [
                    models.Index(fields=['user', 'status'], name='auth_challenges_user_status_idx'),
                    models.Index(fields=['challenge_token'], name='auth_challenges_token_idx'),
                    models.Index(fields=['expires_at'], name='auth_challenges_expires_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='AuthenticationSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_token', models.CharField(db_index=True, max_length=255, unique=True)),
                ('refresh_token', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('EXPIRED', 'Expired'), ('REVOKED', 'Revoked'), ('INVALID', 'Invalid')], db_index=True, default='ACTIVE', max_length=20)),
                ('authenticated_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(db_index=True)),
                ('revoked_at', models.DateTimeField(blank=True, null=True)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('is_mfa_verified', models.BooleanField(default=False, help_text='Whether MFA was completed for this session')),
                ('challenge', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='authentication_sessions', to='identity.authenticationchallenge')),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='authentication_sessions', to='identity.userdevice')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authentication_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Authentication Session',
                'verbose_name_plural': 'Authentication Sessions',
                'db_table': 'authentication_sessions',
                'indexes': [
                    models.Index(fields=['user', 'status'], name='auth_sessions_user_status_idx'),
                    models.Index(fields=['session_token'], name='auth_sessions_token_idx'),
                    models.Index(fields=['expires_at'], name='auth_sessions_expires_idx'),
                ],
            },
        ),
    ]