# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/3/19
@Software: PyCharm
@disc:
======================================="""
import datetime

from celery import shared_task, current_task

from icloud.services import insert_or_update_media, create_icloud_service


@shared_task(soft_time_limit=3600, time_limit=7200)
def sync_list(apple_id: str, *args, **kwargs):
    """
    同步iMedia
    :param apple_id: 苹果🍎ID
    :param args:
    :param kwargs:
    :return:
    """
    # TODO: 实现传惨传cookie文件或者cookie内容,来实现不同的地方免登录操作( 共享cookie )
    print(f"任务已经启动....{apple_id}")
    requires_2fa, iService = create_icloud_service(apple_id)
    if requires_2fa:
        return {"msg": "该AppleID需要进行2FA验证", "appleId": apple_id}
    # TODO: 实现对不同的相册进行iMedia的同步, 选那个相册用参数来控制
    # for album in albums:
    #     photos = iService.photos.albums[album.name]
    #     total = len(photos)
    # if album.count == total:
    #     print(f"{album.name}: 无需同步跳过")
    #     continue
    # for i, p in enumerate(photos):
    #     th = threading.Thread(target=collect, args=(p, album, i, total))
    #     th.start()
    # album.agg()
    # album.save()
    # target_photo = None
    print("iService:", iService)
    _, TOTAL = iService.media_total()
    medias = iService.photos.all
    for i, photo in enumerate(medias):
        insert_or_update_media(i, photo, iService.user.get("accountName"))
        # 更新任务进度
        # TODO: 这里可以实时统计一下每次同步中同步了多少个视频?多少个图片之类的
        current_task.update_state(state='PROGRESS', total=TOTAL,
                                  processed=i + 1,
                                  extra_process_info={})
    return {"msg": "ok"}
