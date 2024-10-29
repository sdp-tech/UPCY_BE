# Generated by Django 4.0 on 2024-10-29 04:07

from django.db import migrations, models
import django.db.models.deletion
import order.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_alter_user_groups_alter_user_user_permissions'),
        ('market', '0005_service_temporary'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('order_number', models.CharField(max_length=20, unique=True)),
                ('order_uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('extra_material_name', models.CharField(max_length=50, null=True)),
                ('additional_request', models.TextField(null=True)),
                ('order_service_price', models.PositiveIntegerField(null=True)),
                ('order_option_price', models.PositiveIntegerField(null=True)),
                ('total_price', models.PositiveIntegerField(null=True)),
                ('request_date', models.DateField()),
                ('kakaotalk_openchat_link', models.TextField(null=True)),
                ('additional_option', models.ManyToManyField(blank=True, related_name='additional_option_order', to='market.ServiceOption')),
                ('material_name', models.ManyToManyField(blank=True, related_name='order_texture_name', to='market.ServiceMaterial')),
                ('request_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_user_order', to='users.user')),
                ('service', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='service_order', to='market.service')),
            ],
            options={
                'db_table': 'order',
            },
        ),
        migrations.CreateModel(
            name='TransactionOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('transaction_uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('transaction_option', models.CharField(choices=[('pickup', '대면'), ('delivery', '택배')], max_length=50)),
                ('delivery_address', models.TextField()),
                ('delivery_name', models.TextField()),
                ('delivery_phone_number', models.TextField()),
                ('service_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaction_option', to='order.order')),
            ],
            options={
                'db_table': 'transaction_option',
            },
        ),
        migrations.CreateModel(
            name='OrderState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('order_state_uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('reformer_status', models.CharField(choices=[('accepted', '수락'), ('rejected', '거절'), ('pending', '대기'), ('received', '재료 수령'), ('produced', '제작 완료'), ('deliver', '배송중'), ('end', '거래 완료')], default='pending', max_length=10)),
                ('service_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_state', to='order.order')),
            ],
            options={
                'db_table': 'order_state',
            },
        ),
        migrations.CreateModel(
            name='OrderImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('image', models.FileField(max_length=255, upload_to=order.models.get_order_image_upload_path)),
                ('service_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_image', to='order.order')),
            ],
            options={
                'db_table': 'order_image',
            },
        ),
        migrations.CreateModel(
            name='DeliveryInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('delivery_uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('delivery_company', models.CharField(max_length=50, null=True)),
                ('delivery_tracking_number', models.CharField(max_length=50, null=True)),
                ('service_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_information', to='order.order')),
            ],
            options={
                'db_table': 'delivery_information',
            },
        ),
        migrations.CreateModel(
            name='AdditionalImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('additional_uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('image', models.FileField(max_length=255, null=True, upload_to=order.models.get_order_additional_image_upload_path)),
                ('service_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='additional_image', to='order.order')),
            ],
            options={
                'db_table': 'additional_image',
            },
        ),
    ]
