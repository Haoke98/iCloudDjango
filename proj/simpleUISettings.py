from . import _STATIC_URL
# SIMPLE UI config.
# SIMPLEUI_DEFAULT_THEME = 'x-green.css'

SIMPLEUI_ICON = {
    'iCloud媒体': 'fas fa-phone-square',
    'iCloud相册': 'fas fa-warehouse',
    '本地资源': 'fas fa-cubes',
}
SIMPLEUI_CONFIG = {
    # 在自定义菜单的基础上保留系统模块
    'system_keep': True,
    'dynamic': False,
    'menus': [
        {
            'name': 'GitHub',
            'icon': 'fas fa-code',
            'url': 'https://haoke98.github.io/AllKeeper/',
            'codename': 'community'
        },
        {
            'name': 'Bug反馈',
            'icon': 'fas fa-bug',
            'url': 'https://github.com/Haoke98/AllKeeper/issues',
            'codename': 'bug_trace',
            'newTab': True
        },
        {
            'name': '依赖',
            'icon': 'fas fa-project-diagram',
            'codename': 'product',
            'models': [
                {
                    'name': 'DjangoAsyncAdmin',
                    'codename': 'django_async_admin',
                    'icon': 'fas fa-bug',
                    'models': [
                        {
                            'name': '文档',
                            'url': 'https://haoke98.github.io/DjangoAsyncAdmin/'
                        }, {
                            'name': 'Github',
                            'url': 'https://github.com/Haoke98/DjangoAsyncAdmin'
                        }
                    ]
                }, {
                    'name': '图标',
                    'url': 'https://fontawesome.com/',  # TODO：后期把这个改成一个单独的页面，里面渲染出所有能够调用的图标，外加图标检索功能
                    'icon': 'fas fa-icons',
                    'codename': 'icon',
                    'newTab': True
                }, {
                    'name': '图片转换器',
                    'url': 'https://convert.72wo.com',
                    'icon': 'fab fa-github',
                    'codename': 'convert',
                    'newTab': True
                }, {
                    'name': '全文检索',
                    'url': 'https://github.com/sea-team/gofound',
                    'icon': 'fab fa-github',
                    'codename': 'gofound',
                    'newTab': True
                }
            ]
        }
    ]
}

SIMPLEUI_LOGO = _STATIC_URL+'img/41166dada6559cb93c7a4ff0ea681e52.png'
SIMPLEUI_HOME_INFO = False  # 首页上的simpleUI的版本信息板块。
SIMPLEUI_ANALYSIS = False  # 收集信息（TODO：不太好，等正式上线后建议关闭；否则出现信息泄露）
