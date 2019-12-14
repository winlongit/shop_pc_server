#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------

    @   Author  :       pengj
    @   date    :       2019/12/13 14:00
    @   IDE     :       PyCharm
    @   GitHub  :       https://github.com/JackyPJB
    @   Contact :       pengjianbiao@hotmail.com
-------------------------------------------------
    Description :       首页，home 页的返回
-------------------------------------------------
"""
from bson import ObjectId
from flask import Blueprint, request

from app import jsonReturn
from app.models.HomeFrame import HomeFrame, PanelContent
from app.models.Product import Product
from app.utils import mongo2dict

__author__ = 'Max_Pengjb'

bp = Blueprint('home', __name__, url_prefix="/api/v1/home")


@bp.route("/add_frame", methods=['POST'])
def add_frame():
    # 轮播图：2240 x 1108
    req_json = request.json
    if not req_json:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    # TODO 一些合法性验证需要增加，这里不管了
    frame_type = req_json.get('type')
    name = req_json.get('name')
    sortOrder = req_json.get('sortOrder')
    panelContents = req_json.get('panelContents')
    if not all([frame_type is not None, name, panelContents]):
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    panelContentsDb = []
    for panelContent in panelContents:
        panelContent_type = panelContent.get('type')
        panelContent_sortOrder = panelContent.get('sortOrder')
        panelContent_picUrl = panelContent.get('picUrl')
        panelContent_fulUrl = panelContent.get('fulUrl')
        panelContent_product_id = panelContent.get('productId')
        if not all([panelContent_type is not None, panelContent_picUrl]):
            return jsonReturn.falseReturn(request.path, '请上传必要参数')
        onePanelContent = PanelContent(type=panelContent_type, sortOrder=panelContent_sortOrder,
                                       picUrl=panelContent_picUrl, fulUrl=panelContent_fulUrl)
        if panelContent_product_id:
            onePanelContent.product_id = ObjectId(panelContent_product_id)
        panelContentsDb.append(onePanelContent)
    home_frame = HomeFrame(type=frame_type, name=name, sortOrder=sortOrder, panelContents=panelContentsDb).save()
    return jsonReturn.trueReturn(home_frame, 'ok')


# name (左上角显示的标题名),sortOrder 排列顺序 status 是否使用 limitNum 限制数量
# type == 0 表示轮播图 limitNum = 5 最多 5 个图
# type == 1 就是活动版块（4幅图并排排列，没啥看头) limitNum = 4
# type == 2 热门商品（2 幅图 没啥好说的) limitNum = 2
# type == 3 官方精选（就是7幅图，其中1幅大图占2格，6幅占剩下的6格，一起站2行-) limitNum = 7
# -> panelContents []中
#       公共属性 sortOrder，picUrl，type。
#       type == 0 || 2 就是表示商品(如果是7幅图中，2表示大图，0表示小图)   必须带productId （picUrl2 picUrl4 是图层叠加效果 可选），
#           通过productId 然后把商品的 name，title，swiper_pics[]，cur_rice 找出来
#       type == 1 就表示是一个链接，同样，必选 fullUrl 作为跳转的目的地址
#
# 返回
@bp.route("/get_frame", methods=['GET'])
def home():
    # 轮播图：2240 x 1108

    home_frames = HomeFrame.objects(status=1).order_by('sortOrder').all()
    print(home_frames)
    if not home_frames:
        return jsonReturn.trueReturn('', '当前没有数据')
    res = [mongo2dict.m2d(home_frame) for home_frame in home_frames]
    for frame in res:
        for panelContent in frame['panelContents']:
            # 是商品的时候,就要去 Product 中把商品的信息取出来
            if panelContent['type'] == 0 or panelContent['type'] == 2:
                print(panelContent)
                print(type(panelContent))
                prod = Product.objects(id=panelContent.pop('product_id')).first()
                # 合并两个 dict
                panelContent.update(mongo2dict.m2d(prod))
                print(panelContent)
    print(res)
    return jsonReturn.trueReturn(res, 'ok')
    # return jsonify({"success": True, "message": "success", "code": 200, "timestamp": 1572182342709, "result": [
    #     {"id": 7, "name": "轮播图", "type": 0, "sortOrder": 0, "position": 0, "limitNum": 5, "status": 1, "remark": "",
    #      "created": 1523766787000, "updated": 1523766787000, "panelContents": [
    #         {"id": 70, "panelId": 7, "type": 0, "productId": 150635087972564, "sortOrder": 1, "fullUrl": "",
    #          "picUrl": "https://api.ai2hit.com/static/upload/201910302141432598.png",
    #          "picUrl2": "",
    #          "picUrl3": "", "created": 1569839898000,
    #          "updated": 1569843454000, "salePrice": 1.00, "productName": "支付测试商品 IPhone X 全面屏 全面绽放",
    #          "subTitle": "此仅为支付测试商品 拍下不会发货", "productImageBig": "https://i.loli.net/2019/09/30/CAZ6QrXPBoh5aIT.png"},
    #         {"id": 33, "panelId": 7, "type": 0, "productId": 150642571432835, "sortOrder": 2, "fullUrl": "",
    #          "picUrl": "https://resource.smartisan.com/resource/4921019f885a28b0c1f8161646dfc395.png?x-oss-process=image/format,jpg/quality,Q_100",
    #          "picUrl2": "",
    #          "picUrl3": "", "created": 1523970502000,
    #          "updated": 1524192439000, "salePrice": 1.00, "productName": "捐赠商品", "subTitle": "您的捐赠将用于本站维护 给您带来更好的体验",
    #          "productImageBig": "https://i.loli.net/2018/11/04/5bdeba4028e90.png"},
    #         {"id": 34, "panelId": 7, "type": 0, "productId": 150635087972564, "sortOrder": 3, "fullUrl": None,
    #          "picUrl": "https://img12.360buyimg.com/cms/jfs/t1/18904/30/10423/567680/5c87148dE406015ca/a4b15b221755ccf1.jpg",
    #          "picUrl2": "", "picUrl3": "",
    #          "created": 1523970510000, "updated": 1523970512000, "salePrice": 1.00,
    #          "productName": "支付测试商品 IPhone X 全面屏 全面绽放", "subTitle": "此仅为支付测试商品 拍下不会发货",
    #          "productImageBig": "https://img12.360buyimg.com/cms/jfs/t1/18904/30/10423/567680/5c87148dE406015ca/a4b15b221755ccf1.jpg"}]},
    #     {"id": 8, "name": "活动版块", "type": 1, "sortOrder": 1, "position": 0, "limitNum": 4, "status": 1, "remark": "",
    #      "created": 1523790300000, "updated": 1523790300000, "panelContents": [
    #         {"id": 25, "panelId": 8, "type": 0, "productId": 150642571432835, "sortOrder": 1,
    #          "fullUrl": "https://www.smartisan.com/jianguo3-accessories",
    #          "picUrl": "https://api.ai2hit.com/static/upload/201911092059359158.jpg", "picUrl2": None,
    #          "picUrl3": None, "created": 1523790463000, "updated": 1524151234000, "salePrice": 1.00,
    #          "productName": "捐赠商品", "subTitle": "您的捐赠将用于本站维护 给您带来更好的体验",
    #          "productImageBig": "https://resource.smartisan.com/resource/6/610400xinpinpeijian.jpg"},
    #         {"id": 26, "panelId": 8, "type": 0, "productId": 150635087972564, "sortOrder": 2,
    #          "fullUrl": "https://www.smartisan.com/service/#/tradein",
    #          "picUrl": "https://api.ai2hit.com/static/upload/201911092100205673.jpg", "picUrl2": None,
    #          "picUrl3": None, "created": 1523790480000, "updated": 1524151248000, "salePrice": 1.00,
    #          "productName": "支付测试商品 IPhone X 全面屏 全面绽放", "subTitle": "此仅为支付测试商品 拍下不会发货",
    #          "productImageBig": "https://resource.smartisan.com/resource/6/610400yijiuhuanxin.jpg"},
    #         {"id": 27, "panelId": 8, "type": 0, "productId": 150642571432835, "sortOrder": 3,
    #          "fullUrl": "https://www.smartisan.com/category?id=69",
    #          "picUrl": "https://api.ai2hit.com/static/upload/201911092101076456.jpg", "picUrl2": None,
    #          "picUrl3": None, "created": 1523790504000, "updated": 1524151261000, "salePrice": 1.00,
    #          "productName": "捐赠商品", "subTitle": "您的捐赠将用于本站维护 给您带来更好的体验",
    #          "productImageBig": "https://resource.smartisan.com/resource/4/489673079577637073.png"},
    #         {"id": 28, "panelId": 8, "type": 0, "productId": 150635087972564, "sortOrder": 4,
    #          "fullUrl": "https://www.smartisan.com/",
    #          "picUrl": "https://api.ai2hit.com/static/upload/201911092100205673.jpg", "picUrl2": None,
    #          "picUrl3": None, "created": 1523790538000, "updated": 1524151273000, "salePrice": 1.00,
    #          "productName": "支付测试商品 IPhone X 全面屏 全面绽放", "subTitle": "此仅为支付测试商品 拍下不会发货",
    #          "productImageBig": "https://resource.smartisan.com/resource/fe6ab43348a43152b4001b4454d206ac.jpg"}]},
    #
    #     {"id": 1, "name": "热门商品", "type": 2, "sortOrder": 2, "position": 0, "limitNum": 3, "status": 1, "remark": "",
    #      "created": 1524066553000, "updated": 1523790316000, "panelContents": [
    #         {"id": 22, "panelId": 1, "type": 0, "productId": 150642571432848321, "sortOrder": 1, "fullUrl": None,
    #          "picUrl": "https://api.ai2hit.com/static/upload/201911092052302994.png", "picUrl2": None, "picUrl3": None,
    #          "created": 1508682391000, "updated": 1508682391000, "salePrice": 1.00,
    #          "productName": "仁医师马油护手霜50ml", "subTitle": "防止肌肤干燥、保持双手滋润亮白的肌肤深层滋养马油乳木果护手霜",
    #          "productImageBig": "https://api.ai2hit.com/static/upload/201911092052302994.png"},
    #         {"id": 23, "panelId": 1, "type": 0, "productId": 150642571432835, "sortOrder": 2, "fullUrl": "",
    #          "picUrl": "https://api.ai2hit.com/static/upload/201911092053116217.png", "picUrl2": None, "picUrl3": None,
    #          "created": 1508682400000, "updated": 1523969975000, "salePrice": 1.00, "productName": "仁医师马油酵素洗面霜100ml",
    #          "subTitle": "清洁毛孔 保湿不紧绷 添加酵素精华的马油酵素洗面霜",
    #          "productImageBig": "https://api.ai2hit.com/static/upload/201911092053116217.png"}]},
    #
    #     {"id": 2, "name": "官方精选", "type": 3, "sortOrder": 3, "position": 0, "limitNum": 8, "status": 1, "remark": "",
    #      "created": None, "updated": 1524108059000, "panelContents": [
    #         {"id": 29, "panelId": 2, "type": 2, "productId": 15064257143284811, "sortOrder": 0, "fullUrl": "",
    #          "picUrl": "https://img11.360buyimg.com/n1/jfs/t26305/153/1540992424/242754/d3070cc9/5bed227aNba46b4d2.jpg",
    #          "picUrl2": None,
    #          "picUrl3": None, "created": 1523794475000, "updated": 1524195687000, "salePrice": 1999.00,
    #          "productName": "五谷扁粮饭", "subTitle": "生态五谷扁粮，家庭营养主食",
    #          "productImageBig": "https://img11.360buyimg.com/n1/jfs/t26305/153/1540992424/242754/d3070cc9/5bed227aNba46b4d2.jpg"},
    #         {"id": 8, "panelId": 2, "type": 0, "productId": 150642571432836333, "sortOrder": 1, "fullUrl": "",
    #          "picUrl": "https://api.ai2hit.com/static/upload/201911092039474228.jpg", "picUrl2": None,
    #          "picUrl3": None, "created": 1506330228000, "updated": 1524151406000, "salePrice": 49.00,
    #          "productName": "溯源码完美盏燕窝", "subTitle": "正规溯源码天然白燕盏印，尼孕纯净雨林，优等干燕窝",
    #          "productImageBig": "https://api.ai2hit.com/static/upload/201911092039474228.jpg"},
    #         {"id": 9, "panelId": 2, "type": 0, "productId": 150642571432836222, "sortOrder": 2, "fullUrl": "",
    #          "picUrl": "https://api.ai2hit.com/static/upload/201911092038424695.jpg", "picUrl2": None,
    #          "picUrl3": None, "created": 1506330275000, "updated": 1524192497000, "salePrice": 79.00,
    #          "productName": "仁师傅酵素梅", "subTitle": "採用特選大顆成熟的梅子，以低糖、低鹽，烘乾而成，淡淡梅香微甜不膩",
    #          "productImageBig": "https://api.ai2hit.com/static/upload/201911092038424695.jpg"},
    #         {"id": 14, "panelId": 2, "type": 0, "productId": 150642571432836123, "sortOrder": 3, "fullUrl": "",
    #          "picUrl": "https://api.ai2hit.com/static/upload/201911092037487244.jpg", "picUrl2": None,
    #          "picUrl3": None, "created": 1508681641000, "updated": 1524192509000, "salePrice": 29.00,
    #          "productName": "仁师傅旗鱼松（金枪鱼）", "subTitle": "严选上等新鲜黑旗鱼胸腹部位，含有丰富鱼肉纤维口感香酥带嚼勁，色泽金黄、入口即化",
    #          "productImageBig": "https://api.ai2hit.com/static/upload/201911092037487244.jpg"},
    #         {"id": 15, "panelId": 2, "type": 0, "productId": 150642571432840, "sortOrder": 4, "fullUrl": "",
    #          "picUrl": "https://api.ai2hit.com/static/upload/201911092036038028.jpg", "picUrl2": None,
    #          "picUrl3": None, "created": 1508681692000, "updated": 1524192523000, "salePrice": 89.00,
    #          "productName": "仁师傅眷村风味牛肉面", "subTitle": "细火慢炖汤头清新浓郁，令人回味无穷",
    #          "productImageBig": "https://api.ai2hit.com/static/upload/201911092036038028.jpg"},
    #         {"id": 16, "panelId": 2, "type": 0, "productId": 150642571432841, "sortOrder": 5, "fullUrl": "",
    #          "picUrl": "https://api.ai2hit.com/static/upload/201911092033162363.png", "picUrl2": None,
    #          "picUrl3": None, "created": 1508681751000, "updated": 1524192542000, "salePrice": 49.00,
    #          "productName": "草本营养餐", "subTitle": "改变膳食结构，回归自然养生",
    #          "productImageBig": "https://api.ai2hit.com/static/upload/201911092033162363.png"},
    #         {"id": 17, "panelId": 2, "type": 0, "productId": 150642571432842444, "sortOrder": 6, "fullUrl": "",
    #          "picUrl": "https://api.ai2hit.com/static/upload/201911092040318000.jpg", "picUrl2": None,
    #          "picUrl3": None, "created": 1508681821000, "updated": 1524192557000, "salePrice": 79.00,
    #          "productName": "上等文山三七", "subTitle": "有机好三七，来自举世公认的最好的三七产地文山",
    #          "productImageBig": "https://api.ai2hit.com/static/upload/201911092040318000.jpg"}]}
    # ]})
