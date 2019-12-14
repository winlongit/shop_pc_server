#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------

    @   Author  :       pengj
    @   date    :       2019/12/8 14:27
    @   IDE     :       PyCharm
    @   GitHub  :       https://github.com/JackyPJB
    @   Contact :       pengjianbiao@hotmail.com
-------------------------------------------------
    Description :       
-------------------------------------------------
"""
from qcloud_cos import CosConfig, CosS3Client, CosServiceError

__author__ = 'Max_Pengjb'
import base64
import io
import hashlib
from bson import ObjectId
from flask import Blueprint, send_file, request, jsonify, Response

from app import jsonReturn
from app.models.Picture import Picture
from config import load_config
from app.utils.smmsPic import SMMSV2, SmmsError

# 对象存储的信息
Config = load_config()
cos_appid = Config.COS_APPID
cos_secret_id = Config.COS_SECRETID
cos_secret_key = Config.COS_SECRETKEY
cos_region = Config.COS_REGION
cos_bucket = Config.COS_BUCKET
cdn_domain = Config.CDN_DOMAIN
cos_config = CosConfig(Region=cos_region, SecretId=cos_secret_id, SecretKey=cos_secret_key)
# 2. 获取客户端对象
cos_client = CosS3Client(cos_config)

bp = Blueprint('image', __name__, url_prefix="/api/v1/img")


@bp.route('/test')
def get_blank():
    gif = 'R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
    gif_str = base64.b64decode(gif)
    return send_file(io.BytesIO(gif_str), mimetype='image/gif')


# 上传图片，我们这里使用 sm.ms 图传，把传回来的 url 保存在mongodb中
# element ui 的上传图片
@bp.route("/img_upload_ui", methods=['POST'])
def img_upload_ui():
    if 'file' not in request.files:
        return jsonReturn.falseReturn(request.path, '请上传file文件')
    img_obj = request.files.get("file")
    filename = img_obj.filename
    if not filename:
        return jsonReturn.falseReturn(request.path, '请上传file文件')
    img_type = filename[filename.rfind(".") + 1:].lower()
    # print(img_type)
    # pic = Picture(image=img_obj)
    if img_type in Config.ALLOWED_IMAGE:
        try:
            # 这个几把sm.ms一下子不能上传太多图片，简直就是垃圾，这里还是转用 腾讯 的对象存储吧
            # sm_url = SMMSV2.upload(img_obj)
            # print(sm_url)
            # 腾讯 COS , 上传按照 key 值放的，若 key 存在，则就覆盖原来的地址，所以我们这里查询一下数据库中有没有这个文件名吧
            # https://ailemong-1259477036.cos.ap-shanghai.myqcloud.com/44.jpg
            file_MD5 = hashlib.md5(img_obj.read()).hexdigest() + '.' + img_type
            img_url = cdn_domain + file_MD5
            pic = Picture.objects(img_name=file_MD5).first()
            if pic:
                return jsonReturn.falseReturn({'sm_url': img_url}, '该文件已经存在了，如果和你的不同，请修改文件名称')
            # 腾讯 cos python sdk
            img_obj.seek(0)  # 前面计算 md5 的时候已经 read(） 一次了，这里要再读取一次，需要把游标归 0
            cos_client.put_object(Bucket=cos_bucket, Body=img_obj, Key=file_MD5, EnableMD5=False)
            # 保存图片到 mongodb 的 picture 中
            Picture(img_name=file_MD5, url=img_url).save()
            return jsonReturn.trueReturn({'sm_url': img_url}, '上传成功')
        except CosServiceError as e:
            return jsonReturn.falseReturn(e.get_error_msg(), '上传失败')
        except Exception as e:
            return jsonReturn.trueReturn('', '上传失败 ' + str(e))
            # 添加图片，并且 追加一个 content_type 属性进去,回头返回的时候，也好填写 Conten-Type 啊
            # pic.image.put(img_obj, content_type=img_obj.content_type)
            # rs = pic.save()
            # rs.id 是 objectId： Object of type 'ObjectId' is not JSON serializable，所以这里把它转成字符串str
            # TODO 这里先不存在mongodb了，等下再做（防止被图床把图片删了，我们这里再本地也备份一份）
            # pic = Picture(img_name=filename, smms_url='', family="swipers", creator="user open id",img_type=img_type)
        # except SmmsError as se:
        # print(se)
        # return jsonReturn.falseReturn(request.path, str(se))
    else:
        return jsonReturn.falseReturn(request.path, '格式不对，仅支持： ' + str(Config.ALLOWED_IMAGE))


@bp.route("/img_download_ui/<img_id>", methods=['GET', 'POST'])
def img_download_ui(img_id):
    pic = Picture.objects.get(id=ObjectId(img_id))
    # 获取 头像 的 ImageGridFsProxy
    image_gfs_proxy = pic.image
    print(image_gfs_proxy.content_type)
    print(image_gfs_proxy)
    return Response(image_gfs_proxy.read(),
                    content_type="image/jpeg",
                    headers={
                        'Content-Length': image_gfs_proxy.length
                    })
