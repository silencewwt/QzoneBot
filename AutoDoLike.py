#!/usr/bin/env python3
# -*-coding:utf-8-*-

import os
import re
import sys
import time
import zlib
import sqlite3
import urllib.parse
import urllib.request
import urllib.error
import http.cookies
import http.cookiejar
import win32crypt


class AutoDoLike(object):
    def __init__(self, self_id, target_id, comment='Python大法好，用过都说屌!'):
        if self_id == '' or target_id == '':
            raise Exception('please input correct id!')
        self.self_id = self_id
        self.target_id = target_id
        self.comment = comment
        self.like_done = False
        self.comment_done = False
        self.prove = 0
        self.msg_list = []
        self.pages = 0
        self.like_num = 0
        self.comment_num = 0
        self.url = 'http://taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?uin={}&inCharset=utf-8&outCharset=utf-8&' \
                   'hostUin={}&notice=0&sort=0&pos={}&num=20&cgi_host=http%3A%2F%2Ftaotao.qq.com%2F' \
                   'cgi-bin%2Femotion_cgi_msglist_v6&code_version=1&format=jsonp&need_private_comment=1' \
                   '&g_tk={}'
        self.cookie = http.cookies.SimpleCookie()
        self.cookie_dic = {}
        self.cookie_name = ['__Q_w_s_hat_seed', '__Q_w_s__QZN_TodoMsgCnt', '__Q_w_s__appDataSeed', 'randomSeed',
                            'o_cookie', 'pgv_pvid', 'RK', 'g_ut', '3g_pt_cvdata', 'pgv_info', 'QZ_FE_WEBP_SUPPORT',
                            'cpu_performance_v8', 'rv2', 'property20', 'pt2gguin', 'uin', 'skey', 'ptisp', 'ptcz',
                            'Loading', 'p_skey', 'pt4_token', 'qzspeedup']
        self.domain = ['.qzone.qq.com', '.user.qzone.qq.com', '.qq.com']
        self.cookie_file_path = os.path.join(os.environ['LOCALAPPDATA'],
                                             r'Google\Chrome\User Data\Default\Cookies')
        self.cookie_str = ''

    def login(self):
        pass

    def get_cookies(self):
        if not os.path.exists(self.cookie_file_path):
            raise Exception('please setup Chrome first!')
        conn = sqlite3.connect(self.cookie_file_path)
        for domain in self.domain:
            for row in conn.execute('select host_key, name, encrypted_value from cookies where host_key=?', (domain,)):
                pwd_hash = row[2]
                try:
                    ret = win32crypt.CryptUnprotectData(pwd_hash, None, None, None, 0)
                except Exception:
                    print('Fail to decrypt chrome cookies')
                    sys.exit(-1)
                self.cookie[row[1]] = ret[1]
                self.cookie_dic[row[1]] = self.cookie[row[1]].value[2:-1]
        cookie_list = []
        for key in self.cookie_name:
            if key in self.cookie_dic:
                cookie_list.append('%s=%s; ' % (key, self.cookie_dic[key]))
        self.cookie_str = ''.join(cookie_list)
        conn.close()
        prove_str = self.cookie_dic['skey']
        variable_a = 5381
        for char in prove_str:
            variable_a += (variable_a << 5) + ord(char)
        self.prove = variable_a & 2147483647
        print(self.prove)

    def get_msg_id(self):
        headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip,deflate,sdch', 'Accept-Language': 'zh-CN,zh;q=0.8',
                   'Connection': 'keep-alive', 'Cookie': self.cookie_str, 'Host': 'taotao.qq.com',
                   'Referer': 'http://cnc.qzs.qq.com/qzone/app/mood_v6/html/index.html',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/36.0.1985.125 Safari/537.36}'}
        reg = r'"t1_termtype":\w+,"tid":"([a-fA-F\d]+)","ugc_right"'
        reg = re.compile(reg)
        while self.comment_done is False:
            url = self.url.format(self.target_id, self.target_id, self.pages*20, self.prove)
            req = urllib.request.Request(url, headers=headers)
            resp_html = urllib.request.urlopen(req).read()
            resp_html = zlib.decompress(resp_html, 16 + zlib.MAX_WBITS).decode('utf8')
            target_list = re.findall(reg, resp_html)
            msg_list = []
            for tid in target_list:
                if tid not in msg_list:
                    self.msg_list.append(tid)
                    msg_list.append(tid)
            # self.like_post(msg_list)
            self.comment_post(msg_list)
            self.pages += 1
            print('%s pages done!' % self.pages)
        self.work_done()

    def like_post(self, target_list):
        headers = {'Host': 'w.cnc.qzone.qq.com', 'Connection': 'keep-alive', 'Content-Length': '268',
                   'Cache-Control': 'max-age=0', 'Origin': 'http://user.qzone.qq.com',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/36.0.1985.125 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded', 'Accept-Encoding': 'gzip,deflate,sdch',
                   'Referer': 'http://user.qzone.qq.com/%s' % self.target_id, 'Accept-Language': 'zh-CN,zh;q=0.8',
                   'Cookie': self.cookie_str}
        if target_list == []:
            self.like_done = True
            return
        for tid in target_list:
            values = {'qzreferrer': 'http://user.qzone.qq.com/%s' % self.target_id, 'opuin': '%s' % self.self_id,
                      'unikey': 'http://user.qzone.qq.com/%s/mood/%s.1' % (self.target_id, tid),
                      'curkey': 'http://user.qzone.qq.com/%s/mood/%s.1' % (self.target_id, tid), 'from': '-100',
                      'fupdate': '1', 'face': '0'}
            data = urllib.parse.urlencode(values).encode('utf8')
            target_url = 'http://w.cnc.qzone.qq.com/cgi-bin/likes/internal_dolike_app?g_tk=%s' % self.prove
            req = urllib.request.Request(target_url, headers=headers, data=data)
            urllib.request.urlopen(req).read()

            # time.sleep(1)
            self.like_num += 1

    def comment_post(self, target_list):
        comment_url = 'http://taotao.qq.com/cgi-bin/emotion_cgi_re_feeds?g_tk=%s&' % self.prove
        headers = {'Host': 'taotao.qq.com', 'Connection': 'keep-alive', 'Content-Length': '303',
                   'Origin': 'http://user.qzone.qq.com', 'Accept': '*/*', 'Accept-Encoding': 'gzip,deflate,sdch',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/36.0.1985.125 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                   'Accept-Language': 'zh-CN,zh;q=0.8', 'Referer': 'http://user.qzone.qq.com/%s' % self.target_id,
                   'Cookie': self.cookie_str + 'qqmusic_uin=; qqmusic_key=; qqmusic_fromtag=;'}
        values = {'feedsType': '100', 'inCharset': 'utf-8', 'private': '0', 'paramstr': '2',
                  'outCharset': 'utf-8', 'plat': 'qzone', 'source': 'ic', 'hostUin': self.target_id, 'isSignIn': '',
                  'uin': self.self_id, 'format': 'fs', 'ref': 'feeds', 'content': self.comment, 'richval': '',
                  'richtype': '', 'qzreferrer': 'http://user.qzone.qq.com/%s' % self.target_id}
        if target_list == []:
            self.comment_done = True
            return
        for tid in target_list:
            values['topicId'] = '%s_%s_1' % (self.target_id, tid)
            data = urllib.parse.urlencode(values).encode('utf8')
            req = urllib.request.Request(comment_url, data=data, headers=headers)
            resp_html = urllib.request.urlopen(req).read()
            resp_html = zlib.decompress(resp_html, 16 + zlib.MAX_WBITS).decode('utf8')
            with open('resp%s.htm' % self.comment_num, 'w', encoding='utf8') as html:
                html.write(resp_html)
            self.comment_num += 1

    def work_done(self):
        print('totally %s pieces of messages done!' % self.like_num)
        print('totally %s pages of messages!' % self.pages)

    def main(self):
        self.get_cookies()
        self.get_msg_id()

a = AutoDoLike('', '')
a.main()