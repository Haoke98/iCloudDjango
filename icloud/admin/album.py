# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/3/31
@Software: PyCharm
@disc:
======================================="""
import threading
import uuid

from django.contrib import admin
from django.http import JsonResponse
from simplepro.admin import FieldOptions
from simplepro.decorators import button, layer
from simpleui.admin import AjaxAdmin

from icloud.models import Album, AppleId
from icloud.services import collect_all_medias
from utils import human_readable_bytes, icloud


def get_sync_layer_config(request, queryset):
    """
    这个方法只有一个request参数，没有其他的入参
    """
    options = []
    objs = AppleId.objects.all()
    for obj in objs:
        options.append({
            "label": obj.email,
            "key": obj.email
        })
    return {
        # 弹出层中的输入框配置

        # 这里指定对话框的标题
        'title': '相册数据同步',
        # 提示信息
        'tips': f'请选出一个账号用来同步数据！！！',
        # 确认按钮显示文本
        'confirm_button': '确认提交',
        # 取消按钮显示文本
        'cancel_button': '取消',

        # 弹出层对话框的宽度，默认50%
        'width': '40%',

        # 表单中 label的宽度，对应element-ui的 label-width，默认80px
        'labelWidth': "160px",
        'params': [{
            # 这里的type 对应el-input的原生input属性，默认为input
            'type': 'select',
            # key 对应post参数中的key
            'key': 'apple_id',
            # 显示的文本
            'label': '要同步的iCloud账号',
            # 为空校验，默认为False
            'require': True,
            'options': options,
            'extras': {
                'prefix-icon': 'el-icon-delete',
                'suffix-icon': 'el-icon-setting',
                'clearable': True,
                "placeholder": "请选择受信任设备"
            }

        }]
    }


@admin.register(Album)
class AlbumAdmin(AjaxAdmin):
    list_display = ['id', 'name', 'total', 'count', 'synced', 'size',
                    'appleId',
                    'query_fieldName', 'query_comparator', 'query_fieldValue_type',
                    'query_fieldValue_value',
                    'updatedAt', 'createdAt', 'deletedAt'
                    ]
    list_filter = ['appleId', 'synced', 'createdAt', 'updatedAt', 'query_fieldName',
                   'query_comparator', 'query_fieldValue_type']
    actions = ['sync', 'collect', 'handle_pk']
    search_fields = ['name', 'query_fieldValue_value']
    ordering = ('-updatedAt',)

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def formatter(self, obj, field_name, value):
        # 这里可以对value的值进行判断，比如日期格式化等
        if field_name == "size":
            if value:
                return f"""<span title="{value}">{human_readable_bytes(value)}</span>"""
        return value

    @layer(config=get_sync_layer_config)
    @button(type='danger', short_description='从icloud中同步相册列表', enable=True, confirm="您确定要生成吗？")
    def sync(self, request, queryset):
        post = request.POST
        if not post.get('apple_id'):
            return JsonResponse(data={
                'status': 'error',
                'msg': '没有选择任何AppleID！'
            })
        else:
            apple_id = post.get("apple_id")
            qs: AppleId = AppleId.objects.filter(email=apple_id).first()
            print("被选中的用户名:", qs.username, qs.passwd)
            _iService = icloud.IcloudService(qs.username, qs.passwd, True)
            print(f"连接成功！[{_iService.requires_2fa}, {_iService.requires_2sa}]")
            if _iService.requires_2fa:
                return JsonResponse(data={
                    'status': 'warn',
                    'msg': '需要先去做二次验证, 此页面无法验证'
                })
            else:
                for i, album_name in enumerate(_iService.photos.albums):
                    album = _iService.photos.albums[album_name]
                    total = len(album)
                    print(i, album_name, total, album.query_filter)
                    obj, _ = Album.objects.get_or_create(name=album_name, appleId=apple_id)
                    obj.total = total
                    obj.agg()
                    obj.set_query(album.query_filter)
                    obj.appleId = apple_id
                    obj.save()
                return {
                    'state': True,
                    'msg': f'同步成功'
                }

    @button(type='warning', short_description='同步媒体', enable=False, confirm="您确定要生成吗？")
    def collect(self, request, queryset):
        for qs in queryset:
            # FIXME: 以下调用的 collect_all_media 方法, 目前只接受一个参数iService,
            #  所以不支持按照输入的album来同步, 需要继续实现.
            th = threading.Thread(target=collect_all_medias, args=([qs],))
            th.start()
        return {
            'state': True,
            'msg': f'采集程序已经启动'
        }

    @button(type='warning', short_description='处理PK', enable=True, confirm="确定对PK进行特殊处理吗?")
    def handle_pk(self, request, queryset):
        for i, album in enumerate(Album.objects.all()):
            final_pk = None
            if album.query_fieldValue_value == "" or album.query_fieldValue_value is None:
                final_pk = uuid.uuid4().__str__()
            else:
                final_pk = album.query_fieldValue_value
            print(f"album{i}:{album.name} ===> {final_pk}")
            album.id = final_pk
            album.save()
            medias = album.medias.all()
            for j, media in enumerate(medias):
                print(" " * 10, "|", "-" * 10, f"{j}/{media.__len__()}", media, "===>", final_pk)
        return {
            'state': True,
            'msg': f'处理成功'
        }

    fields_options = {
        'id': FieldOptions.UUID,
        'createdAt': {
            'width': '180px',
            'align': 'left'
        },
        'updatedAt': {
            'width': '180px',
            'align': 'left'
        },
        'name': {
            'width': '180px',
            'align': 'left'
        },
        'total': {
            'width': '100px',
            'align': 'right'
        },
        'count': {
            'width': '120px',
            'align': 'right'
        },
        'synced': {
            'width': '70px',
            'align': 'right'
        },
        'size': {
            'width': '100px',
            'align': 'right'
        },
        'appleId': {
            'width': '120px',
            'align': 'right',
            "show_overflow_tooltip": True
        },
        'query_fieldName': {
            'width': '100px',
            'align': 'center'
        },
        'query_comparator': {
            'width': '100px',
            'align': 'center'
        },
        'query_fieldValue_type': {
            'width': '140px',
            'align': 'center'
        },
        'query_fieldValue_value': {
            'width': '340px',
            'align': 'center'
        },
    }
