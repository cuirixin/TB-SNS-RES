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
    def generate_thumbs(uploadPath, _uuid):
        
        tmp_file = uploadPath+_uuid+".jpg"
        
        file_large = uploadPath+_uuid+".jpg"
        file_middle = uploadPath+_uuid+"_m.jpg"
        image_one = Image.open(tmp_file)
        image_one = image_one.convert('RGB')
        o_width, o_height = image_one.size
        o_maxsize = max(o_width, o_height)
        scale = 1.0
        
        if os.path.isfile(file_middle): 
            return
        
        if o_maxsize <= 420: #最大尺寸小于420
            image_one.save(file_middle)
        elif 420 <o_maxsize<= 860: #最大尺寸>420  <=800 
            scale = float(o_maxsize)/420
            newWidth, newHeight = int(round(o_width / scale)),int(round(o_height/ scale))
            image_one.thumbnail((newWidth,newHeight), resample=1)
            image_one.save(file_middle)
        else:# 最大尺寸>860 
            
            scale = float(o_maxsize)/860
            newWidth, newHeight = int(round(o_width / scale)),int(round(o_height/ scale))
            image_one.thumbnail((newWidth,newHeight), resample=1)
            image_one.save(file_large)
            
            scale = float(o_maxsize)/420
            newWidth, newHeight = int(round(o_width / scale)),int(round(o_height/ scale))
            image_one.thumbnail((newWidth,newHeight), resample=1)
            image_one.save(file_middle)


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
        