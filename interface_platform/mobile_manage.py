# coding: utf-8

from pyDes import *
import base64
import hashlib
import binascii
from model import itsettings

reload(sys)
sys.setdefaultencoding('utf-8')

class MobileManage:
    """Mobile Http Client"""

    def __init__(self):
        pass

    def encrpyt(self, key, data):
        if len(key) != 8:
            print 'key length is not 16!'
            return None
        """DES对称加密"""
        k = des(str(key), ECB, pad=None, padmode=PAD_PKCS5)
        d = k.encrypt(str(data))
        """base64加密"""
        return base64.b64encode(d)

    def decrypt(self, key, data):
        if len(key) != 8:
            print 'key length is not 16!'
            return None
        """base64解密"""
        d = base64.b64decode(data)
        """DES对称解密"""
        k = des(key, ECB, pad=None, padmode=PAD_PKCS5)
        destr = k.decrypt(d)
        return destr

    def getkey(self, key1, unique):
        """generate the key of DES"""
        print 'uuid is ' + unique
        listuuid = []
        listuuid.append(unique[0:4])
        listuuid.append(unique[4:8])
        listuuid.append(unique[8:12])
        listuuid.append(unique[12:16])
        listuuid.append(unique[16:20])
        listuuid.append(unique[20:24])
        listuuid.append(unique[24:28])
        listuuid.append(unique[28:32])
        listcrc32 = []
        for element in listuuid:
            listcrc32.append(binascii.crc32(element))
        list32 = []
        for element in listcrc32:
            list32.append(element % 32)
        key = key1[list32[0]] + key1[list32[1]] + key1[list32[2]] + key1[list32[3]] + key1[list32[4]] + key1[
            list32[5]] + key1[list32[6]] + key1[list32[7]]
        print 'key is ' + key
        return key

    def generate_sign(self,key,enbody,unique):
		"""generate sign, sign = sha1(key+time+unique+enbody),then transform 16 byte string"""

		value = str(key) + str(itsettings.current_time) + str(unique) + str(enbody)
		h = hashlib.sha1()
		h.update(value)
		return h.hexdigest()

    # def qrcode_get(self, url, uid, key2):
    #
    #     uidencode = base64.b64encode(uid)
    #     # 手机端扫描二维码
    #     unique = str(uuid.uuid1()).replace('-', '')
    #     key = self.getkey(key2, unique)
    #
    #     # 计算签名
    #     value = key2 + uidencode + str(time)
    #     h = hashlib.sha1()
    #     h.update(value)
    #     sign = h.hexdigest()
    #     # 发送请求
    #     http = httplib2.Http()
    #     qrpara = {'uid': uidencode, 'timestamp': str(time), 'signature': sign, 'unique': unique}
    #     geturl = url + "&" + self.encodepara(str(qrpara))
    #     print 'HttpGet url is ' + geturl
    #     try:
    #         http = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
    #         resp, content = http.request(geturl, 'GET')
    #     except Exception, e:
    #         raise e
    #     else:
    #         de_content = self.decrypt(key, content)
    #         res_content = self.replace_null(de_content)
    #         print 'send HttpPost successful! content is ' + res_content
    #         return res_content.decode('utf-8')
    #         # print content
    #
    # def encodepara(self, para):
    #     encodepara = urllib.urlencode(eval(para))
    #     return encodepara
    #
    # def replace_null(self, response):
    #     strres = json.dumps(response, ensure_ascii=False)
    #     return eval(strres.replace('null', '\\"null\\"').replace('false', '\\"false\\"').replace('true', '\\"true\\"'))
    #
    # def checkport(self):
    #     global host
    #     global port
    #     if port == 0:
    #         url = host
    #     else:
    #         url = host + ':' + str(port)
    #     return url
    #
    # def mobile_environment_config(self, h, p):
    #     """Set HTTP Request host and port,host and port is global variable.
    #     host default value is https://b.yixin.im,port default value is 0.
    #
    #     Examples:
    #     | Environment Mobile Config| host | port |
    #     """
    #     global host
    #     global port
    #     host = h
    #     port = p
    #     print 'host is ' + h
    #     print 'port is ' + str(p)
    #
    # def get_app_oAuth(self, url, user, password, mac):
    #     ###获取重定向URL###
    #     r = requests.get(url)
    #     oAuthUrl = r.history[1].url
    #
    #     ###去服务器拿临时票据ticket###
    #     # 调用102登录接口#
    #     para_login = str({"c": login_port})
    #     body_login = str({"email": user, "password": password, "mac": mac})
    #     res_login = self.mobile_post(para_login, body_login, '["password"]')
    #     res_json_login = json.loads(res_login)
    #     uid_login = str(res_json_login["result"]["uid"])
    #     key2_login = str(res_json_login["result"]["key2"])
    #     # 调用901获取应用免登票据#
    #     para = str({"c": ticket_port})
    #     body = '{"url": "' + oAuthUrl + '"}'
    #     sbody = str(body)
    #     res_ticket = self.mobile_post(para, sbody, "None", key2_login, uid_login)
    #     st = json.loads(res_ticket).get('result').get('st')
    #
    #     ###oauth地址加上st参数,获取带code地址###
    #     url_st = oAuthUrl + "&st=" + st
    #     url_code = requests.get(url_st).url
    #     print url_code
    #     return url_code