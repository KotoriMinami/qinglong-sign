# -*- coding: utf-8 -*-
"""
cron: 0 9 * * *
new Env('什么值得买');
"""

import requests
import json

from notify import send

class Smzdm():
    name = "什么值得买"

    def __init__(self, check_item):
        self.csrf = None
        self.signUrl = "https://zhiyou.smzdm.com/user/checkin/jsonp_checkin"
        self.userUrl = "https://zhiyou.smzdm.com/user/info/jsonp_get_current"
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Host": "zhiyou.smzdm.com",
            "Referer": "https://www.smzdm.com/",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        self.check_item = check_item

    def sign(self, session, smzdm_data, msg):
        try:
            response = session.get(
                url=self.signUrl, headers=self.headers)
            if response.status_code == 200:
                checkin_num = response.json().get("data", {}).get('checkin_num', {})
                msg.append({"name": "已经签到", "value": f"{checkin_num} 天"})
        except Exception as e:
            msg = [
                {"name": "签到信息", "value": "签到失败"},
                {"name": "错误信息", "value": str(e)},
            ]

    def valid(self, session):
        try:
            content = session.get(url=self.userUrl,
                                  headers={**self.headers})
        except Exception as e:
            return False, f"登录验证异常,错误信息: {e}"
        data = content.json()
        if content.status_code == 200:
            return data, ""
        return False, "登录信息异常"

    def main(self):
        session = requests.session()
        cookie = self.check_item.get("cookie")
        smzdm_cookie = {item.split("=")[0]: item.split("=")[1] for item in cookie.split("; ")}
        requests.utils.add_dict_to_cookiejar(session.cookies, smzdm_cookie)
        smzdm_data, user_name = self.valid(session)
        if smzdm_data:
            completed = smzdm_data["checkin"]["has_checkin"]
            msg = [
                {"name": "账号信息", "value": smzdm_data.get("nickname", "")},
                {"name": "目前积分", "value": smzdm_data.get("point", "")},
                {"name": "当前经验", "value": smzdm_data.get("exp", "")},
                {"name": "当前金币", "value": smzdm_data.get("gold", "")},
                {"name": "碎银子数", "value": smzdm_data.get("silver", "")},
                {"name": "当前威望", "value": smzdm_data.get("prestige", "")},
                {"name": "当前等级", "value": smzdm_data.get("level", "")}
            ]
            if not completed:
                self.sign(session, smzdm_data, msg)
            else:
                msg.append({"name": "已经签到", "value": f"{smzdm_data.get('checkin', {}).get('daily_checkin_num', '')} 天"})
        else:
            msg = [
                {"name": "cookie信息", "value": "Cookie 可能过期"},
            ]
        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return msg


if __name__ == "__main__":
    with open("/ql/config/sg_check.json", "r", encoding="utf-8") as f:
        all_data = json.loads(f.read())
        _check_item = all_data.get("SMZDM", [])
        res = ""
        for index, item in enumerate(_check_item):
            res = f'{res}账号{index + 1}：\n{Smzdm(item).main()}\n'
        print(res)
        send('什么值得买', res)
