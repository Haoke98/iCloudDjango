# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/3/19
@Software: PyCharm
@disc:
======================================="""
import logging
from datetime import datetime

from django.contrib import admin
from django.http import JsonResponse
from simplepro.admin import FieldOptions
from simpleui.admin import AjaxAdmin

from utils import icloud
from ..models import AppleId


@admin.register(AppleId)
class AccountAdmin(AjaxAdmin):
    list_display = ['id', 'email', 'tel', 'passwd', 'last2FactorAuthenticateAt', 'last_2fa_time',
                    'isActive', 'lastConfirmedSessionValidityAt', 'maxSessionAge', 'updatedAt',
                    'createdAt']
    fields = ('email', 'tel', 'passwd', 'info')
    actions = ['two_factor_authenticate']

    def async_get_layer_config(self, request, queryset):
        """
        这个方法只有一个request参数，没有其他的入参
        """
        global iService
        qs: AppleId = queryset[0]
        print("被选中的用户名:", qs.username, qs.passwd)
        config = {
            # 弹出层中的输入框配置

            # 这里指定对话框的标题
            'title': '两步验证(Two Factor Authentication)',
            # 提示信息
            'tips': f'账号{qs.username}已经验证过！！！',
            # 确认按钮显示文本
            'confirm_button': '确认提交',
            # 取消按钮显示文本
            'cancel_button': '取消',

            # 弹出层对话框的宽度，默认50%
            'width': '40%',

            # 表单中 label的宽度，对应element-ui的 label-width，默认80px
            'labelWidth': "80px",
            'params': []
        }
        iService = icloud.IcloudService(qs.username, qs.passwd, True)
        print(f"连接成功！[{iService.requires_2fa}, {iService.requires_2sa}]")
        if iService.requires_2fa:
            config["tips"] = f"正在为账号{qs.username}进行两步验证.....\nTwo-factor authentication required."
            config["params"].append({
                # 这里的type 对应el-input的原生input属性，默认为input
                'type': 'input',
                # key 对应post参数中的key
                'key': 'code',
                # 显示的文本
                'label': '验证码',
                # 为空校验，默认为False
                'require': True,
                'extras': {
                    'prefix-icon': 'el-icon-delete',
                    'suffix-icon': 'el-icon-setting',
                    'clearable': True,
                    'placeholder': '请输入在你设备上出现6位验证码'
                }

            })
        else:
            qs.lastConfirmedSessionValidityAt = datetime.now()
            csa = qs.current_session_age
            if csa > qs.maxSessionAge:
                qs.maxSessionAge = csa
            qs.save()

        # elif iService.requires_2sa:
        #     print("进来了")
        #     config[
        #         "tips"] = f"正在为账号{qs.username}进行两步验证.....\nTwo-step authentication required. Your trusted devices are: (Which device would you like to use?)"
        #     # FIXME: 这里的设备无法获取， 估计是icloud升级了接口，而这个依赖库没有更新导致的
        #     devices = iService.trusted_devices
        #     print("守信任设备：", devices)
        #     options = []
        #     for i, device in enumerate(devices):
        #         opt = {
        #             'key': i,
        #             'label': device.get('deviceName', "SMS to %s" % device.get('phoneNumber'))
        #         }
        #         print(opt)
        #         options.append(opt)
        #     config["params"].append({
        #         # 这里的type 对应el-input的原生input属性，默认为input
        #         'type': 'select',
        #         # key 对应post参数中的key
        #         'key': 'device',
        #         # 显示的文本
        #         'label': '受信任设备',
        #         # 为空校验，默认为False
        #         'require': True,
        #         'options': options,
        #         'extras': {
        #             'prefix-icon': 'el-icon-delete',
        #             'suffix-icon': 'el-icon-setting',
        #             'clearable': True,
        #             "placeholder": "请选择受信任设备"
        #         }
        #
        #     })
        # 模拟处理业务耗时
        # 可以根据request的用户，来动态设置返回哪些字段，每次点击都会来获取配置显示
        print(config)
        return config

    def two_factor_authenticate(self, request, queryset):
        post = request.POST
        # 这里获取到数据后，可以做些业务处理
        # post中的_action 是方法名
        # post中 _selected 是选中的数据，逗号分割
        if not post.get('_selected'):
            return JsonResponse(data={
                'status': 'error',
                'msg': '没有选择任何AppleID！'
            })
            # device = devices[device]
            # if not self.send_verification_code(device):
            #     logging.error("Failed to send verification code")
            #
            # code = click.prompt('Please enter validation code')
            # if not self.validate_verification_code(device, code):
            #     logging.info("Failed to verify verification code")
        else:
            code = post.get("code")
            logging.info(f"用户输入的验证码：{code}")
            result = iService.validate_2fa_code(code)
            logging.info("Code validation result: %s" % result)
            if not result:
                logging.error("Failed to verify security code")
                return JsonResponse(data={
                    'status': 'error',
                    'msg': '验证码错误！'
                })
            if not iService.is_trusted_session:
                logging.warning("Session is not trusted. Requesting trust...")
                result = iService.trust_session()
                logging.info("Session trust result %s" % result)
                if not result:
                    logging.error(
                        "Failed to request trust. You will likely be prompted for the code again in the coming weeks")
                    return JsonResponse(data={
                        'status': 'error',
                        'msg': 'Failed to request trust. You will likely be prompted for the code again in the coming weeks！'
                    })
            appleId: AppleId = queryset[0]
            appleId.last2FactorAuthenticateAt = datetime.now()
            appleId.save()
            return JsonResponse(data={
                'status': 'success',
                'msg': '验证成功！'
            })

    two_factor_authenticate.short_description = "两步验证"
    two_factor_authenticate.icon = 'el-icon-view'
    two_factor_authenticate.layer = async_get_layer_config

    def isActive(self, obj: AppleId):
        # FIXME: 修复这里,改成2FA验证是否还有效.
        # if iService is not None:
        #     if obj.username == iService.user.get("accountName"):
        #         return '<el-radio value="1" label="1">已被选中</el-radio>'
        # else:
        return '<el-radio value="1" label="2"><a href="#">点击选择</a></el-radio>'

    isActive.short_description = "被选中"

    fields_options = {
        'id': FieldOptions.UUID,
        'createdAt': FieldOptions.DATE_TIME,
        'updatedAt': FieldOptions.DATE_TIME,
        'two_factor_authenticate': {
            'min_width': '100px',
            'align': 'center',
            'fixed': 'right'
        },
        'email': FieldOptions.EMAIL,
        'tel': FieldOptions.MOBILE,
        'last2FactorAuthenticateAt': FieldOptions.DATE_TIME,
        'last_2fa_time': FieldOptions.DURATION,
        'passwd': FieldOptions.DURATION,
        'lastConfirmedSessionValidityAt': {
            'min_width': "220px",
            'align': 'center'
        },
        'maxSessionAge': FieldOptions.DURATION,
        'isActive': {
            'min_width': '160px',
            'align': 'center'
        },
    }
