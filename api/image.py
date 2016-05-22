#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
#
# 2013-1-20 by Victor
# Copyright 2013 www.Tubban.com
from api._base_ import BaseHandler, auth_user, auth_app
from calendar import c
from _module._lib.common import Common
from _module._lib.image import ImageGenerate
from _module.image.model import ImageModel
import config_base
import tempfile

try:
    from PIL import Image
except:
    import Image
    
    
class UploadCommonH(BaseHandler):
    @auth_app
    def post(self):
        
        data = {
            'title': {'type':'s','default':''},
            'watermark': {'type':'d','default':0},
        }
        ret = self.pack_args(data)
        if not ret[0]:
            self.display_para_error(ret[1])
            return
        
        if not self.request.files.has_key('upload'):
            self.display_para_error('upload image error, no file in param: upload')
            return
        
        file_dict_list = self.request.files['upload']
        
        if len(file_dict_list)<0 or len(file_dict_list)>6:
            self.display_para_error("Image num range： 1~6")
            return
        
        uuids = []

        for file_dict in file_dict_list:
            try:
                # 获取image id
                _uuid = ImageModel().gen_id()
                # 获取存储路径
                imageUploadPath = Common.get_image_path(_uuid)
        
                #basename, extension = os.path.splitext(file_dict["filename"])
                tmp_file = tempfile.NamedTemporaryFile(delete=True) #创建临时文件，当文件关闭时自动删除
                tmp_file.write(file_dict["body"])  #写入临时文件
                tmp_file.seek(0)
                
                image_one = Image.open(tmp_file)
                image_one = image_one.convert('RGB')
                o_width, o_height = image_one.size
                
                if ret[1]['watermark'] == 1:
                    # 加水印
                    mark = Image.open(config_base.setting['static']+"/resource/image/tubban_img_watermark.png") 
                    if mark.size[0] * 10 >o_width:
                        mark.thumbnail((o_width/10,o_height/10),resample=1)
                    layer = Image.new('RGBA', image_one.size, (0,0,0,0)) 
                    position = ((image_one.size[0] - mark.size[0]-image_one.size[0]/50),(image_one.size[1] - mark.size[1]-image_one.size[1]/50))
                    layer.paste(mark, position)
                    image_one = Image.composite(layer, image_one, layer)
                    # End 加水印

                image_one.save(imageUploadPath+_uuid+".jpg")
                ImageGenerate.generate_thumbs(imageUploadPath, _uuid)
                uuids.append(_uuid)
            except Exception as e:  
                self.display_para_error(str(e))   
        self.set_data(uuids)
        self.display()

class UploadAvatorH(BaseHandler):
    """Upload User Avator
    """
    @auth_app
    def post(self):
        data = {
            'uid': {'type':'s','required':1},
        }
        ret = self.pack_args(data)
        if ret[0] == False:
            self.display_para_error()
            return
        uid = ret[1]['uid']

        _uuid = ImageModel().get_avator_id(uid)
        
        uploadPath = Common.get_avator_path(_uuid)
        
        try:
            file_dict_list = self.request.files['upload']
        except Exception as e:
            self.display_para_error("File empty or file param error.")
            return
        
        if len(file_dict_list)<0:
            self.display_para_error("File empty")
            return
        
        file_dict = file_dict_list[0]
        
    
        filenameBig = "%s.jpg" % str(_uuid)
        filenameMid = "%s_s.jpg" % str(_uuid)

        try:
            tmp_file = tempfile.NamedTemporaryFile(delete=True) #创建临时文件，当文件关闭时自动删除
            tmp_file.write(file_dict["body"])  #写入临时文件
            tmp_file.seek(0)
              
            image_one = Image.open(tmp_file)
            image_one.save(uploadPath+filenameBig)
            
            # other size
            img = Image.open(uploadPath+filenameBig)
            img.thumbnail((600,600),resample=1)
            img.save(uploadPath+filenameBig)
            img.thumbnail((200,200),resample=1)
            img.save(uploadPath+filenameMid)
            
            tmp_file.close()
            self.set_data({"id": _uuid})
            self.display()
        except Exception, e:
            print str(e)
            self.display_internal_error()


            
class PageNotFoundH(BaseHandler):
    def get(self, *args, **kwargs):
        self.write("No resource")
        