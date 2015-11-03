#!/usr/bin/env python2.7
#-*- coding:utf8 -*-
'''
Created on May 22, 2015

@author: victor
'''
from xml.dom import minidom

class XmlUtil(object):
    
    def __init__(self, input, type='file', encoding='UTF-8'):
        self.encoding = encoding
        self.doc = None
        if type <> 'file':
            self.doc = self._parse_str(input)
        else:
            self.doc = self._parse_file(input)
            
    def get_doc(self):
        return self.doc

    def _parse_file(self, filename):
        try:
            return minidom.parse(filename) 
        except:
            return None
    
    def _parse_str(self, _str):
        try:
            return minidom.parseString(_str)
        except:
            return None
    
    def get_attrvalue(self, node, attrname):
        return node.getAttribute(attrname) if node else ''

    def get_nodevalue(self, node, index = 0):
        return node.childNodes[index].nodeValue if node else ''
    
    def get_1level_nodevalue(self, name):
        """
        <xml>
            <ToUserName>xxxx</ToUserName>
            <FromUserName>90</FromUserName>
            <CreateTime>123456789</CreateTime>
            <MsgType><![CDATA[event]]></MsgType>
            <Event>Event</Event>
            <Latitude>23.137466</Latitude>
            <Longitude>113.352425</Longitude>
            <Precision>119.385040</Precision>
        </xml>
        
        get_1level_nodevalue("FromUserName")
        
        """
        return self.get_xmlnodes(self.doc, name)[0].firstChild.data
    
    def get_xmlnodes(self, node, name):
        return node.getElementsByTagName(name) if node else []

    def xml_to_string(self, filename):
        doc = minidom.parse(filename)
        return doc.toxml(self.encoding)

    
    
if __name__ == "__main__":
    
    location_xml_str = """<xml><ToUserName><![CDATA[gh_10f6c3c3ac5a]]></ToUserName><FromUserName><![CDATA[oyORnuP8q7ou2gfYjqLzSIWZf0rs]]></FromUserName><CreateTime>1409735668</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[abcdteT]]></Content><MsgId>6054768590064713728</MsgId><Encrypt><![CDATA[hyzAe4OzmOMbd6TvGdIOO6uBmdJoD0Fk53REIHvxYtJlE2B655HuD0m8KUePWB3+LrPXo87wzQ1QLvbeUgmBM4x6F8PGHQHFVAFmOD2LdJF9FrXpbUAh0B5GIItb52sn896wVsMSHGuPE328HnRGBcrS7C41IzDWyWNlZkyyXwon8T332jisa+h6tEDYsVticbSnyU8dKOIbgU6ux5VTjg3yt+WGzjlpKn6NPhRjpA912xMezR4kw6KWwMrCVKSVCZciVGCgavjIQ6X8tCOp3yZbGpy0VxpAe+77TszTfRd5RJSVO/HTnifJpXgCSUdUue1v6h0EIBYYI1BD1DlD+C0CR8e6OewpusjZ4uBl9FyJvnhvQl+q5rv1ixrcpCumEPo5MJSgM9ehVsNPfUM669WuMyVWQLCzpu9GhglF2PE=]]></Encrypt></xml>"""
    """
    <xml>
        <ToUserName>xxxx</ToUserName>
        <FromUserName>UserOpenID </FromUserName>
        <CreateTime>123456789</CreateTime>
        <MsgType><![CDATA[event]]></MsgType>
        <Event>Event</Event>
        <Latitude>23.137466</Latitude>
        <Longitude>113.352425</Longitude>
        <Precision>119.385040</Precision>
    </xml>
    """
    
    
    xmlUtil = XmlUtil(location_xml_str, 'str')
    doc = xmlUtil.get_doc()
    print doc
    #userNodes = xmlUtil.get_xmlnodes(doc, "FromUserName")
    #print userNodes
    #print userNodes[0].firstChild.data
    
    print xmlUtil.get_1level_nodevalue("FromUserName")
    #print xmlUtil.get_1level_nodevalue("Latitude")
    #print xmlUtil.get_1level_nodevalue("Longitude")
    
    #print xmlUtil.get_nodevalue(userNodes[0], 0).encode('utf-8','ignore')
    
    #print XmlUtil.get_nodevalue(XmlUtil.get_xmlnodes(doc, "FromUserName"), 0)
    
    