#-*- coding:utf-8 -*-

from django.http import HttpResponse
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def record_id(wb_id, max_wb_page, max_cmt_page):
    record_path = './temp/'
    if not os.path.exists(record_path):
        os.mkdir(record_path)
    file_path = record_path + wb_id
    cmd = 'touch ' + file_path + '__' + str(max_wb_page) + '__' + str(max_cmt_page)
    res = os.system(cmd)

def handle_request(request):
    try:
        wb_id = request.GET.get('wbid', 'null')
        max_cmt_page = request.GET.get('max_cmt_page', '0')
        try:
            max_wb_page = int(request.GET.get('max_wb_page', '0'))
        except:
            return HttpResponse('max_wb_page must be integer')
        try:
            max_cmt_page = int(request.GET.get('max_cmt_page', '0'))
        except:
            return HttpResponse('max_cmt_page must be integer')
        if wb_id != 'null':
            record_id(wb_id, max_wb_page, max_cmt_page)
            return HttpResponse(wb_id + ' has recorded.')
        else:
            return HttpResponse('Parameter is illegal, please input: wbid=xxx')
    except Exception as e:
        print e
        return HttpResponse('Occur an unexpected error, please connect adminstrator')

