from cStringIO import StringIO
import Image, ImageEnhance
LEFT_TOP     = 'lt'
LEFT_BOTTOM  = 'lb'
RIGHT_TOP    = 'rt'
RIGHT_BOTTOM = 'rb'
WIDTH_GRID = 30.0
HIGHT_GRID = 30.0

def mark_layout(im, mark, layout=RIGHT_BOTTOM):
    im_width, im_hight     = im.size[0], im.size[1]
    mark_width, mark_hight = mark.size[0], mark.size[1]
    coordinates = { LEFT_TOP: (int(im_width/WIDTH_GRID),int(im_hight/HIGHT_GRID)),
                    LEFT_BOTTOM: (int(im_width/WIDTH_GRID), int(im_hight - mark_hight - im_hight/HIGHT_GRID)),
                    RIGHT_TOP: (int(im_width - mark_width - im_width/WIDTH_GRID), int(im_hight/HIGHT_GRID)),
                    RIGHT_BOTTOM: (int(im_width - mark_width - im_width/WIDTH_GRID), \
                    int(im_hight - mark_hight - im_hight/HIGHT_GRID)),
                  }
    return coordinates[layout]

def reduce_opacity(mark, opacity):
    assert opacity >= 0 and opacity <= 1
    mark  = mark.convert('RGBA') if mark.mode != 'RGBA' else mark.copy()
    alpha = mark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    mark.putalpha(alpha)
    return mark

def water_mark(img_data, opacity=1):
    img  = Image.open(StringIO(img_data))
    mark = Image.open('/mark/path') # 水印文件可以使用指定路径
    #mark = fs.get(mark_url)
    if not mark:
        return img_data
    mark = Image.open(StringIO(mark))
    if opacity < 1:
        mark = reduce_opacity(mark, opacity)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
        img_format = 'JPEG'
    else:
        img_format = 'PNG'
    # 指定上传图片最大宽度580和高宽600，如超过进行resize
    if img.size[0] > 580:
        img = img.resize((580, img.size[1]/(img.size[0]/580.0)), resample=1)
    if img.size[1] > 600:
        img = img.resize((img.size[0]/(img.size[1]/600.0),600), resample=1)
    layer = Image.new('RGBA', img.size, (0,0,0,0))
    layer.paste(mark, mark_layout(img, mark, layout))
    img = Image.composite(layer, img, layer)
    new_img = StringIO()
    img.save(new_img, img_format, quality=100)
    return new_img.getvalue()

