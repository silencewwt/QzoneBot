# -*-coding:utf-8-*-

import os
import re
import sys
import time
import zlib
import sqlite3
import threading
import urllib.parse
import urllib.request
import urllib.error
import http.client
import http.cookies
import http.cookiejar
import win32crypt
from hashlib import md5


class QzoneAuto(threading.Thread):
    def __init__(self, client, self_id, password, target_id, vote, imitate, comment):
        threading.Thread.__init__(self)
        self.client = client
        self.self_id = self_id
        self.target_id = target_id
        self.password = password
        self.cond = threading.Condition()
        self.verify_code = ''
        self.vote = vote
        self.imitate = imitate
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
        self.cookie_jar = http.cookiejar.CookieJar()
        self.handler = urllib.request.HTTPCookieProcessor(self.cookie_jar)
        self.opener = urllib.request.build_opener(self.handler)
        urllib.request.install_opener(self.opener)

    def login(self):
        def hexchar2bin(hex_str):
            str_list = []
            for i in range(len(hex_str)//2):
                str_list.append(chr(int(hex_str[2*i:2*i+2], 16)))
            return ''.join(str_list)
        login_sig = ''
        sig_url = 'http://ui.ptlogin2.qq.com/cgi-bin/login?hide_title_bar=1&low_login=0&qlogin_auto_login=1&' \
                  'no_verifyimg=1&link_target=blank&appid=549000912&style=12&target=self&s_url=http%3A//qzs.qq.com/' \
                  'qzone/v5/loginsucc.html?para=reload&pt_qr_app=%CA%D6%BB%FAQQ%BF%D5%BC%E4&pt_qr_link=http%3A//z.' \
                  'qzone.com/download.html&self_regurl=http%3A//qzs.qq.com/qzone/v6/reg/index.html&pt_qr_help_link=' \
                  'http%3A//z.qzone.com/download.html'
        headers = {'Host': 'ui.ptlogin2.qq.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/36.0.1985.125 Safari/537.36',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3', 'Accept-Encoding': 'gzip, deflate',
                   'Referer': 'http://user.qzone.qq.com/%s/main' % self.target_id, 'Connection': 'keep-alive',
                   'If-Modified-Since': 'Mon, 28 Jul 2014 01:30:00 GMT'}
        req = urllib.request.Request(sig_url, headers=headers)
        try:
            resp_html = urllib.request.urlopen(req).read()
        except urllib.error.HTTPError as e:
            print(e.code, e.reason)
            return
        except urllib.error.URLError as e:
            print(e.reason)
            return
        if not resp_html:
            return
        resp_html = zlib.decompress(resp_html, 16 + zlib.MAX_WBITS).decode('utf8')
        login_sig = re.search('login_sig:"(.*?)"', resp_html).group(1)
        if not login_sig:
            print('get sig failed!')
            return
        check_url = 'http://check.ptlogin2.qq.com/check?regmaster=&uin={}&appid=549000912&js_ver=10087&js_type=1&' \
                    'login_sig={}&u1=http%3A%2F%2Fqzs.qq.com%2Fqzone%2Fv5%2Floginsucc.html%3Fpara%3Dreload&' \
                    'r=0.11670281237108926'.format(self.self_id, login_sig)
        check_headers = {'Host': 'ui.ptlogin2.qq.com',
                         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                       'Chrome/36.0.1985.125 Safari/537.36',
                         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                         'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3', 'Accept-Encoding': 'gzip, deflate',
                         'Referer': 'http://user.qzone.qq.com/%s/main' % self.target_id, 'Connection': 'keep-alive'}
        cookie_list = []
        for cookie in self.cookie_jar:
            cookie_list.append('%s=%s; ' % (cookie.name, cookie.value))
        cookie_str = ''.join(cookie_list)
        check_headers['Cookie'] = cookie_str
        req = urllib.request.Request(check_url, headers=check_headers)
        try:
            resp_html = urllib.request.urlopen(req).read().decode('utf8')
        except urllib.error.HTTPError as e:
            print(e.code, e.reason)
            return
        except urllib.error.URLError as e:
            print(e.reason)
            return
        if not resp_html:
            return
        check_list = re.findall("'(.*?)'", resp_html)
        uin = re.sub('\\\\x', '', check_list[2])
        uin = hexchar2bin(uin).encode('iso-8859-1')
        str1 = hexchar2bin(md5(self.password.encode('iso-8859-1')).hexdigest()).encode('iso-8859-1')
        str2 = md5(str1 + uin).hexdigest().upper().encode('iso-8859-1')
        if True:
            verify_code_url = 'http://captcha.qq.com/getimage?uin={}&aid=549000912&cap_cd={}&0.7367948200565873'
            verify_code_url = verify_code_url.format(self.self_id, check_list[1])
            cookie_list = []
            verify_code_headers = {'Host': 'captcha.qq.com', 'Connection': 'keep-alive',
                                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like '
                                                 'Gecko) Chrome/36.0.1985.125 Safari/537.36',
                                   'Accept': 'image/png,image/*;q=0.8,*/*;q=0.5', 'Accept-Encoding': 'gzip, deflate',
                                   'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
                                   'Referer': 'http://ui.ptlogin2.qq.com/cgi-bin/login?hide_title_bar=1&low_login=0&'
                                              'qlogin_auto_login=1&no_verifyimg=1&link_target=blank&appid=549000912&'
                                              'style=12&target=self&s_url=http%3A//qzs.qq.com/qzone/v5/loginsucc.html?'
                                              'para=reload&pt_qr_app=%CA%D6%BB%FAQQ%BF%D5%BC%E4&pt_qr_link=http%3A//z.'
                                              'qzone.com/download.html&self_regurl=http%3A//qzs.qq.com/qzone/v6/reg/'
                                              'index.html&pt_qr_help_link=http%3A//z.qzone.com/download.html'}
            for cookie in self.cookie_jar:
                cookie_list.append('%s=%s; ' % (cookie.name, cookie.value))
            cookie_str = ''.join(cookie_list)
            verify_code_headers['Cookie'] = cookie_str
            # req = urllib.request.Request(verify_code_url, headers=verify_code_headers)
            # resp_html = urllib.request.urlopen(req).read()
            urllib.request.urlretrieve(verify_code_url, 'verifycode.jpg')
            self.client.entry_verify_code()

            self.cond.acquire()
            self.cond.wait()
            self.get_verify_code()
            self.cond.release()
            print(self.verify_code)

            psw_encode = md5(str2 + self.verify_code).hexdigest().upper()
        login_url = 'http://ptlogin2.qq.com/login?u={}&verifycode={}&pt_vcode_v1=0&pt_verifysession_v1=dabe22d7b2099' \
                    'ab14e9d7a658c604a6c5f3904f91b3c3ea033b5bb63965e37befce36a0943b7ad0e15a7698fed250f91&p={}&' \
                    'pt_rsa=0&u1=http%3A%2F%2Fqzs.qq.com%2Fqzone%2Fv5%2Floginsucc.html%3Fpara%3Dizone&ptredirect=0&' \
                    'h=1&t=1&g=1&from_ui=1&ptlang=2052&action=2-8-1407072058849&js_ver=10087&js_type=1&login_sig={}&' \
                    'pt_uistyle=32&aid=549000912&daid=5&pt_qzone_sig=1&'
        login_url = login_url.format(self.self_id, self.verify_code, psw_encode, login_sig)
        login_headers = {'Host': 'ptlogin2.qq.com', 'Connection': 'keep-alive', 'Accept': '*/*',
                         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                       'Chrome/36.0.1985.125 Safari/537.36',
                         'Referer': 'http://xui.ptlogin2.qq.com/cgi-bin/xlogin?proxy_url=http%3A//qzs.qq.com/qzone/'
                                    'v6/portal/proxy.html&daid=5&pt_qzone_sig=1&hide_title_bar=1&low_login=0&'
                                    'qlogin_auto_login=1&no_verifyimg=1&link_target=blank&appid=549000912&style=22&'
                                    'target=self&s_url=http%3A//qzs.qq.com/qzone/v5/loginsucc.html?para=izone&'
                                    'pt_qr_app=%E6%89%8B%E6%9C%BAQQ%E7%A9%BA%E9%97%B4&pt_qr_link=http%3A//z.qzone.com/'
                                    'download.html&self_regurl=http%3A//qzs.qq.com/qzone/v6/reg/index.html&'
                                    'pt_qr_help_link=http%3A//z.qzone.com/download.html',
                         'Accept-Encoding': 'gzip,deflate,sdch', 'Accept-Language': 'zh-CN,zh;q=0.8'}
        login_headers['Cookie'] = cookie_str
        print('asdf')
        req = urllib.request.Request(login_url, headers=login_headers)
        resp_html = urllib.request.urlopen(req).read()
        resp_html = zlib.decompress(resp_html, 16 + zlib.MAX_WBITS).decode('utf8')
        with open('123.htm', 'w', encoding='utf8') as html:
            html.write(resp_html)

    def get_verify_code(self):
        self.verify_code = self.client.verify_code.upper().encode('iso-8859-1')

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
        reg = r'\[\\/em\]'
        reg = re.compile(reg)
        while True:
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
            resp_html = re.sub(reg, '[/em]', resp_html)
            with open('%s.htm' % self.pages, 'w', encoding='utf8') as htm:
                htm.write(resp_html)
            null = None
            page_data = eval(resp_html[10:-2])
            if 'msglist' not in page_data:
                self.work_done()
                return
            target_list = []
            for msg in page_data['msglist']:
                target_list.append(msg['tid'])
            msg_list = []
            for tid in target_list:
                if tid not in msg_list:
                    self.msg_list.append(tid)
                    msg_list.append(tid)

            if self.imitate:
                for msg in page_data['msglist']:
                    if msg['cmtnum'] > 1:
                        comment_list = []
                        for cmt in msg['commentlist']:
                            comment_list.append(cmt['content'])
                        self.imitate_post(msg['tid'], comment_list)
            if self.vote:
                self.vote_post(msg_list)
            if self.comment:
                self.comment_post(msg_list, self.comment)
            # self.get_more_comment(msg_list)
            self.pages += 1
            print('%s pages done!' % self.pages)

    def vote_post(self, target_list):
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
                urllib.request.urlopen(req).read()
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
            self.comment_post([tid], comment_list[sml_list[0]['index']])
            return

        cmt_list = []
        index = 0
        for comment in comment_list:
            comment = re.sub(r'\[em\]e\w+\[/em\]', '', comment)
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
            self.comment_post([tid], comment_list[sml_list[0]['index']])
            return
        print('cant imitate!')

    def work_done(self):
        print('totally %s pieces of messages done!' % self.like_num)
        print('totally %s pages of messages!' % self.pages)

    def run(self):
        self.login()
        self.get_cookies()
        self.get_msg_id()