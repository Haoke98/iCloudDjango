# Generated by Django 4.0 on 2024-03-19 03:45

import datetime
from django.db import migrations, models
import icloud.models
import simplepro.components.fields
import simplepro.components.fields.char_field
import simplepro.components.fields.input_password_field
import simplepro.editor.fields
import simplepro.editor.fields.json_text_field
import simplepro.lib.pkHelper


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('createdAt', models.DateTimeField(auto_created=True, auto_now_add=True, db_index=True, null=True, verbose_name='创建时间')),
                ('updatedAt', models.DateTimeField(auto_now=True, db_index=True, null=True, verbose_name='最近更新时间')),
                ('deletedAt', models.DateTimeField(db_index=True, editable=False, null=True, verbose_name='被删除时间')),
                ('remark', models.CharField(blank=True, db_index=True, max_length=100, null=True, verbose_name='小备注/标签')),
                ('info', simplepro.editor.fields.UETextField(blank=True, null=True, verbose_name='说明')),
                ('id', models.CharField(default=simplepro.lib.pkHelper.uuid_generator, editable=False, max_length=48, primary_key=True, serialize=False)),
                ('appleId', simplepro.components.fields.char_field.CharField(max_length=48, null=True, verbose_name='AppleID')),
                ('name', models.CharField(max_length=50, verbose_name='标题')),
                ('total', models.PositiveIntegerField(default=0, verbose_name='iCloud上的数量')),
                ('count', models.PositiveIntegerField(default=0, verbose_name='已经采集到的数量')),
                ('synced', models.BooleanField(default=False, verbose_name='同步完毕')),
                ('size', models.PositiveBigIntegerField(default=0, verbose_name='大小')),
                ('query_fieldName', models.CharField(max_length=50, null=True, verbose_name='过滤字段')),
                ('query_comparator', models.CharField(max_length=50, null=True, verbose_name='过滤操作')),
                ('query_fieldValue_type', models.CharField(max_length=50, null=True, verbose_name='过滤值数据类型')),
                ('query_fieldValue_value', models.CharField(max_length=50, null=True, verbose_name='过滤值')),
            ],
            options={
                'verbose_name': 'iCloud相册',
                'verbose_name_plural': 'iCloud相册',
            },
        ),
        migrations.CreateModel(
            name='AppleId',
            fields=[
                ('createdAt', models.DateTimeField(auto_created=True, auto_now_add=True, db_index=True, null=True, verbose_name='创建时间')),
                ('id', models.CharField(default=simplepro.lib.pkHelper.uuid_generator, editable=False, max_length=48, primary_key=True, serialize=False)),
                ('updatedAt', models.DateTimeField(auto_now=True, db_index=True, null=True, verbose_name='最近更新时间')),
                ('deletedAt', models.DateTimeField(db_index=True, editable=False, null=True, verbose_name='被删除时间')),
                ('remark', models.CharField(blank=True, db_index=True, max_length=100, null=True, verbose_name='小备注/标签')),
                ('info', simplepro.editor.fields.UETextField(blank=True, null=True, verbose_name='说明')),
                ('email', simplepro.components.fields.char_field.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='绑定的邮箱')),
                ('tel', simplepro.components.fields.char_field.CharField(blank=True, max_length=11, null=True, unique=True, verbose_name='绑定的手机号')),
                ('passwd', simplepro.components.fields.input_password_field.PasswordInputField(blank=True, max_length=48, null=True, verbose_name='密码')),
                ('last2FactorAuthenticateAt', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='上次两步验证时间')),
                ('lastConfirmedSessionValidityAt', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='上次确认会话有效性时间')),
                ('maxSessionAge', models.DurationField(blank=True, default=datetime.timedelta(0), editable=False, verbose_name='最长会话有效期')),
            ],
            options={
                'verbose_name': 'AppleID',
                'verbose_name_plural': 'AppleID',
            },
        ),
        migrations.CreateModel(
            name='LocalMedia',
            fields=[
                ('createdAt', models.DateTimeField(auto_created=True, auto_now_add=True, db_index=True, null=True, verbose_name='创建时间')),
                ('updatedAt', models.DateTimeField(auto_now=True, db_index=True, null=True, verbose_name='最近更新时间')),
                ('deletedAt', models.DateTimeField(db_index=True, editable=False, null=True, verbose_name='被删除时间')),
                ('remark', models.CharField(blank=True, db_index=True, max_length=100, null=True, verbose_name='小备注/标签')),
                ('info', simplepro.editor.fields.UETextField(blank=True, null=True, verbose_name='说明')),
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('appleId', simplepro.components.fields.char_field.CharField(max_length=48, null=True, verbose_name='AppleID')),
                ('filename', models.CharField(blank=True, max_length=100, null=True, verbose_name='文件名')),
                ('ext', models.CharField(blank=True, max_length=10, null=True, verbose_name='扩展名')),
                ('size', models.BigIntegerField(blank=True, null=True, verbose_name='大小')),
                ('duration', models.PositiveIntegerField(blank=True, null=True, verbose_name='时长')),
                ('dimensionX', models.IntegerField(blank=True, null=True, verbose_name='DX')),
                ('dimensionY', models.IntegerField(blank=True, null=True, verbose_name='DY')),
                ('orientation', models.IntegerField(blank=True, null=True, verbose_name='方向')),
                ('adjustmentRenderType', models.IntegerField(blank=True, null=True)),
                ('timeZoneOffset', models.IntegerField(blank=True, null=True)),
                ('burstFlags', models.IntegerField(blank=True, null=True)),
                ('masterRecordChangeTag', models.CharField(blank=True, max_length=50, null=True)),
                ('assetRecordChangeTag', models.CharField(blank=True, max_length=50, null=True)),
                ('asset_date', models.DateTimeField(blank=True, null=True, verbose_name='生成时间')),
                ('added_date', models.DateTimeField(blank=True, null=True, verbose_name='加入icloud的时间')),
                ('detach_icloud_date', models.DateTimeField(blank=True, null=True, verbose_name='从icloud中移除时间')),
                ('locationEnc', models.TextField(blank=True, null=True, verbose_name='地址信息(已加密)')),
                ('prv', models.FileField(blank=True, help_text='HICH图片和PNG图片的可预览文件为JPEG图，MOV视频的可预览文件为MP4', null=True, upload_to=icloud.models.upload_prv, verbose_name='可预览文件')),
                ('origin', models.FileField(blank=True, null=True, upload_to=icloud.models.upload_origin, verbose_name='原始文件')),
                ('originTest', simplepro.components.fields.VideoField(blank=True, max_length=255, null=True, verbose_name='视频原始文件(测试)')),
                ('thumb', simplepro.components.fields.ImageField(blank=True, max_length=255, null=True, verbose_name='缩略图')),
                ('versions', simplepro.editor.fields.json_text_field.JsonTextField(blank=True, null=True)),
                ('masterRecord', simplepro.editor.fields.json_text_field.JsonTextField(blank=True, null=True)),
                ('assetRecord', simplepro.editor.fields.json_text_field.JsonTextField(blank=True, null=True)),
                ('assetRecordAfterDelete', simplepro.editor.fields.json_text_field.JsonTextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': '本地资源',
                'verbose_name_plural': '本地资源',
                'ordering': ('-asset_date',),
            },
        ),
        migrations.CreateModel(
            name='IMedia',
            fields=[
                ('createdAt', models.DateTimeField(auto_created=True, auto_now_add=True, db_index=True, null=True, verbose_name='创建时间')),
                ('updatedAt', models.DateTimeField(auto_now=True, db_index=True, null=True, verbose_name='最近更新时间')),
                ('deletedAt', models.DateTimeField(db_index=True, editable=False, null=True, verbose_name='被删除时间')),
                ('remark', models.CharField(blank=True, db_index=True, max_length=100, null=True, verbose_name='小备注/标签')),
                ('info', simplepro.editor.fields.UETextField(blank=True, null=True, verbose_name='说明')),
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('appleId', simplepro.components.fields.char_field.CharField(max_length=48, null=True, verbose_name='AppleID')),
                ('filename', models.CharField(max_length=100, null=True, verbose_name='文件名')),
                ('ext', models.CharField(max_length=10, verbose_name='扩展名')),
                ('size', models.BigIntegerField(null=True, verbose_name='大小')),
                ('dimensionX', models.IntegerField(null=True, verbose_name='DX')),
                ('dimensionY', models.IntegerField(null=True, verbose_name='DY')),
                ('asset_date', models.DateTimeField(null=True, verbose_name='生成时间')),
                ('added_date', models.DateTimeField(null=True, verbose_name='加入icloud的时间')),
                ('versions', models.TextField(null=True)),
                ('startRank', models.IntegerField(null=True)),
                ('thumbURL', models.TextField(null=True)),
                ('isHidden', models.BooleanField(null=True, verbose_name='隐藏')),
                ('isFavorite', models.BooleanField(null=True, verbose_name='收藏')),
                ('deleted', models.BooleanField(null=True, verbose_name='已删除')),
                ('createdDeviceID', models.CharField(max_length=255, null=True, verbose_name='创建的设备ID')),
                ('createdUserRecordName', models.CharField(max_length=255, null=True, verbose_name='创建的用户ID')),
                ('modifiedDeviceID', models.CharField(max_length=255, null=True, verbose_name='更新的设备ID')),
                ('modifiedUserRecordName', models.CharField(max_length=255, null=True, verbose_name='更新的用户ID')),
                ('duration', models.PositiveIntegerField(null=True, verbose_name='时长')),
                ('adjustmentRenderType', models.IntegerField(null=True)),
                ('timeZoneOffset', models.IntegerField(null=True)),
                ('burstFlags', models.IntegerField(null=True)),
                ('orientation', models.IntegerField(null=True, verbose_name='方向')),
                ('locationEnc', models.TextField(null=True, verbose_name='地址信息(已加密)')),
                ('masterRecordChangeTag', models.CharField(max_length=50, null=True)),
                ('assetRecordChangeTag', models.CharField(max_length=50, null=True)),
                ('masterRecordType', models.CharField(max_length=50, null=True)),
                ('assetRecordType', models.CharField(max_length=50, null=True)),
                ('masterRecord', models.TextField(null=True)),
                ('assetRecord', models.TextField(null=True)),
                ('albums', simplepro.components.fields.ManyToManyField(blank=True, related_name='medias', to='icloud.Album', verbose_name='相册')),
            ],
            options={
                'verbose_name': 'iCloud媒体',
                'verbose_name_plural': 'iCloud媒体',
                'ordering': ('-asset_date',),
            },
        ),
        migrations.AddConstraint(
            model_name='album',
            constraint=models.UniqueConstraint(fields=('name', 'appleId'), name='unique_name_appleId'),
        ),
        migrations.AddConstraint(
            model_name='album',
            constraint=models.UniqueConstraint(fields=('id', 'appleId'), name='unique_id_appleId'),
        ),
        migrations.AddConstraint(
            model_name='album',
            constraint=models.UniqueConstraint(fields=('name', 'id'), name='unique_name_id'),
        ),
        migrations.AddConstraint(
            model_name='imedia',
            constraint=models.UniqueConstraint(fields=('id', 'appleId'), name='unique_media_id_appleId'),
        ),
    ]
