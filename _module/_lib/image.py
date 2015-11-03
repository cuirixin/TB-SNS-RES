#-*- coding:utf8 -*-

'''
Created on 2014-4-19
@author: cuirixin
'''
import os
import config_base
try:
    from PIL import Image,ImageFont,ImageDraw
except:
    import Image,ImageFont,ImageDraw
    
class ImageGenerate():
    
    @staticmethod
    def generate_thumb(uploadPath, _uuid):
        tmp_file = uploadPath+_uuid+".jpg"
        
        file_1000 = uploadPath+_uuid+".jpg"
        file_120 = uploadPath+_uuid+"_120.jpg"
        image_one = Image.open(tmp_file)
        image_one = image_one.convert('RGB')
        o_width, o_height = image_one.size
        o_maxsize = max(o_width, o_height)
        scale = 1.0
        
        if os.path.isfile(file_120): 
            return
        
        if o_maxsize <= 120: #最大尺寸小于120 保存原图三份
            image_one.save(file_120)
        elif 400 <o_maxsize<= 800: #最大尺寸>400  <=800 保存原图两份,并压缩到120一份
            scale = float(o_maxsize)/120
            newWidth, newHeight = int(round(o_width / scale)),int(round(o_height/ scale))
            image_one.thumbnail((newWidth,newHeight),resample=1)
            image_one.save(file_120)
        else:#>1200 压缩到1200一份，400一份，120一份
            
            scale = float(o_maxsize)/800
            newWidth, newHeight = int(round(o_width / scale)),int(round(o_height/ scale))
            image_one.thumbnail((newWidth,newHeight),resample=1)
            image_one.save(file_1000)
            
            scale = float(o_maxsize)/120
            newWidth, newHeight = int(round(o_width / scale)),int(round(o_height/ scale))
            image_one.thumbnail((newWidth,newHeight),resample=1)
            image_one.save(file_120)
    
    @staticmethod
    def generate_thumbs(uploadPath, _uuid):
        
        tmp_file = uploadPath+_uuid+".jpg"
        
        file_1000 = uploadPath+_uuid+".jpg"
        file_120 = uploadPath+_uuid+"_120.jpg"
        file_400 = uploadPath+_uuid+"_400.jpg"
        image_one = Image.open(tmp_file)
        image_one = image_one.convert('RGB')
        o_width, o_height = image_one.size
        o_maxsize = max(o_width, o_height)
        scale = 1.0
        
        if os.path.isfile(file_120): 
            return
        
        if o_maxsize <= 400: #最大尺寸小于120 保存原图三份
            image_one.save(file_120)
            image_one.save(file_400)
        elif 400 <o_maxsize<= 800: #最大尺寸>400  <=800 保存原图两份,并压缩到120一份
            image_one.save(file_400)
            scale = float(o_maxsize)/400
            print scale
            newWidth, newHeight = int(round(o_width / scale)),int(round(o_height/ scale))
            print newWidth, newHeight, file_120
            image_one.thumbnail((newWidth,newHeight),resample=1)
            image_one.save(file_120)
        elif 800 <o_maxsize<= 1000: #最大尺寸>400  <=1000 保存原图一份,并压缩到400一份，120一份
            
            scale = float(o_maxsize)/800
            newWidth, newHeight = int(round(o_width / scale)),int(round(o_height/ scale))
            image_one.thumbnail((newWidth,newHeight),resample=1)
            image_one.save(file_400)
            
            scale = float(o_maxsize)/400
            newWidth, newHeight = int(round(o_width / scale)),int(round(o_height/ scale))
            image_one.thumbnail((newWidth,newHeight),resample=1)
            image_one.save(file_120)
        else:#>1200 压缩到1000一份，400一份，120一份
            
            scale = float(o_maxsize)/1000
            newWidth, newHeight = int(round(o_width / scale)),int(round(o_height/ scale))
            image_one.thumbnail((newWidth,newHeight),resample=1)
            image_one.save(file_1000)
            
            scale = float(o_maxsize)/800
            newWidth, newHeight = int(round(o_width / scale)),int(round(o_height/ scale))
            image_one.thumbnail((newWidth,newHeight),resample=1)
            image_one.save(file_400)
            
            scale = float(o_maxsize)/400
            newWidth, newHeight = int(round(o_width / scale)),int(round(o_height/ scale))
            image_one.thumbnail((newWidth,newHeight),resample=1)
            image_one.save(file_120)

    @staticmethod
    def rotate(file_path, direction='l', degree = 90):
        if not os.path.isfile(file_path): 
            return False
        im = Image.open(file_path)
        if direction == 'r':
            out = im.transpose(Image.ROTATE_270)
        elif direction == 'u':
            out = im.transpose(Image.ROTATE_180)  
        else:
            out = im.transpose(Image.ROTATE_90)
        out.save(file_path)
        return True
        
class PrintImage():
    
    """
    item:
        {
            'add_time': '2014-07-08 23:26:41',
            'currency_iso_code': u'CHF',
            'extra': u'',
            'id': 11L,
            'mod_time': 1404833201L,
            'name': u'\u96ea\u78a7',
            'name_i18n': u'\u96ea\u78a7',
            'note': u'',
            'num': 1,
            'number': u'46',
            'price': 3.0,
            'price_num': u'1',
            'price_unit': 110L,
            'price_unit_name': u'Bottle',
            'real_price': 3.0,
            'refer_id': 136L,
            'rid': 50023L,
            'uid': 38L
        }
    """
    @staticmethod
    def generate_order(order, items):
        WIDTH = 450
        HEIGHT = 450
        HEAD_HEIGTH = 70
        LINE_HEIGHT = 50
        FOOT_HEIGHT = 100
        LINE_NUM = 0
     
        num = len(items)
        
        for item in items:
            if len(item['name'].decode('utf-8'))>20:
                LINE_NUM += 3
            else:
                LINE_NUM += 2
        
        HEIGHT = HEAD_HEIGTH + (LINE_HEIGHT*LINE_NUM) + FOOT_HEIGHT
        if HEIGHT < 450:
            HEIGHT = 450
    
        im = Image.new('RGB', (WIDTH, HEIGHT), 0xffffff)
        draw = ImageDraw.Draw(im)
        width,height = im.size
    
        img = Image.open(config_base.setting['static']+"/image/tubban_small.png")
        im.paste(img, (WIDTH-185, HEIGHT-55), img)
    
        #画头
        #draw.rectangle(((0,0),(WIDTH,HEAD_HEIGTH)),fill=(223,223,223));
        draw.line(((10, HEAD_HEIGTH),(width-10,HEAD_HEIGTH)) , fill=(225,225,225))
        #标题文字，使用雅黑粗
        font = ImageFont.truetype(config_base.setting['static']+"/font/msyh.ttf", 16)
        font_18 = ImageFont.truetype(config_base.setting['static']+"/font/msyh.ttf", 18)
        font_30 = ImageFont.truetype(config_base.setting['static']+"/font/msyh.ttf", 30)
        font_32 = ImageFont.truetype(config_base.setting['static']+"/font/msyh.ttf", 32)
        fontcolor = (0,0,0) #(14,77,157)
        fontcolor_gold = (0,0,0) #(255,200,0)
        draw.text((10,18), "Table: "+str(order['table_num']), fill=fontcolor,font=font_32)
        draw.text((WIDTH-200,18), "People: "+str(order['people_num']), fill=fontcolor,font=font_32)
    
        #画行横线，每行LINE_HEIGHT像素。
        offset = HEAD_HEIGTH
        for i in range(1,num+1):
            
            if len(items[i-1]['name'].decode('utf-8')) > 20:
                step = 3*LINE_HEIGHT
                # 每行的底线位置
                line_y=offset+step;
                text_name_y_1 = line_y - 2*LINE_HEIGHT - 40
                text_name_y_2 = line_y - LINE_HEIGHT - 40
                text_num_y = line_y - 40
                # 间隔线  
                draw.line(((10, line_y),(width-10,line_y)) , fill=(225,225,225))
                # 名称行
                draw.text((10,text_name_y_1), items[i-1]['name_i18n'].decode('utf-8')[0:20], fill=fontcolor,font=font_32)
                draw.text((10,text_name_y_2), items[i-1]['name_i18n'].decode('utf-8')[20:], fill=fontcolor,font=font_32)
                # 数量行
                draw.text((10,text_num_y), str(items[i-1]['price_num']) + ' '+ str(items[i-1]['price_unit_name']).decode('utf-8'), fill=fontcolor_gold,font=font_32)
                draw.text((WIDTH-90,text_num_y), 'X '+str(items[i-1]['num']), fill=fontcolor_gold,font=font_32)
                
            else:
                step = 2*LINE_HEIGHT
                offset = offset+step
                # 每行的底线位置
                line_y=offset;
                text_name_y = line_y - LINE_HEIGHT - 40
                text_num_y = line_y - 40
                # 间隔线  
                draw.line(((10, line_y),(width-10,line_y)) , fill=(225,225,225))
                # 名称行
                draw.text((10,text_name_y), items[i-1]['name_i18n'].decode('utf-8'), fill=fontcolor,font=font_32)
                # 数量行
                draw.text((10,text_num_y), str(items[i-1]['price_num']) + ' '+ str(items[i-1]['price_unit_name']).decode('utf-8'), fill=fontcolor_gold,font=font_32)
                draw.text((WIDTH-90,text_num_y), 'X '+str(items[i-1]['num']), fill=fontcolor_gold,font=font_32)
            offset = line_y
        # 画底部
        draw.text((10,HEIGHT-60), 'Total: '+str(order['total_price'])+' '+items[0]['currency_iso_code'], fill=fontcolor,font=font_32)
        img = im.rotate(90)
        #img.show()
        # TOTO 规划路劲，名称中可以加语言前缀
        # print config.setting['uploads']+'/'+str(order['id'])+".png"
        img.save(config_base.setting['uploads']+'/print/'+str(order['id'])+".png")

if __name__ == '__main__':
    order = {'id':1,'table_num':2, 'people_num':3, 'total_price':200}
    items = [
        {
            'add_time': '2014-07-08 23:26:41',
            'currency_iso_code': u'CHF',
            'extra': u'',
            'id': 11L,
            'mod_time': 1404833201L,
            'name': u'abcdedefghijklmnopqrstuvwxyz',
            'name_i18n': u'test1',
            'note': u'',
            'num': 1,
            'number': u'46',
            'price': 3.0,
            'price_num': u'1',
            'price_unit': 110L,
            'price_unit_name': u'Bottle',
            'real_price': 3.0,
            'refer_id': 136L,
            'rid': 50023L,
            'uid': 38L
        },
          {
            'add_time': '2014-07-08 23:26:41',
            'currency_iso_code': u'CHF',
            'extra': u'',
            'id': 11L,
            'mod_time': 1404833201L,
            'name': u'ABCDEFGHIGKLMNOPQRSTUVWXYZ',
            'name_i18n': u'test1',
            'note': u'',
            'num': 1,
            'number': u'46',
            'price': 3.0,
            'price_num': u'1',
            'price_unit': 110L,
            'price_unit_name': u'Bottle',
            'real_price': 3.0,
            'refer_id': 136L,
            'rid': 50023L,
            'uid': 38L
        }]
    PrintImage.generate_order(order, items)