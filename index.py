import json
import time

import requests


from logger import logger
from config import Config

push_plus_token = ""
push_plus_group_token = ""
group_code = ""
login_case = ""


class Shana(object):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Cookie": "CASCID=CID2BFCADB9A0154A9D877294366E144906; sdo_cas_id=10.129.20.137; CAS_LOGIN_STATE=1; sdo_dw_track=G81Y/L1voXjLY8VH5ZWfpw==; CASTGC=ULSTGT-f0caef48519646a09e4ecee2f864e40a",
        "Host": "cas.sdo.com",
        "Pragma": "no-cache",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    def __init__(self) -> None:
        super().__init__()
        self.cookie = {}

    def __put_cookie(self, items):
        for item in items:
            self.cookie.setdefault(item[0], item[1])

    # 提交用户名和密码, 获取ticket
    def step1(self) -> str:
        global login_case
        logger.info("将以 %s/%s 登录" % (Config.login_name, Config.login_password))
        params = {
            "callback": "staticLogin_JSONPMethod",
            "inputUserId": Config.login_name,
            "password": Config.login_password,
            "appId": "100001900",
            "areaId": "1",
            "serviceUrl": "http://act.ff.sdo.com/20180707jifen/Server/SDOLogin.ashx?returnPage=index.html",
            "productVersion": "v5",
            "frameType": "3",
            "locale": "zh_CN",
            "version": "21",
            "tag": "20",
            "authenSource": "2",
            "productId": "2",
            "scene": "login",
            "usage": "aliCode",
            "customSecurityLevel": "2",
            "autoLoginFlag": "0",
            "_": int(round(time.time() * 1000)),
        }
        url = "https://cas.sdo.com/authen/staticLogin.jsonp"
        r = requests.get(url, params=params, headers=Shana.headers)
        self.__put_cookie(r.cookies.items())
        text = r.text
        text = text[text.find("(") + 1: text.rfind(")")]
        obj = json.loads(text)
        if "ticket" in obj["data"]:
            logger.info("登录成功, 正在设置cookie...")
            login_case = "登录成功, 正在设置cookie..."
            return obj["data"]["ticket"]
        else:
            logger.error("登录失败, 短期内登录失败次数过多, 服务器已开启验证码, 请在1-3天后再试...")
            login_case = "登录失败, 短期内登录失败次数过多, 服务器已开启验证码, 请在1-3天后再试..."
            return ""

    # 设置cookie
    def step2(self):
        url = "http://login.sdo.com/sdo/Login/Tool.php"
        params = {
            "value": "index|%s" % Config.login_name,
            "act": "setCookie",
            "name": "CURRENT_TAB",
            "r": "0.8326684884385089",
        }
        r = requests.get(url, params=params, cookies=self.cookie)
        self.__put_cookie(r.cookies.items())

    # 设置cookie
    def step3(self):
        url = "https://cas.sdo.com/authen/getPromotionInfo.jsonp"
        params = {
            "callback": "getPromotionInfo_JSONPMethod",
            "appId": "991000350",
            "areaId": "1001",
            "serviceUrl": "http://act.ff.sdo.com/20180707jifen/Server/SDOLogin.ashx?returnPage=index.html",
            "productVersion": "v5",
            "frameType": "3",
            "locale": "zh_CN",
            "version": "21",
            "tag": "20",
            "authenSource": "2",
            "productId": "2",
            "scene": "login",
            "usage": "aliCode",
            "customSecurityLevel": "2",
            "_": "1566623599098",
        }
        r = requests.get(url, params=params, cookies=self.cookie)
        self.__put_cookie(r.cookies.items())

    # 设置cookie
    def step4(self, ticket: str):
        url = "http://act.ff.sdo.com/20180707jifen/Server/SDOLogin.ashx?returnPage=index.html&ticket=" + ticket
        r = requests.get(url, cookies=self.cookie)
        self.__put_cookie(r.cookies.items())
        logger.info("设置cookie成功...")

    # 查询角色列表
    def step5(self) -> str:
        ipid = ""
        if Config.area_name == "陆行鸟":
            ipid = "1"
        elif Config.area_name == "莫古力":
            ipid = "6"
        else:
            ipid = "7"
        url = "http://act.ff.sdo.com/20180707jifen/Server/ff14/HGetRoleList.ashx"
        params = {
            "method": "queryff14rolelist",
            "ipid": ipid,
            "i": "0.8075943537407986",
        }
        r = requests.get(url, params=params, cookies=self.cookie)
        text = r.text
        obj = json.loads(text)
        attach = obj["Attach"]
        role = "{0}|{1}|{2}"
        logger.info("正在获取角色列表...")
        for r in attach:
            if r["worldnameZh"] == Config.server_name and r["name"] == Config.role_name:
                logger.info("获取角色列表成功...")
                return role.format(r["cicuid"], r["worldname"], r["groupid"])
        logger.error("获取角色列表失败...")
        return ""

    # 选择区服及角色
    def step6(self, role: str):
        url = "http://act.ff.sdo.com/20180707jifen/Server/ff14/HGetRoleList.ashx"
        AreaId = ""
        if Config.area_name == "陆行鸟":
            AreaId = "1"
        elif Config.area_name == "莫古力":
            AreaId = "6"
        else:
            AreaId = "7"
        params = {
            "method": "setff14role",
            "AreaId": AreaId,
            "AreaName": Config.area_name,
            "RoleName": "[%s]%s" % (Config.server_name, Config.role_name),
            "Role": role,
            "i": "0.8326684884385089",
        }
        r = requests.post(url, params=params, cookies=self.cookie)
        self.__put_cookie(r.cookies.items())
        logger.info("已选择目标角色...")

    # 签到
    def step7(self):
        logger.info("正在签到...")
        url = "http://act.ff.sdo.com/20180707jifen/Server/User.ashx"
        params = {
            "method": "signin",
            "i": "0.855755357775076"
        }
        r = requests.post(url, params=params, cookies=self.cookie)
        obj = json.loads(r.text)
        logger.info(obj["Message"])
        return obj["Message"]

    # 查询当前积分
    def step8(self):
        url = "http://act.ff.sdo.com/20180707jifen/Server/User.ashx"
        params = {
            "method": "querymystatus",
            "i": "0.855755357775076"
        }
        r = requests.post(url, params=params, cookies=self.cookie)
        obj = json.loads(r.text)
        attach = obj["Attach"]
        jifen = json.loads(attach)["Jifen"]
        logger.info("当前积分为: %d" % jifen)
        return "当前积分为: %d" % jifen

    def push_plus(self,push_content):
        global push_plus_token
        global push_plus_group_token
        if push_plus_token is None or push_plus_group_token is None:
            return
        logger.info("推送开始")
        if push_plus_token:
            url = "http://pushplus.hxtrip.com/send/"
            params = {
                "token": push_plus_token,
                "title":"FF14积分商城签到",
                "content":push_content
            }
            r = requests.post(url, params=params)
            logger.info(r.text)
        if push_plus_group_token:
            url = "http://pushplus.hxtrip.com/send/"
            params = {
                "token": push_plus_group_token,
                "title":"FF14积分商城签到",
                "content":push_content,
                "topic": group_code
            }
            requests.post(url, params=params)

    def go(self):
        push_plus_content = ''
        ticket = self.step1()
        if ticket == "":
            self.push_plus(push_plus_content+login_case)
            return
        self.step2()
        self.step3()
        self.step4(ticket)
        role = self.step5()
        if role == "":
            self.push_plus(push_plus_content + "查询角色列表失败")
            return
        self.step6(role)
        sign_result_string = self.step7()
        point_string = self.step8()
        self.push_plus(push_plus_content+Config.role_name+sign_result_string+point_string)
        time.sleep(5)

def main_handler(event,context):
    config_list = event["Message"].split("&")
    logger.info(config_list)
    Config.login_name = config_list[0]
    Config.login_password = config_list[1]
    Config.area_name = config_list[2]
    Config.server_name = config_list[3]
    Config.role_name = config_list[4]
    Shana().go()