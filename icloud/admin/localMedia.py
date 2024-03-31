# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/3/31
@Software: PyCharm
@disc:
======================================="""
import urllib

from django.contrib import admin
from django.http import JsonResponse
from minio_storage.storage import get_setting
from simplepro.dialog import MultipleCellDialog, ModalDialog

from icloud.admin.iMedia import ThumbFilter, PrvFilter
from icloud.models import LocalMedia
from utils import human_readable_bytes, human_readable_time


@admin.register(LocalMedia)
class LocalMediaAdmin(admin.ModelAdmin):
    list_display = ['id', 'filename', 'ext', 'size', 'thumb', 'dialog_lists', 'dimensionX', 'dimensionY',
                    'asset_date', 'added_date', 'detach_icloud_date', 'createdAt', 'updatedAt', 'origin'
                    ]
    list_filter = ['ext', 'dimensionX', 'dimensionY', 'asset_date', 'added_date', 'createdAt', 'updatedAt',
                   ThumbFilter, PrvFilter]  # TODO:实现是否为实况图的过滤器，可以通过originalRes.ext和prv.ext来确认。
    # list_filter_multiples = ('ext', 'dimensionX', 'dimensionY',)
    search_fields = ['id', 'filename']
    actions = []
    list_per_page = 20

    def dialog_lists(self, model):
        return MultipleCellDialog([
            ModalDialog(url=f'/icloud/detail?id={urllib.parse.quote(model.id)}&source=LocalMedia', title=model.filename,
                        cell='<el-link type="primary">预览</el-link>', width="840px", height="600px"),
        ])

    def _thumb(self, obj):
        if obj.prv.name is None:
            return True
        return False

    # 这个是列头显示的文本
    dialog_lists.short_description = "预览"

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def formatter(self, obj, field_name, value):
        # 这里可以对value的值进行判断，比如日期格式化等
        if field_name == "size":
            if value:
                return f"""<span title="{value}">{human_readable_bytes(value)}</span>"""
        if field_name == 'thumb':
            if value:
                STORAGE_END_POINT = get_setting("MINIO_STORAGE_ENDPOINT")
                BUCKET_NAME = get_setting("MINIO_STORAGE_MEDIA_BUCKET_NAME")
                final_url = "http://" + STORAGE_END_POINT + '/' + BUCKET_NAME + '/' + value
                print(STORAGE_END_POINT, print(final_url))
                return f"""<img src="{final_url}" style="height:100px;">"""
        if field_name == "duration":
            if value:
                return f"""<span title="{value}">{human_readable_time(value)}</span>"""
        if field_name == "origin":
            if value:
                return f""" <el-link type="primary" href="/media/{value}" target="_blank">点击浏览源文件</el-link>"""
        return value

    fields_options = {
        'id': {
            # 'fixed': 'left',
            'width': '280px',
            'align': 'center'
        },
        'createdAt': {
            'width': '180px',
            'align': 'left'
        },
        'updatedAt': {
            'width': '180px',
            'align': 'left'
        },
        'filename': {
            'width': '200px',
            'align': 'center'
        },
        'ext': {
            'width': '100px',
            'align': 'center'
        },
        'size': {
            'width': '120px',
            'align': 'center'
        },
        'dimensionX': {
            'width': '70px',
            'align': 'left'
        },
        'dimensionY': {
            'width': '70px',
            'align': 'left'
        },
        'asset_date': {
            'width': '180px',
            'align': 'center'
        },
        'added_date': {
            'width': '180px',
            'align': 'center'
        },
        'thumb': {
            'width': '120px',
            'align': 'center'
        },
        'origin': {
            'width': '200px',
            'align': 'center'
        },
        'detach_icloud_date': {
            'width': '180px',
            'align': 'center'
        }
    }

    def layer_input(self, request, queryset):
        # 这里的queryset 会有数据过滤，只包含选中的数据

        post = request.POST
        # 这里获取到数据后，可以做些业务处理
        # post中的_action 是方法名
        # post中 _selected 是选中的数据，逗号分割
        if not post.get('_selected'):
            return JsonResponse(data={
                'status': 'error',
                'msg': '请先选中数据！'
            })
        else:
            return JsonResponse(data={
                'status': 'success',
                'msg': '处理成功！'
            })

    layer_input.short_description = '弹出对话框输入'
    layer_input.type = 'success'
    layer_input.icon = 'el-icon-s-promotion'

    # 指定一个输入参数，应该是一个数组

    # 指定为弹出层，这个参数最关键
    layer_input.layer = {
        # 弹出层中的输入框配置

        # 这里指定对话框的标题
        'title': '弹出层输入框',
        # 提示信息
        'tips': '这个弹出对话框是需要在admin中进行定义，数据新增编辑等功能，需要自己来实现。',
        # 确认按钮显示文本
        'confirm_button': '确认提交',
        # 取消按钮显示文本
        'cancel_button': '取消',

        # 弹出层对话框的宽度，默认50%
        'width': '40%',

        # 表单中 label的宽度，对应element-ui的 label-width，默认80px
        'labelWidth': "80px",
        'params': [{
            # 这里的type 对应el-input的原生input属性，默认为input
            'type': 'input',
            # key 对应post参数中的key
            'key': 'name',
            # 显示的文本
            'label': '名称',
            # 为空校验，默认为False
            'require': True,
            # 附加参数
            'extras': {
                'prefix-icon': 'el-icon-delete',
                'suffix-icon': 'el-icon-setting',
                'clearable': True
            }
        }, {
            'type': 'select',
            'key': 'type',
            'label': '类型',
            'width': '200px',
            # size对应elementui的size，取值为：medium / small / mini
            'size': 'small',
            # value字段可以指定默认值
            'value': '0',
            'options': [{
                'key': '0',
                'label': '收入'
            }, {
                'key': '1',
                'label': '支出'
            }]
        }, {
            'type': 'number',
            'key': 'money',
            'label': '金额',
            # 设置默认值
            'value': 1000
        }, {
            'type': 'date',
            'key': 'date',
            'label': '日期',
        }, {
            'type': 'datetime',
            'key': 'datetime',
            'label': '时间',
        }, {
            'type': 'rate',
            'key': 'star',
            'label': '评价等级'
        }, {
            'type': 'color',
            'key': 'color',
            'label': '颜色'
        }, {
            'type': 'slider',
            'key': 'slider',
            'label': '滑块'
        }, {
            'type': 'switch',
            'key': 'switch',
            'label': 'switch开关'
        }, {
            'type': 'input_number',
            'key': 'input_number',
            'label': 'input number'
        }, {
            'type': 'checkbox',
            'key': 'checkbox',
            # 必须指定默认值
            'value': [],
            'label': '复选框',
            'options': [{
                'key': '0',
                'label': '收入'
            }, {
                'key': '1',
                'label': '支出'
            }, {
                'key': '2',
                'label': '收益'
            }]
        }, {
            'type': 'radio',
            'key': 'radio',
            'label': '单选框',
            'options': [{
                'key': '0',
                'label': '收入'
            }, {
                'key': '1',
                'label': '支出'
            }, {
                'key': '2',
                'label': '收益'
            }]
        }]
    }
