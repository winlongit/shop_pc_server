from app.models import db

import datetime

# -> panelContents []中
#       公共属性 sortOrder，picUrl，type。
#       type == 0 || 2 就是表示商品(如果是7幅图中，2表示大图，0表示小图)  必须带productId （picUrl2 picUrl4 是图层叠加效果 可选），
#           通过productId 然后把商品的 productName，subTitle，productImageBig，salePrice 找出来
#       type == 1 就表示是一个链接，同样，必选 fullUrl 作为跳转的目的地址
from app.models.Product import Product


class PanelContent(db.EmbeddedDocument):
    type = db.IntField(verbose_name='条目类型 0轮播图里的商品,2表示陈列的商品，1表示一个链接', required=True)
    sortOrder = db.IntField(verbose_name='顺序', default=9999)
    picUrl = db.StringField(max_length=512, verbose_name='图片地址，必须的')
    fulUrl = db.StringField(max_length=512, verbose_name='如果type==1，外链，这就是必须的')
    product_id = db.ReferenceField(Product, verbose_name='如果type==0||2，这就就是必须的')


# name (左上角显示的标题名),sortOrder 排列顺序 status 是否使用 limitNum 限制数量
# type == 0 表示轮播图 limitNum = 5 最多 5 个图
# type == 1 就是活动版块（4幅图并排排列，没啥看头) limitNum = 4
# type == 2 热门商品（2 幅图 没啥好说的) limitNum = 2
# type == 3 官方精选（就是7幅图，其中1幅大图占2格，6幅占剩下的6格，一起站2行-) limitNum = 7
class HomeFrame(db.Document):
    type = db.IntField(verbose_name='0 表示轮播图 1 就是活动版块 2 热门商品 3 官方精选', required=True)
    name = db.StringField(max_length=64, verbose_name='左上角标题', required=True)
    sortOrder = db.IntField(verbose_name='顺序', default=9999)
    panelContents = db.EmbeddedDocumentListField(PanelContent, required=True, verbose_name='所有条目', default=[])
    status = db.IntField(verbose_name='是否启用,1 启用，0 不启用', required=True, default=1)

    create_time = db.DateTimeField(default=datetime.datetime.utcnow, verbose_name='创建时间')

    def __unicode__(self):
        return str(self.name)
