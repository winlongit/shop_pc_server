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
import base64
import io

from bson import ObjectId
from flask import Blueprint, send_file, request, jsonify, Response

from app import jsonReturn
from app.models.Picture import Picture
from config.default import Config
from app.utils.smmsPic import SMMSV2, SmmsError

__author__ = 'Max_Pengjb'

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
            sm_url = SMMSV2.upload(img_obj)
            print(sm_url)
            # 添加图片，并且 追加一个 content_type 属性进去,回头返回的时候，也好填写 Conten-Type 啊
            # pic.image.put(img_obj, content_type=img_obj.content_type)
            # rs = pic.save()
            # rs.id 是 objectId： Object of type 'ObjectId' is not JSON serializable，所以这里把它转成字符串str
            # TODO 这里先不存在mongodb了，等下再做（防止被图床把图片删了，我们这里再本地也备份一份）
            # pic = Picture(img_name=filename, smms_url='', family="swipers", creator="user open id",img_type=img_type)
            return jsonReturn.trueReturn({'sm_url': sm_url}, '上传文件成功')
        except SmmsError as se:
            # print(se)
            return jsonReturn.falseReturn(request.path, str(se))
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
