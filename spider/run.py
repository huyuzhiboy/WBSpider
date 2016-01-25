# -*- coding:utf-8 -*-

import os
import time
import sys
import weibo
import requests
import json
reload(sys)
sys.setdefaultencoding('utf-8')

def upload(res_dict):
    req_url = 'http://www.clawbook.com/api/snsupload'
    json_str = json.dumps(res_dict, ensure_ascii=False)
    print json_str
    payload = {
        'ak':'lkj.pasiuzhb*iasyjwhq',
        'UploadForm[snsFile]':json_str
    }
    try:
        rescode = requests.post(req_url, data=payload)
        print 'rescode: ' + str(rescode)
        return True
    except Exception as e:
        print e
        print 'Cannot send post request!'
        return False

def work(temp_dir_path):
    if temp_dir_path[-1] != '/':
        temp_dir_path += '/'
    filename_list = list(set(os.listdir(temp_dir_path)))
    print filename_list 
    for filename in filename_list:
        try:
            res = filename.split('__')
            nickname = res[0]
            max_wb_page = int(res[1])
            max_cmt_page = int(res[2])
            if max_wb_page == 0:
                max_wb_page = 9999
            if max_cmt_page == 0:
                max_cmt_page = 9999
        except Exception as e:
            print e
            print 'Illegal filename: ' + filename
        nickname, idx_url = weibo.find_top_user(nickname)
        res_dict = weibo.crawl(nickname, idx_url, max_wb_page, max_cmt_page)
        if upload(res_dict):
            os.remove(temp_dir_path + filename)

def usage():
    print 'python run.py temp_dir_path'
    exit(-1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage()
    temp_dir_path = sys.argv[1]    
    while 1:
        work(temp_dir_path)
        time.sleep(1)
