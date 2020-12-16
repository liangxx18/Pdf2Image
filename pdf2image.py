# -*- coding: utf-8 -*-
# @Author: lxx
# @Create_time: 2020/11/24
# @File: pdf2image.py

import fitz
from PyPDF2 import PdfFileReader,PdfFileWriter
import os,shutil,re
from PIL import Image
import logging

logging.basicConfig(level = logging.INFO,format = '%(asctime)s -- %(name)s - %(levelname)s :: %(message)s')#,filename="epaper_xml_extract.log")
logger = logging.getLogger("pdf2image")

class Pdf2Image():
    def __init__(self,file_path,file,type='jpg',save_path=None,image_name=None,direction='x',if_del_blank_page=True,if_splice=True):
        """
        :param file_path: 原始文件路径
        :param file: 文件
        :param type: 另存为jpg或png
        :param save_path: 保存路径
        :param image_name: 另存为文件名
        :param direction: 拼接方向
        :param if_del_blank_page: 是否去除空白页
        :param if_splice: 是否拼接
        """
        self.file_path = file_path
        self.file = file
        self.file_name = file if len(re.findall('\.pdf',file.lower()))==0 else '.'.join(file.split('.')[:-1])
        self.type = type
        self.save_path = save_path if save_path is not None else self.file_path
        self.image_name = image_name if image_name is not None else self.file_name
        self.direction = direction
        self.if_del_blank_page = if_del_blank_page
        self.if_splice = if_splice

    def delete_pdf_blank_page(self,save_name=None):
        """
        删除PDF的空白页
        :param save_name: 删除后的文件名
        :return:
        """
        if os.path.exists(os.path.join(self.file_path,self.file)):
            reader = PdfFileReader(open(os.path.join(self.file_path,self.file), 'rb'))
        else:
            logger.error("PDF file do not exist !\t\t" + os.path.join(self.file_path,self.file))
            exit(1)
        writer = PdfFileWriter()
        pages = reader.getNumPages()
        k = 0
        for i in range(pages):
            page = reader.getPage(i)
            if "/XObject" in page["/Resources"].keys() or "/Font" in page["/Resources"].keys():
                writer.addPage(page)
                k += 1
        logger.info("pdf总页数：%d；空白页数：%d" % (pages, pages - k))
        if save_name is None:
            save_name = self.file_name+'_temp.PDF'
        if k<pages:
            with open(os.path.join(self.save_path,save_name), "wb") as outputStream:
                writer.write(outputStream)
        elif save_name!=self.file:
            shutil.copyfile(os.path.join(self.file_path,self.file),os.path.join(self.save_path,save_name))

    def pdf_to_image(self,zoom_x, zoom_y,rotate=0):
        """
        PDF转化为图片
        :param zoom_x: 设置图片相对于PDF文件在X轴上的缩放比例
        :param zoom_y: 设置图片相对于PDF文件在Y轴上的缩放比例
        :param rotate: 设置图片相对于PDF文件的旋转角度
        :param type: 转化图片的类型，jpg或png
        :return:
        """
        if self.if_del_blank_page:
            self.delete_pdf_blank_page()
            pdf_doc = fitz.open(os.path.join(self.file_path,self.file_name+'_temp.PDF'))
        else:
            pdf_doc = fitz.open(os.path.join(self.file_path, self.file))
        image_list = []
        for pg in range(pdf_doc.pageCount):
            page = pdf_doc[pg]
            rotate = int(rotate)
            trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
            pix = page.getPixmap(matrix=trans, alpha=False)
            if self.type.lower()=='png':
                pix.writePNG(os.path.join(self.save_path, self.image_name + '_' + str(pg) + '.png'))
                image_list.append(os.path.join(self.save_path, self.image_name + '_' + str(pg) + '.png'))
            else:
                pix.writeImage(os.path.join(self.save_path, self.image_name + '_' + str(pg) + '.jpg'))
                image_list.append(os.path.join(self.save_path, self.image_name + '_' + str(pg) + '.jpg'))
        if self.if_splice:
            self.image_splice(image_list)
            for p in image_list:
                if os.path.exists(p):
                    os.remove(p)
        if os.path.exists(os.path.join(self.file_path,self.file_name+'_temp.PDF')):
            os.remove(os.path.join(self.file_path,self.file_name+'_temp.PDF'))
        #return image_list


    def image_splice(self,image_list):
        """
        图片拼接
        :param image_list: 带拼接的图片列表
        :param direction: 拼接的方向，x：按x轴方向拼接，y：按y轴方向拼接
        :return:
        """
        images = [Image.open(p) for p in image_list]
        width, height = images[0].size
        new_images = []
        for i in images:
            new_image = i.resize((width, height),Image.BILINEAR)
            new_images.append(new_image)
        if self.direction=='y':
            # 创建空白长图
            result = Image.new(new_images[0].mode, (width, height * len(new_images)))
            # 拼接图片
            for i, image in enumerate(new_images):
                result.paste(image, box=(0,i * height))
        else:
            #创建空白长图
            result = Image.new(new_images[0].mode, (width * len(new_images), height))
            #拼接图片
            for i,image in enumerate(new_images):
                result.paste(image,box=(i * width, 0))
        if self.type.lower() == 'png':
            result.save(os.path.join(self.save_path, self.image_name + '.png'))
        else:
            result.save(os.path.join(self.save_path, self.image_name + '.jpg'))


if __name__=="__main__":
    file_path, file = "",""
    p2i = Pdf2Image(file_path,file)
    p2i.pdf_to_image(2,2)
