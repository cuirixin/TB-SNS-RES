#-*- coding:utf8 -*-

'''
Created on 2014-4-19
@author: cuirixin
'''
import xlrd
import xlwt

class OpExcel():
    
    @staticmethod
    def rExcel_Sheet_Num(inEfile):
        rfile = xlrd.open_workbook(inEfile)
        return len(rfile.sheets())
    
    @staticmethod
    def rExcel_Sheet_By_Index(inEfile, sheet_index=0):
        rfile = xlrd.open_workbook(inEfile)
        #创建索引顺序获取一个工作表
        table = rfile.sheet_by_index(sheet_index)
        
        #获取行数和列数
        nrows = table.nrows
        ncols = table.ncols

        #从第二行开始获取数据，组装成list返回
        data = []
        for i in range(1, nrows):
            data.append(table.row_values(i))
            #table.cell(i,0).value获取某一单元格的值
            #print table.row_values(i)
        head = None
        if nrows>0:
            head = table.row_values(0)
        return {'name':table.name, 'head':head, 'data':data}
    
    @staticmethod
    def rExcel_Sheet_Head(inEfile, sheet_index=0):
        rfile = xlrd.open_workbook(inEfile)
        #创建索引顺序获取一个工作表
        table = rfile.sheet_by_index(sheet_index)
        if table.nrows == 0:
            return None
        else:
            return table.row_values(0)
    
    #读取Excel表
    @staticmethod
    def rExcel(inEfile, sheet_index=0):
        rfile = xlrd.open_workbook(inEfile)
        #创建索引顺序获取一个工作表
        table = rfile.sheet_by_index(sheet_index)
        #获取行数和列数
        nrows = table.nrows
        ncols = table.ncols

        #从第二行开始获取数据，组装成list返回
        data = []
        for i in range(1, nrows):
            data.append(table.row_values(i))
            #table.cell(i,0).value获取某一单元格的值
            #print table.row_values(i)
        return data

    #将数据写入Excel表
    @staticmethod
    def wExcel(infile,outEfile):
        rfile = open(infile,'r')
        buf = rfile.read().split('\n')
        rfile.close()
        
        w = xlwt.Workbook()
        sheet = w.add_sheet('sheet1')
        for i in range(len(buf)):
            sheet.write(i,0,buf[i].decode('utf8'))
        w.save(outEfile)

if __name__ == '__main__':
    t = OpExcel()
    t.rExcel('carte.xlsx')
    #t.wExcel('test','1.xls')
