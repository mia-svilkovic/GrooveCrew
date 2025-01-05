# Generated by Django 5.1.4 on 2025-01-05 13:03

import django.contrib.auth.models
import django.db.models.deletion
import django.db.models.functions.text
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('username', models.CharField(max_length=150, unique=True)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Genre',
                'verbose_name_plural': 'Genres',
                'constraints': [models.UniqueConstraint(django.db.models.functions.text.Lower('name'), name='unique_genre_case_insensitive', violation_error_message='A genre with this name already exists (case insensitive).')],
            },
        ),
        migrations.CreateModel(
            name='GoldmineConditionCover',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('abbreviation', models.CharField(max_length=10)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Goldmine Condition (Cover)',
                'verbose_name_plural': 'Goldmine Conditions (Cover)',
                'constraints': [models.UniqueConstraint(django.db.models.functions.text.Lower('name'), name='unique_cover_condition_name_case_insensitive', violation_error_message='A cover condition with this name already exists (case insensitive).'), models.UniqueConstraint(django.db.models.functions.text.Lower('abbreviation'), name='unique_cover_condition_abbreviation_case_insensitive', violation_error_message='A cover condition with this abbreviation already exists (case insensitive).')],
            },
        ),
        migrations.CreateModel(
            name='GoldmineConditionRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('abbreviation', models.CharField(max_length=10)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Goldmine Condition (Record)',
                'verbose_name_plural': 'Goldmine Conditions (Record)',
                'constraints': [models.UniqueConstraint(django.db.models.functions.text.Lower('name'), name='unique_record_condition_name_case_insensitive', violation_error_message='A record condition with this name already exists (case insensitive).'), models.UniqueConstraint(django.db.models.functions.text.Lower('abbreviation'), name='unique_record_condition_abbreviation_case_insensitive', violation_error_message='A record condition with this abbreviation already exists (case insensitive).')],
            },
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('catalog_number', models.CharField(max_length=255)),
                ('artist', models.CharField(max_length=255)),
                ('album_name', models.CharField(max_length=255)),
                ('release_year', models.IntegerField()),
                ('location', models.CharField(max_length=255)),
                ('available_for_exchange', models.BooleanField(default=True)),
                ('additional_description', models.TextField(blank=True)),
                ('cover_condition', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='records', to='api.goldmineconditioncover')),
                ('genre', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='records', to='api.genre')),
                ('record_condition', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='records', to='api.goldmineconditionrecord')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='records', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Record',
                'verbose_name_plural': 'Records',
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='record_photos/')),
                ('record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='api.record')),
            ],
            options={
                'verbose_name': 'Photo',
                'verbose_name_plural': 'Photos',
            },
        ),
        migrations.CreateModel(
            name='Exchange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modification_datetime', models.DateTimeField(auto_now=True)),
                ('completed_datetime', models.DateTimeField(blank=True, null=True)),
                ('completed', models.BooleanField(default=False)),
                ('initiator_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='initiated_exchanges', to=settings.AUTH_USER_MODEL)),
                ('next_user_to_review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exchanges_to_review', to=settings.AUTH_USER_MODEL)),
                ('receiver_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_exchanges', to=settings.AUTH_USER_MODEL)),
                ('requested_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requesting_exchanges', to='api.record')),
            ],
            options={
                'verbose_name': 'Exchange',
                'verbose_name_plural': 'Exchanges',
            },
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_catalog_number', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeRecordRequestedByReceiver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exchange', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='records_requested_by_receiver', to='api.exchange')),
                ('record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exchanges_where_requested_by_receiver', to='api.record')),
            ],
            options={
                'verbose_name': 'Record Requested by Receiver',
                'verbose_name_plural': 'Records Requested by Receiver',
                'constraints': [models.UniqueConstraint(fields=('exchange', 'record'), name='unique_record_requested_per_exchange')],
            },
        ),
        migrations.CreateModel(
            name='ExchangeOfferedRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exchange', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offered_records', to='api.exchange')),
                ('record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exchanges_where_offered', to='api.record')),
            ],
            options={
                'verbose_name': 'Offered record',
                'verbose_name_plural': 'Offered records',
                'constraints': [models.UniqueConstraint(fields=('exchange', 'record'), name='unique_record_per_exchange')],
            },
        ),
        migrations.AddConstraint(
            model_name='exchange',
            constraint=models.UniqueConstraint(fields=('initiator_user', 'receiver_user', 'requested_record'), name='unique_exchange_per_record_per_user'),
        ),
        migrations.AddConstraint(
            model_name='wishlist',
            constraint=models.UniqueConstraint(fields=('record_catalog_number', 'user'), name='unique_record_catalog_number_per_user', violation_error_message="This record catalog number is already added to the user's wishlist."),
        ),
    ]
