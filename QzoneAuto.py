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
import http.client
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

    def get_msg_id(self):
        headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip,deflate,sdch', 'Accept-Language': 'zh-CN,zh;q=0.8',
                   'Connection': 'keep-alive', 'Cookie': self.cookie_str, 'Host': 'taotao.qq.com',
                   'Referer': 'http://cnc.qzs.qq.com/qzone/app/mood_v6/html/index.html',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/36.0.1985.125 Safari/537.36}'}
        while self.comment_done is False:
            url = self.url.format(self.target_id, self.target_id, self.pages*20, self.prove)
            req = urllib.request.Request(url, headers=headers)
            try:
                resp_html = urllib.request.urlopen(req).read()
            except urllib.error.HTTPError as e:
                print(e.code, e.reason)
                sys.exit(-1)
            except urllib.error.URLError as e:
                print(e.reason)
                sys.exit(-1)
            resp_html = zlib.decompress(resp_html, 16 + zlib.MAX_WBITS).decode('utf8')
            with open('%s.htm' % self.pages, 'w', encoding='utf8') as htm:
                htm.write(resp_html)
            null = None
            page_data = eval(resp_html[10:-2])
            target_list = []
            for msg in page_data['msglist']:
                target_list.append(msg['tid'])
            msg_list = []
            for tid in target_list:
                if tid not in msg_list:
                    self.msg_list.append(tid)
                    msg_list.append(tid)
            for msg in page_data['msglist']:
                if msg['cmtnum'] > 1:
                    comment_list = []
                    for cmt in msg['commentlist']:
                        comment_list.append(cmt['content'])
                    self.imitate_post(msg['tid'], comment_list)
            # self.like_post(msg_list)
            # self.comment_post(msg_list)
            # self.get_more_comment(msg_list)
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
        if not target_list:
            self.like_done = True
            return
        for tid in target_list:
            data = {'qzreferrer': 'http://user.qzone.qq.com/%s' % self.target_id, 'opuin': '%s' % self.self_id,
                    'unikey': 'http://user.qzone.qq.com/%s/mood/%s.1' % (self.target_id, tid),
                    'curkey': 'http://user.qzone.qq.com/%s/mood/%s.1' % (self.target_id, tid), 'from': '-100',
                    'fupdate': '1', 'face': '0'}
            data = urllib.parse.urlencode(data).encode('utf8')
            target_url = 'http://w.cnc.qzone.qq.com/cgi-bin/likes/internal_dolike_app?g_tk=%s' % self.prove
            req = urllib.request.Request(target_url, headers=headers, data=data)
            try:
                urllib.request.urlopen(req)
            except urllib.error.HTTPError as e:
                print(e.code, e.reason)
            except urllib.error.URLError as e:
                print(e.reason)
            time.sleep(1)
            self.like_num += 1

    def comment_post(self, target_list, comment=''):
        comment_url = 'http://taotao.qq.com/cgi-bin/emotion_cgi_re_feeds?g_tk=%s&' % self.prove
        headers = {'Host': 'taotao.qq.com', 'Connection': 'keep-alive', 'Content-Length': '286',
                   'Origin': 'http://user.qzone.qq.com', 'Accept': '*/*', 'Accept-Encoding': 'gzip,deflate,sdch',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/36.0.1985.125 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                   'Accept-Language': 'zh-CN,zh;q=0.8', 'Referer': 'http://user.qzone.qq.com/%s' % self.target_id,
                   'Cookie': self.cookie_str + 'qqmusic_uin=; qqmusic_key=; qqmusic_fromtag=;'}
        values = {'topicId': '', 'feedsType': '100', 'inCharset': 'utf-8', 'private': '0', 'paramstr': '2',
                  'outCharset': 'utf-8', 'plat': 'qzone', 'source': 'ic', 'hostUin': self.target_id, 'isSignIn': '',
                  'uin': self.self_id, 'format': 'fs', 'ref': 'feeds', 'richval': '', 'richtype': '',
                  'qzreferrer': 'http://user.qzone.qq.com/%s' % self.target_id}
        if not comment:
            if not target_list:
                self.comment_done = True
                return
        for tid in target_list:
            values['topicId'] = '%s_%s_1' % (self.target_id, tid)
            if comment:
                values['content'] = comment
            else:
                values['content'] = self.comment
            data = urllib.parse.urlencode(values).encode('utf8')
            req = urllib.request.Request(comment_url, data=data, headers=headers)
            try:
                urllib.request.urlopen(req)
            except urllib.error.HTTPError as e:
                print(e.code, e.reason)
            except urllib.error.URLError as e:
                print(e.reason)
            self.comment_num += 1

    def get_more_comment(self, tid):
        get_url = 'http://taotao.qq.com/cgi-bin/emotion_cgi_ic_getcomments?g_tk=%s' % self.prove
        headers = {'Host': 'taotao.qq.com', 'Connection': 'keep-alive', 'Content-Length': '613',
                   'Cache-Control': 'max-age=0', 'Accept': 'text/html,application/xhtml+xml,application'
                                                           '/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Origin': 'http://ic2.s8.qzone.qq.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                                 '/36.0.1985.125 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'Accept-Encoding': 'gzip,deflate,sdch', 'Accept-Language': 'zh-CN,zh;q=0.8',
                   'Cookie': self.cookie_str + 'qqmusic_uin=; qqmusic_key=; qqmusic_fromtag=;'}
        values = {'topicId': '', 'feedsType': '8', 'inCharset': 'gbk', 'outCharset': 'gbk', 'sort': '1',
                  'plat': 'qzone', 'source': 'ic', 'hostUin': self.target_id, 'uin': self.self_id, 'start': '0',
                  'num': '20', 'format': 'fs', 'ref': 'feeds', 'isfakereq': '1', 'paramstr': '2'}
        referer = 'http://ic2.s8.qzone.qq.com/cgi-bin/feeds/feeds_html_module?i_uin={}&i_login_uin={}&mode=4&' \
                  'previewV8=1&style=35&version=8&needDelOpr=true&transparence=true&hideExtend=false&showcount=5&' \
                  'MORE_FEEDS_CGI=http%3A%2F%2Fic2.s8.qzone.qq.com%2Fcgi-bin%2Ffeeds%2Ffeeds_html_act_all&refer=2&' \
                  'paramstring=os-win7|100'
        referer = referer.format(self.target_id, self.self_id)
        headers['Referer'] = referer
        values['qzreferrer'] = referer
        values['topicId'] = '%s_%s__1' % (self.target_id, tid)
        data = urllib.parse.urlencode(values).encode('utf8')
        req = urllib.request.Request(get_url, headers=headers, data=data)
        resp_html = ''
        try:
            resp_html = urllib.request.urlopen(req).read()
        except http.client.HTTPException as e:
            print(e.__cause__)
        except urllib.error.HTTPError as e:
            print(e.code, e.reason)
        except urllib.error.URLError as e:
            print(e.reason)
        if resp_html:
            resp_html = zlib.decompress(resp_html, 16 + zlib.MAX_WBITS).decode('utf8')
            reg = re.compile(r'&nbsp; : (.+?)\\u003Cdiv')
            content_list = re.findall(reg, resp_html)
            if content_list:
                self.imitate_post(tid, content_list)

    def imitate_post(self, tid, comment_list):
        sml_list = []
        for i in range(len(comment_list)):
            sml_list.append({'index': i, 'similar': 0})
            for j in range(i):
                if comment_list[i] == comment_list[j]:
                    sml_list[i]['similar'] += 1
        sml_list.sort(reverse=True, key=lambda x: x['similar'])
        if sml_list[0]['similar'] > 0:
            self.comment_post(tid, comment_list[sml_list[0]['index']])
            print(comment_list[sml_list[0]['index']])
            return

        cmt_list = []
        index = 0
        for comment in comment_list:
            comment = re.sub(r'\[em\]e\w+\[\\/em\]', '', comment)
            comment = re.sub(r'@\{uin:\d+,nick:.+?,who:\d+\}', '', comment)
            m = re.findall('(\w+)', comment)
            if m:
                cmt_list.append({'index': index, 'content': ''.join(m)})
            index += 1
        sml_list = []
        for i in range(len(cmt_list)):
            sml_list.append({'index': cmt_list[i]['index'], 'similar': 0})
            for j in range(i):
                if cmt_list[i]['content'] == cmt_list[j]['content']:
                    sml_list[i]['similar'] += 1
        sml_list.sort(reverse=True, key=lambda x: x['similar'])
        if sml_list[0]['similar'] > 0:
            self.comment_post(tid, comment_list[sml_list[0]['index']])
            print(comment_list[sml_list[0]['index']])
            return
        print('cant imitate!')

    def work_done(self):
        print('totally %s pieces of messages done!' % self.like_num)
        print('totally %s pages of messages!' % self.pages)

    def main(self):
        self.get_cookies()
        self.get_msg_id()


a = AutoDoLike('385204916', '155319144', 'bug终于解决了……')
if __name__ == '__main__':
    a.main()