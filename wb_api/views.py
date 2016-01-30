#-*- coding:utf-8 -*-

from django.http import HttpResponse
import os
import sys
import json
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
        res_dict = {}
        res_dict['result'] = 0
        
        try:
            max_cmt_page = request.GET.get('max_cmt_page', '0')
            max_wb_page = int(request.GET.get('max_wb_page', '0'))
            res_dict['max_wb_page'] = max_wb_page
        except:
            res_dict['result'] = 1
            res_dict['desc'] = 'max_wb_page must be integer'
        
        try:
            max_cmt_page = int(request.GET.get('max_cmt_page', '0'))
            res_dict['max_cmt_page'] = max_cmt_page
        except:
            res_dict['result'] = 2
            res_dict['desc'] = 'max_cmt_page must be integer'
        
        wb_id = request.GET.get('wbid', 'null')
        if wb_id != 'null' and wb_id.strip() != '':
            res_dict['wb_id'] = wb_id
            record_id(wb_id, max_wb_page, max_cmt_page)
            res_dict['desc'] = ''
        else:
            res_dict['result'] = 3
            res_dict['desc'] = 'Parameter is illegal, please input: wbid=xxx'

        return HttpResponse(json.dumps(res_dict, ensure_ascii=False))
    except Exception as e:
        print e
        res_dict = {}
        res_dict['result'] = 4
        res_dict['desc'] = 'Occur an unexpected error, please connect adminstrator'
        return HttpResponse(json.dumps(res_dict, ensure_ascii=False))
        

