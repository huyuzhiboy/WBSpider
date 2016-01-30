# -*- coding: utf-8 -*-

import urllib2, urllib, cookielib
from scrapy import Selector
import pdb 
import sys 
import json
import time
import datetime
import cStringIO
import Image
reload(sys)
sys.setdefaultencoding('utf-8')

def get_html_by_data(url, use_cookie=False):
    data = {}
    post_data = urllib.urlencode(data)
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    req = urllib2.Request(url)
    req.add_header("User-agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36")
    if use_cookie:
        with open('cookie.conf', 'r') as cookie_file:
            for cookie in cookie_file.readlines():
                req.add_header("Cookie", cookie.strip())
                f = opener.open(req)
                html = f.read()
                f.close()
                html_file = open('test.html','w')
                print >> html_file, html
                if f.code != 200 or html.find('微博广场') != -1:
                    continue
                return html
            print 'Cannot find any available cookie!'
            exit(-1)
    else:
        f = opener.open(req)
        html = f.read()
        f.close()
        return html

def crawl_profile(profile_url, prod):
    prod['user_info_oid'] = profile_url.split('cn/')[1].split('/')[0]
    hxs = Selector(text=get_html_by_data(profile_url, True))
    # crawl touxiang
    img_list = hxs.xpath('//img')
    prod['user_info_avatar'] = ''
    for img in img_list:
        tlist = img.xpath('./@alt')
        if len(tlist) > 0 and tlist[0].extract() == '头像':
            prod['user_info_avatar'] = img.xpath('./@src')[0].extract()
            break
    print 'tx_url: ' + prod['user_info_avatar']
    # crawl jianjie
    prod['user_info_intro'] = ''
    txt_list = hxs.xpath('//div[@class="c"]/text()')
    for txt in txt_list:
        if txt.extract().find('简介') != -1:
            prod['user_info_intro'] = txt.extract().split(':')[1]
    print 'jianjie: ' + prod['user_info_intro']

def get_max_page(hxs):
    try:
        text = hxs.xpath('//div[@id="pagelist"]/form/div/input/@value')[0].extract()
        return int(text)
    except:
        return 1

def find_at_in_text(text):
    res = ""
    for part in text.split('@'):
        res += part.split(' ')[0] + ' '
    return res

def get_time_stamp(date_text):
    try:
        return time.mktime(time.strptime(date_text, "%Y-%m-%d %H:%M:%S"))
    except:
        return time.time()

def get_date_text(wb):
    date = wb.xpath('.//span[@class="ct"]/text()')[0].extract()
    date_text = date.split(' ')[0]
    if date_text.find('今天') != -1 or date_text.find('前') != -1:
        date_text = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    elif date_text.find('月') != -1:
        date_text = '2015-' + date_text.replace('月','-').replace('日','')
    date_text += ' ' + date.split(' ')[1].split('来自')[0].strip()
    return date_text

def crawl_weibo(prod, cur_page, max_cmt_page):
    url = "http://weibo.cn/%s?page=%d" % (prod['user_info_oid'], cur_page)
    print '============START CRAWL WEIBO======================'
    hxs = Selector(text=get_html_by_data(url, True))
    wb_list = hxs.xpath('//div[@class="c"]')
    if len(wb_list) <= 3:
        return
    print 'Find ' + str(len(wb_list)) + ' weibo elements'
    for wb in wb_list:
        try:
            print '=====SINGLE START====='
            wb_dict = {}
            wb_dict['text'] = ""
            content_list = wb.xpath('.//span[@class="ctt"]/a/text()|.//span[@class="ctt"]/text()|.//span[@class="ctt"]/span/text()')
            for elem in content_list:
                wb_dict['text'] += elem.extract()
            print 'text: ' + wb_dict['text']
            
            wb_dict['WB_forward_info'] = find_at_in_text(wb_dict['text'])

            date_text = get_date_text(wb)
            print 'date_text: ' + date_text
            wb_dict['time'] = str(int(get_time_stamp(date_text)))
            print 'time: ' + wb_dict['time']

            date = wb.xpath('.//span[@class="ct"]/text()')[0].extract()
            wb_dict['source'] = date.split('来自')[1].strip()
            if wb_dict['source'] == '':
                wb_dict['source'] = wb.xpath('.//span[@class="ct"]/a/text()')
                if len(wb_dict['source']) > 0:
                    wb_dict['source'] = wb_dict['source'][0].extract()
            print 'source: ' + wb_dict['source']

            text_list = wb.xpath('.//a/text()')
            for text in text_list:
                text = text.extract()
                if text.find('赞') != -1:
                    eq1 = text.find('[')
                    eq2 = text.find(']')
                    wb_dict['like'] = text[eq1+1:eq2]
                    print 'like: ' + wb_dict['like']
    
            wb_dict['comment'] = []
            # crawl comment url
            cmt_url = ''
            a_list = wb.xpath('.//a')
            for a in a_list:
                tlist = a.xpath('./text()')
                if len(tlist) > 0 and tlist[0].extract().find('评论') != -1 and tlist[0].extract().find('原文') == -1:
                    cmt_url = a.xpath('./@href')[0].extract()
                    break
            print 'cmt_url: ' + cmt_url
            crawl_imgs(wb, wb_dict, a_list)
            crawl_comment(wb_dict, cmt_url, max_cmt_page)
            prod['weiborecord'].append(wb_dict)
            print '=====SINGLE END====='
        except Exception as e:
            print e
            continue  
    print '============END CRAWL WEIBO======================'

def get_img_size(img_url):
    img_buf = get_html_by_data(img_url.replace('large', 'wap180'), use_cookie=True)
    c_img_buf = cStringIO.StringIO(img_buf)
    im = Image.open(c_img_buf)
    return im.size

def crawl_imgs(wb, wb_dict, a_list):
    wb_dict['image_list'] = []
    zt_url = ''
    for a in a_list:
        try:
            text = a.xpath('./text()')[0].extract()
            if text.find('组图共') != -1:
                zt_url = a.xpath('./@href')[0].extract()
        except:
            continue
    print 'zt_url: ' + zt_url
    if zt_url == '':
        img_url = wb.xpath('./div/a/img[@class="ib"]/@src')
        if len(img_url) > 0:
            try:
                img_dict = {}
                img_dict['url'] = img_url[0].extract().replace('wap180', 'large')
                img_dict['w'], img_dict['h'] = get_img_size(img_dict['url'])
                wb_dict['image_list'].append(img_dict)
            except Exception as e:
                #print e
                pass
    else:
        zt_hxs = Selector(text=get_html_by_data(zt_url,use_cookie=True))
        a_list = zt_hxs.xpath('//a')
        for a in a_list:
            try:
                text = a.xpath('./text()')[0].extract()
                if text == '原图':
                    img_url = a.xpath('./@href')[0].extract()
                    img_id = img_url.split('u=')[1].split('&')[0]
                    img_dict = {}
                    img_dict['url'] = 'http://ww3.sinaimg.cn/large/' + img_id + '.jpg'
                    img_dict['w'], img_dict['h'] = get_img_size(img_dict['url'])
                    wb_dict['image_list'].append(img_dict)
            except Exception as e:
                #print e
                continue
    print 'images: ',
    print wb_dict['image_list']

def crawl_cmt_details(wb_dict, hxs):
    for div in hxs.xpath('//div[@class="c"]'):
        try:
            id = div.xpath('./@id')[0].extract()
            if len(id) < 3:
                continue
            print '=====COMMENT START====='
            cmt_dict = {}
            cmt_dict['com_user_nick'] = div.xpath('./a/text()')[0].extract()
            print 'nickname: ' + cmt_dict['com_user_nick']
            date_text = get_date_text(div)
            print 'date_text: ' + date_text
            cmt_dict['time'] = str(int(get_time_stamp(date_text)))
            print 'time: ' + cmt_dict['time']
            cmt_dict['com_content'] = ""
            content_list = div.xpath('.//span[@class="ctt"]/a/text()|.//span[@class="ctt"]/text()|.//span[@class="ctt"]/span/text()')
            for elem in content_list:
                cmt_dict['com_content'] += elem.extract()
            print 'text: ' + cmt_dict['com_content']
            cmt_dict['com_forward_info'] = find_at_in_text(cmt_dict['com_content'])
            wb_dict['comment'].append(cmt_dict)
            print '=====COMMENT END====='
        except Exception as e:
            print e
            continue

def crawl_comment(wb_dict, cmt_url, max_cmt_page):
    # get max comment page
    hxs = Selector(text=get_html_by_data(cmt_url, True))
    max_page = get_max_page(hxs)
    print 'comment max page: ' + str(max_page)
    crawl_cmt_details(wb_dict, hxs)
    for cur_page in xrange(2, min(max_cmt_page, max_page) + 1):
        cur_url = cmt_url.replace('#cmtfrm','&page=%d'%cur_page)
        hxs = Selector(text=get_html_by_data(cur_url, True))
        crawl_cmt_details(wb_dict, hxs)
 
def crawl(nickname, idx_url, max_wb_page, max_cmt_page):
    prod = {}
    prod['user_nick'] = nickname
    hxs = Selector(text=get_html_by_data(idx_url, True))
    a_list = hxs.xpath('//a')
    profile_url = ''
    for a in a_list:
        tlist = a.xpath('./text()')
        if len(tlist) > 0 and tlist[0].extract() == '资料':
            profile_url = a.xpath('./@href')[0].extract()
            break
    profile_url = 'http://weibo.cn' + profile_url
    print 'profile_url: ' + profile_url
    crawl_profile(profile_url, prod)
    max_page = get_max_page(hxs)
    print 'max_page: ' + str(max_page)
    prod['weiborecord'] = []
    for cur_page in xrange(1, min(max_wb_page, max_page) + 1):
        crawl_weibo(prod, cur_page, max_cmt_page)
    return prod
 
def find_top_user(nickname):
    url = 'http://weibo.cn/search/user/?keyword=' + nickname
    hxs = Selector(text=get_html_by_data(url, True))
    try:
        nickname = hxs.xpath('//table[1]/tr/td[2]/a/text()')[0].extract()
        print nickname
        idx_url = 'http://weibo.cn' + hxs.xpath('//table[1]/tr/td[2]/a/@href')[0].extract().split('?')[0]
        print idx_url
        return nickname, idx_url
    except Exception as e:
        print e

if __name__ == "__main__":
    nickname, idx_url = find_top_user('中央')
    max_wb_page = 1
    max_cmt_page = 1
    res_dict = crawl(nickname, idx_url, max_wb_page, max_cmt_page)
    json_str = json.dumps(res_dict, ensure_ascii=False)
    with open('crawl_result.json', 'w') as res_file:
        print >> res_file, json_str
