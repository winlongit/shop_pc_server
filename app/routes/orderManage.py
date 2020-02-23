#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------

    @   Author  :       pengj
    @   date    :       2019/12/10 20:46
    @   IDE     :       PyCharm
    @   GitHub  :       https://github.com/JackyPJB
    @   Contact :       pengjianbiao@hotmail.com
-------------------------------------------------
    Description :       订单管理
-------------------------------------------------
"""
from bson import ObjectId
from wechatpy.exceptions import InvalidSignatureException

from app.models.Cart import Cart
from app.models.Product import Product
from app.models.User import User
from app.models.UserOrder import UserOrder, ProductOrder
from app.utils import mongo2dict
from config import load_config

__author__ = 'Max_Pengjb'

from flask import request, Blueprint, current_app
from app import jsonReturn

from wechatpy import WeChatPay

# PostForm = model_form(User)
bp = Blueprint('order', __name__, url_prefix="/api/v1/order")
# 微信的签名逻辑需要注意：
#
#     商户密钥不参与字典序排序
#     md5后需要转大写
#     参与排序的字典名要与微信的文档严格保持一致
Config = load_config()
wx_id = Config.WX_APPID
mch_id = Config.MCH_ID
mch_key = Config.MCH_KEY
# 这里吃的大亏，回调地址不能用 https ， fuck
http_root = Config.HTTP_ROOT
notify_url = http_root + '/api/v1/order/notifyurl'
# 通过 wechatpy 初始化一个支付的接口
wx_pay = WeChatPay(appid=wx_id, mch_id=mch_id, mch_key=mch_key, api_key=mch_key)


@bp.route('/new_order', methods=['POST'])
def new_order():
    # 提交订单，生成一个订单号和一个微信支付的 code 供前端生成支付二维码使用
    req_json = request.json
    if not req_json:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    user_id = req_json.get('userId')
    goodsList = req_json.get('goodsList')
    orderTotal = float(req_json.get('orderTotal'))
    userName = req_json.get('userName')
    streetName = req_json.get('streetName')
    tel = req_json.get('tel')
    if not all([user_id, goodsList, orderTotal, userName, streetName, tel]):
        return jsonReturn.falseReturn(request.path, '请上传必要参数user_id, goodsList, orderTotal, userName, streetName, tel')
    # 检查用户 Id 是不是有效用户
    user = User.objects(id=ObjectId(user_id)).first()
    if not user:
        return jsonReturn.falseReturn('', '用户id有问题，找不到这个问题')
    # 查询商品，比较价格，看看前端传过来的价格有没有问题
    total_fee = 0
    embeddedGoodsList = []
    cartGoodList = []
    for good in goodsList:
        productId = good.get('productId')
        name = good.get('productName')
        title = good.get('title')
        salePrice = float(good.get('salePrice'))
        print('type(salePrice)', type(salePrice))
        productNum = good.get('productNum')
        productImg = good.get('productImg')
        print(type(productNum))
        if not all([productId, productNum, productImg, name, salePrice]):
            return jsonReturn.falseReturn(request.path,
                                          '提交的商品列表数据中，每个都需要 productId, productNum, productImg, name, salePrice')
        # 查询数据库中的商品，对比价格，看看前端有没有搞鬼
        cartGood = Product.objects(id=ObjectId(productId)).first()
        if not cartGood:
            return jsonReturn.falseReturn('', name + '这个商品有问题，数据库中么有他')
        # 加到这个list中，回头生成好了的话，就在购物车中把这些都删了
        cartGoodList.append(cartGood)
        if cartGood['cur_price'] != int(salePrice * 100):
            return jsonReturn.falseReturn('', name + '这个商品价格问题，数据库中和他不一样')
        # 计算总价
        total_fee += cartGood['cur_price'] * productNum
        # 这里看样子是没有问题了，那就把商品构建一个 ProductOrder 的 EmbeddedDocument
        productOrder = ProductOrder(productId=productId, name=name, title=title, salePrice=cartGood['cur_price'],
                                    productNum=productNum, productImg=productImg)
        embeddedGoodsList.append(productOrder)
    # 检查总价对不对
    if total_fee != int(orderTotal * 100):
        return jsonReturn.falseReturn('', '这个总价有问题啊，数据库算出来的和你不一样')
    # 不是 VIP 的首次消费需要满 288
    if not user.vip and total_fee < 28800:
        from flask import jsonify
        return jsonify({"status": "failed", "message": '您是非会员，首次消费需满 288 元', "code": "500", "success": False})
    try:
        user_order = UserOrder(user_id=user, goodsList=embeddedGoodsList, total_fee=total_fee, userName=userName,
                               tel=tel,
                               streetName=streetName).save()
    except Exception as e:
        return jsonReturn.falseReturn('', '保存到mongodb出错了：' + str(e))
    # 这里还有一个 请求 sign 的构造过程， wechatpy 都已经封装好了
    rs = wx_pay.order.create(trade_type="NATIVE",
                             total_fee=total_fee,  # 订单总金额，单位为分
                             notify_url=notify_url,  # 异步接收微信支付结果通知的回调地址，通知url必须为外网可访问的 http 地址，不能是 https ，不能携带参数。
                             # user_id=request.args.get("openid"),  # 小程序appid下的唯一标识 trade_type=JSAPI和sub_appid已设定，此参数必传
                             body="乐盟商城",  # 商品详细描述，对于使用单品优惠的商户，该字段必须按照规范上传
                             out_trade_no=str(user_order.id),  # 商户系统内部订单号，要求32个字符内，只能是数字、大小写字母_-|*且在同一个商户号下唯一
                             )
    # 微信统一下单接口 https://pay.weixin.qq.com/wiki/doc/api/native.php?chapter=9_1
    # native 支付说明 https://pay.weixin.qq.com/wiki/doc/api/native.php?chapter=6_5
    # 请求支付二维码的code_url成功 return_code=SUCCESS && result_code=SUCCESS
    if rs['return_code'] == 'SUCCESS' and rs['result_code'] == 'SUCCESS':
        # code_url 还需要存入数据库中，再次支付的时候还要调用一下
        user_order.code_url = rs['code_url']
        user_order.save()
        # 通过 userId 来查找他对应的购物车，把这些提交过来的商品在购物车中删掉
        Cart.objects(user_id=user, product_id__in=cartGoodList).delete()
        # 获取 code_url 把这个code返回给前端，让前端生成 qrcode
        return jsonReturn.trueReturn({'order_id': str(user_order.id), 'code_url': rs['code_url']}, 'ok')
    else:
        return jsonReturn.falseReturn(rs, '请求统一下单接口失败')


@bp.route("/query_order", methods=["GET"])
def query_order():
    req_json = request.args
    if not req_json:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    order_id = req_json.get('orderId')
    if not order_id:
        return jsonReturn.falseReturn(request.path, '请上传必要参数orderId')
    try:
        user_order = UserOrder.objects(id=ObjectId(order_id)).first()
        return jsonReturn.trueReturn(mongo2dict.m2d(user_order), 'ok')
    except Exception as e:
        return jsonReturn.falseReturn(request.path, str(e))


@bp.route("/del_order", methods=["POST"])
def del_order():
    req_json = request.json
    if not req_json:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    order_id = req_json.get('orderId')
    if not order_id:
        return jsonReturn.falseReturn(request.path, '请上传必要参数orderId')
    try:
        user_order = UserOrder.objects(id=ObjectId(order_id)).delete()
        return jsonReturn.trueReturn(user_order, 'ok')
    except Exception as e:
        return jsonReturn.falseReturn(request.path, str(e))


# 通过用户id获取该用户下的所有订单
@bp.route("/get_orders", methods=["GET"])
def get_order():
    req_json = request.args
    if not req_json:
        return jsonReturn.falseReturn(request.path, '请上传必要参数')
    user_id = req_json.get('userId')
    if not user_id:
        return jsonReturn.falseReturn(request.path, '请上传必要参数userId')
    page = req_json.get('page', 1)
    page_size = req_json.get('size', 20)
    try:
        query_set = UserOrder.objects(user_id=ObjectId(user_id)).paginate(page=int(page), per_page=int(page_size))
        res = {
            'page': query_set.page,
            'page_size': query_set.per_page,
            'total': query_set.total,
            'data': query_set.items
        }
        return jsonReturn.trueReturn(res, 'ok')
    except Exception as e:
        return jsonReturn.falseReturn(request.path, str(e))


# 微信推送消息是XML格式，使用wechatpy的parse_payment_result方法可以将结果转化成OrderedDict类型，且帮你做好了验签。
@bp.route("/notifyurl", methods=["GET", "POST"])
def get_notify_url():
    notify_data = request.data
    print(notify_data)
    try:
        # parse_payment_result 有对通知合法性的验证， 通过 sign 来对比
        data = wx_pay.parse_payment_result(notify_data)
        # 通知的格式 https://pay.weixin.qq.com/wiki/doc/api/native.php?chapter=9_7&index=8
        print(data)
        if data['return_code'] == 'SUCCESS' and data['result_code'] == 'SUCCESS':
            order_id = data['out_trade_no']
            total_fee = data['total_fee']
            try:
                # 这里加个 total_fee=total_fee 是为了验证支付的金额和我们应该收到的金额是一样的
                UserOrder.objects(id=ObjectId(order_id), total_fee=total_fee).update_one(ischeck=True, status='支付成功')
                user = UserOrder.objects(id=UserOrder.user_id)
                # 这个付款成功，如果不是 VIP 但是付款成功了，肯定是满足付款条件了，那也升级为 VIP
                if not user.vip:
                    user.vip = True
                    user.save()
                # 然后就可以根据返回的结果，处理之前的订单了。
                # TODO 写上处理结果的逻辑。存储数据库之类的
                # 唯一需要注意的一点，微信推送消息后，需要给微信服务器返回一个消息：
                return "<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"
            except Exception as e:
                print(e)
    except InvalidSignatureException as e:
        print(e)
        return jsonReturn.falseReturn('', '你个骗子，想拿个假的通知骗我？')


"""  之前没用 wechatpy ， 自己手动写的方法， 能用，但是有现成的封装好的不是更好吗
    感谢 wechatpy 的作者 https://wechatpy.readthedocs.io/zh_CN/master/pay.html#module-wechatpy.pay
# 生成随机字符串，长度要求在32位以内
def creat_nonce_str():
    ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
    ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ascii_letters = ascii_lowercase + ascii_uppercase
    digits = '0123456789'
    char = ascii_letters + digits
    return "".join(random.choice(char) for _ in range(16))
to_uft8 = lambda x: x.encode("utf-8") if isinstance(x, str) else x
# 签名所有发送或者接收到的数据为集合M,将集合M内非空参数值的参数按照参数名ASCII码从小到大排序
# URL键值对的格式（即key1 = value1 & key2 = value2…）拼接成字符串stringA
# tringA最后拼接上key得到stringSignTemp字符串，并对stringSignTemp进行MD5运算，
# 再将得到的字符串所有字符转换为大写
def sign(pay_data):
    stringA = '&'.join(["{0}={1}".format(k, pay_data.get(k)) for k in sorted(pay_data)])
    stringSignTemp = '{0}&key={1}'.format(stringA, mp_mch_key)
    return hashlib.md5(to_uft8(stringSignTemp)).hexdigest().upper()
# 生成xml格式发送
def to_xml(arr):
    xml = ["<xml>"]
    for k, v in arr.items():
        if v.isdigit():
            xml.append("<{0}>{1}</{0}>".format(k, v))
        else:
            xml.append("<{0}><![CDATA[{1}]]></{0}>".format(k, v))
    xml.append("</xml>")
    return "".join(xml)
# 每个element对象都具有以下属性：
# 1.tag：string对象，表示数据代表的种类。
# 2.attrib：dictionary对象，表示附有的属性。
# 3.text：string对象，表示element的内容。
# 4.tail：string对象，表示element闭合之后的尾迹。
# 例如：< tag attrib1 = 1 > text < / tag > tail
def to_dict(content):
    raw = {}
    root = eTree.fromstring(content)
    for child in root:
        raw[child.tag] = child.text
    return raw
# 实行发送请求，并且得到返回结果
def pay_send_get(url, xml_data):
    req = urllib.request.Request(url, bytes(xml_data, encoding="utf8"))
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler())
    # try:
    # resp = urllib.request.urlopen(url,bytes(data, encoding="utf8"), timeout=20)
    resp = opener.open(req, timeout=20).read()
    print("统一下单返回：")
    print(resp)
    # # except urllib.request.HTTPSHandler as e:
    # #     resp = e
    res_data = Map(to_dict(resp))
    # 微信服务器返回的xml里有:
    # 返回状态码：return_code
    # 此字段是通信标识，非交易标识，交易是否成功需要查看result_code来判断
    # 返回信息:return_msg     如果无错为空
    if res_data.return_code == "FAIL":
        # raise PayError(data.return_msg)
        raise res_data.return_msg
    # 得到了返回的xml，并且转成dict类型
    return res_data
# python小程序付款参考： https://www.jianshu.com/p/07ed48e4a50b
@bp.route("/reqPay1", methods=["POST", "GET"])
def get_json():
    spbill_create_ip = request.remote_addr
    openid = request.args.get("openid")
    print(openid)
    data = {
        'appid': mp_id,  # 微信分配的小程序ID,擦嘞，这里的appid 的 i 是小写
        'mch_id': mp_mch_id,  # 微信支付分配的商户号
        'nonce_str': creat_nonce_str(),  # 随机字符串，长度要求在32位以内
        'body': '测试',  # 商品详细描述，对于使用单品优惠的商户，该字段必须按照规范上传
        'out_trade_no': str(int(time.time())),  # 商户系统内部订单号，要求32个字符内，只能是数字、大小写字母_-|*且在同一个商户号下唯一
        'total_fee': '1',  # 订单总金额，单位为分
        'spbill_create_ip': spbill_create_ip,  # 支持IPV4和IPV6两种格式的IP地址。调用微信支付API的机器IP 支付提交用户端ip，得到终端ip
        'notify_url': notify_url,  # 异步接收微信支付结果通知的回调地址，通知url必须为外网可访问的url，不能携带参数。
        'attach': '{"msg": "自定义数据"}',  # 附加数据，在查询API和支付通知中原样返回，可作为自定义参数使用。
        'trade_type': "JSAPI",  # 小程序取值如下：JSAPI
        'openid': openid  # 用户标识 当 trade_type=JSAPI，此参数必传，用户在商户appid下的唯一标识。
    }
    get_sign = sign(data)
    print("第一次搞到sign：")
    print(get_sign)
    data["sign"] = get_sign
    print(data)
    get_xml = to_xml(data)
    print(get_xml)
    res_data = pay_send_get("https://api.mch.weixin.qq.com/pay/unifiedorder", get_xml)
    print(res_data)
    # 得到prepay_id 微信生成的预支付会话标识，用于后续接口调用中使用，该值有效期为2小时
    prepay_id = res_data["prepay_id"]
    # 生成wx.requestPayment小程序中的paySign签名: https://pay.weixin.qq.com/wiki/doc/api/wxa/wxa_api.php?chapter=7_7
    paySign_data = {
        'appId': mp_id,  # 微信分配的小程序ID 擦嘞，这里的appId 的 I 是大写
        'timeStamp': str(int(time.time())),  # 时间戳从1970年1月1日00:00:00至今的秒数,即当前的时间
        'nonceStr': creat_nonce_str(),  # 随机字符串，不长于32位
        'package': 'prepay_id={0}'.format(prepay_id),
        # 统一下单接口返回的 prepay_id 参数值，提交格式如：prepay_id=wx2017033010242291fcfe0db70013231072
        'signType': 'MD5'  # 签名类型，默认为MD5
    }
    # 生成 sign 签名
    get_paySign = sign(paySign_data)
    print("这次搞到的sign" + get_paySign)
    paySign_data["paySign"] = get_paySign
    print(paySign_data)
    return jsonify(paySign_data)

@bp.route("/notifyurl", methods=["GET", "POST"])
def get_notify_url():
    print("yes,here")
    allthings = request.stream.read()
    print(allthings)
    respData = {'return_code': "SUCCESS"}
    # respData = arrayToXml(respData)
    return to_xml(respData)
"""
