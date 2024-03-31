# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/3/31
@Software: PyCharm
@disc:
======================================="""
import os
import threading
import urllib
from datetime import datetime
from urllib.parse import urlencode

from django.contrib import admin
from django.http import JsonResponse
from simplepro.decorators import layer, button
from simplepro.dialog import MultipleCellDialog, ModalDialog
from simpleui.admin import AjaxAdmin

from icloud.models import LocalMedia, IMedia, AppleId
from utils import icloud, human_readable_bytes, human_readable_time
from .album import get_sync_layer_config
from ..services import collect_all_medias, migrateIcloudToLocal, delete_from_icloud
from ..views import DLT


class ThumbFilter(admin.SimpleListFilter):
    title = '缩略图'  # 过滤器标题
    parameter_name = 'thumb'  # URL中参数的名字

    def lookups(self, request, model_admin):
        # 返回要显示为过滤选项的值
        a = LocalMedia.objects.filter(thumb__isnull=False).count()
        b = LocalMedia.objects.filter(thumb__isnull=True).count()
        return [(0, f"有({a})"), (1, f"无({b})")]

    def queryset(self, request, queryset):
        # 对查询集进行过滤
        if self.value() == '0':
            return queryset.filter(thumb__isnull=False)
        elif self.value() == '1':
            return queryset.filter(thumb__isnull=True)
        else:
            return queryset.filter()


class PrvFilter(admin.SimpleListFilter):
    title = '可预览文件'  # 过滤器标题
    parameter_name = 'prv_f'  # URL中参数的名字

    def lookups(self, request, model_admin):
        # 返回要显示为过滤选项的值
        return [(0, f"有"), (1, f"无")]
        # FIXME: 自从引入MinIO之后,此功能就无法正常使用了, 请尽快修复相关功能
        a = 0
        b = 0
        for i in LocalMedia.objects.all():
            if i.prv:
                try:
                    if os.path.exists(i.prv.path):
                        a += 1
                    else:
                        b += 1
                except ValueError as e:
                    if "The 'prv' attribute has no file associated with it." in str(e):
                        b += 1
            else:
                pass
        return [(0, f"有({a})"), (1, f"无({b})")]

    def queryset(self, request, queryset):
        # 对查询集进行过滤
        id_list = []
        if self.value() == '0':
            for i in IMedia.objects.all():
                try:
                    if os.path.exists(i.prv.path):
                        id_list.append(i.id)
                except ValueError as e:
                    if "The 'prv' attribute has no file associated with it." in str(e):
                        pass
            return queryset.filter(id__in=id_list)
        elif self.value() == '1':
            for i in IMedia.objects.all():
                try:
                    if not os.path.exists(i.prv.path):
                        id_list.append(i.id)
                except ValueError as e:
                    if "The 'prv' attribute has no file associated with it." in str(e):
                        id_list.append(i.id)
            return queryset.filter(id__in=id_list)
        else:
            return queryset.filter()


@admin.register(IMedia)
class IMediaAdmin(AjaxAdmin):
    list_display = ['id', 'startRank', 'filename', 'ext', 'size', 'duration', 'thumb', 'dialog_lists',
                    'dimensionX', 'dimensionY',
                    'isHidden', 'isFavorite', 'deleted',
                    'asset_date', 'added_date', 'createdAt', 'updatedAt',
                    'adjustmentRenderType', 'timeZoneOffset', 'burstFlags',
                    'orientation',
                    'masterRecordType', 'assetRecordType',
                    'masterRecordChangeTag', 'assetRecordChangeTag',
                    'createdDeviceID', 'createdUserRecordName', 'modifiedDeviceID', 'modifiedUserRecordName',
                    'locationEnc']
    list_filter = ['albums', 'ext', 'dimensionX', 'dimensionY', 'asset_date', 'added_date', 'createdAt',
                   'updatedAt', 'isHidden', 'isFavorite', 'deleted',
                   'createdDeviceID', 'createdUserRecordName', 'modifiedDeviceID', 'modifiedUserRecordName',
                   'adjustmentRenderType', 'timeZoneOffset', 'burstFlags',
                   'orientation',
                   'masterRecordChangeTag', 'assetRecordChangeTag',
                   'masterRecordType', 'assetRecordType'
                   ]  # TODO:实现是否为实况图的过滤器，可以通过originalRes.ext和prv.ext来确认。
    # list_filter_multiples = ('ext', 'dimensionX', 'dimensionY',)
    search_fields = ['id', 'filename']
    actions = ['collect', 'migrate', 'delete']
    list_per_page = 20

    def thumb(self, obj):
        thumb_url = obj.thumbURL
        prv_url = "https://cvws.icloud-content.com.cn/B/AXsCTFGEAH5K_G8v5M550BKYQgrYAU3Llil8eeGq1YllzSOChTP8GzK8/$%7Bf%7D?o=AtJgOCoyIAwQaAoS4iNMm_t_66U9m_Cwk6V-Xc5u9itt&v=1&x=3&a=CAogEuXMIhmVlMSdUwyDPmMEeHBW4Pe8dlT5llye-A7y1KUSbxCh0t6dqTEYoa-6n6kxIgEAUgSYQgrYWgT8GzK8aicHbBtuls-GzfByFYWw_IFgUTD-mns3AcGQtUB2RN2ncMsWk2-ItNJyJ7ksv1IBrE1ycr9kwjX2z7yo1W7T6a5KGQ4z8-32UP5ONKX9XWGyHw&e=1694699001&fl=&r=65210c2f-4722-49e5-9724-3e53321d48d7-1&k=4uaX3YNtEyqLkhukOc7y5A&ckc=com.apple.photos.cloud&ckz=PrimarySync&y=1&p=215&s=bsmRo--bR8qyGg-VJt0rZnR_1XI"
        dlt = datetime.now() - obj.updatedAt
        if dlt > DLT:
            thumb_url = f"/icloud/thumb?" + urlencode({"id": obj.id, "startRank": obj.startRank})
        return '''<el-image style="width: 100px; height: 100px" src="{}" :preview-src-list="['{}']" lazy></el-image>'''.format(
            thumb_url, thumb_url)

    thumb.short_description = "缩略图"

    def dialog_lists(self, model):
        return MultipleCellDialog([
            ModalDialog(url=f'/static/preview.html?id={urllib.parse.quote(model.id)}&source=IMedia',
                        title=model.filename,
                        cell='<el-link type="primary">预览</el-link>', width="840px", height="600px"),
        ])

    # 这个是列头显示的文本
    dialog_lists.short_description = "预览"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # groupList = []
        # start = queryset[0].startRank
        # group = []
        # n = 0
        # for qs in queryset:
        #     distance = qs.startRank - start
        #     if distance < 100:
        #         group.append(qs)
        #     else:
        #         groupList.append(group)
        #         n += 1
        #         print(n, group[0].startRank, "~", group[-1].startRank, len(group))
        #         group = [qs]
        #         start = qs.startRank
        return queryset

    def get_paginator(self, request, queryset, per_page, orphans=0, allow_empty_first_page=True):
        res = super().get_paginator(request, queryset, per_page, orphans, allow_empty_first_page)
        return res

    # 也可以是方法的形式来返回html
    def get_top_html(self, request):
        return f'''
        <el-collapse accordion>
            <el-collapse-item>
                <template slot="title">
                    同步进度监控<i class="header-icon el-icon-info"></i>
                </template>
                <iframe style="width:100%;height:200px;" src="/static/iMedia_list_top.html"></iframe>
            </el-collapse-item>
        </el-collapse>
        '''

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    @layer(config=get_sync_layer_config)
    @button(type='danger', short_description='从icloud中获取数据', enable=True, confirm="您确定要生成吗？")
    def collect(self, request, queryset):
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
                th = threading.Thread(target=collect_all_medias, args=(_iService,))
                th.start()
                return {
                    'state': True,
                    'msg': f'采集程序已经启动'
                }

    @button(type='warning', short_description='数据迁移', enable=False, confirm="您确定从icloud迁移到本地吗？")
    def migrate(self, request, queryset):
        ids = request.POST.get('ids').replace(" ", "+").split(",")
        objs = IMedia.objects.filter(id__in=ids).all()
        for i, qs in enumerate(objs):
            migrateIcloudToLocal(qs)
        return {
            'state': True,
            'msg': f'迁移开始！'
        }

    @button(type='error', short_description='从iCloud中删除', enable=False, confirm="您确定从icloud迁移到本地吗？")
    def delete(self, request, queryset):
        ids = request.POST.get('ids').replace(" ", "+").split(",")
        objs = IMedia.objects.filter(id__in=ids).all()
        for qs in objs:
            lm = LocalMedia.objects.filter(id=qs.id).first()
            resp = delete_from_icloud(qs, lm)
            return {
                'state': True,
                'msg': resp.text
            }

    def formatter(self, obj, field_name, value):
        # 这里可以对value的值进行判断，比如日期格式化等
        if field_name == "size":
            if value:
                return f"""<span title="{value}">{human_readable_bytes(value)}</span>"""
        if field_name == 'img':
            if value:
                return f"""<img src="{value}" style="height:100px;">"""
        if field_name == "duration":
            if value and value != 0:
                return f"""<span title="{value}">{human_readable_time(value)}</span>"""
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
            'align': 'left'
        },
        'added_date': {
            'width': '180px',
            'align': 'left'
        },
        'thumb': {
            'width': '130px',
            'align': 'center'
        },
        'duration': {
            'width': '130px',
            'align': 'center'
        },
        'createdUserRecordName': {
            'width': '300px',
            'align': 'left'
        },
        'modifiedUserRecordName': {
            'width': '300px',
            'align': 'left'
        },
        'createdDeviceID': {
            'width': '400px',
            'align': 'left'
        },
        'modifiedDeviceID': {
            'width': '400px',
            'align': 'left'
        },
        'locationEnc': {
            'width': '1000px',
            'align': 'left'
        },
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
