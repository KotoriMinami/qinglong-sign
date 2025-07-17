# -*- coding: utf-8 -*-
"""
cron: 0 9 * * *
new Env('九号出行');
"""

import requests
import json


from notify import send
from utils import GetConfig
from datetime import datetime

def parse_accounts(env_str):
    accounts = env_str.split('&')
    result = []
    for account in accounts:
        device_id, authorization, ua = account.split('#')
        result.append({
            "deviceId": device_id, "authorization": authorization, "ua": ua
        })
    return result

class Ninebot():
    name = "九号出行"

    def __init__(self, check_item):
        self.signUrl = "https://cn-cbu-gateway.ninebot.com/portal/api/user-sign/v2/sign"
        self.validUrl = "https://cn-cbu-gateway.ninebot.com/portal/api/user-sign/v2/status"
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": check_item.get("authorization"),
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Content-Type": "application/json",
            "Host": "cn-cbu-gateway.ninebot.com",
            "Origin": "https://h5-bj.ninebot.com",
            "from_platform_1": "1",
            "language": "zh",
            "User-Agent": check_item.get("ua"),
            "Referer": "https://h5-bj.ninebot.com/",
            "sys_language": "zh-CN",
            "platform": "h5",
            "device_id": check_item.get("device_id"),
            "Connection": "keep-alive"
        }
        self.check_item = check_item

    def sign(self, session, msg):
        try:
            response = session.post(
                url=self.signUrl, headers=self.headers, json={
                    "deviceId": self.check_item.get("deviceId")
                })
            if response.status_code == 200:
                response_data = response.json()
                if (response_data.get("code") == 0):
                    # checkin_num = response.json().get("data", {}).get('consecutiveDays')
                    msg.append({"name": "签到成功", "value": f""})
                else:
                    msg.append({"name": "签到失败", "value": f"{response_data.get('msg')}"})
        except Exception as e:
            msg.extend([
                {"name": "签到信息", "value": "签到失败"},
                {"name": "错误信息", "value": str(e)},
            ])

    def valid(self, session):
        try:
            content = session.get(url=f"{self.validUrl}?t={int(datetime.now().timestamp() * 1000)}", headers={**self.headers})
        except Exception as e:
            return False, f"登录验证异常,错误信息: {e}"
        json_data = content.json()
        if content.status_code == 200:
            if json_data.get("code") == 0:
                return json_data.get("data", False), ""
            else:
                return False, json.get("msg")
        return False, "登录信息异常"

    def main(self):
        session = requests.session()
        valid_data, err_info = self.valid(session)
        if valid_data:
            completed = valid_data.get("currentSignStatus") == 1
            msg = [
                {"name": "连续签到天数", "value": f"{valid_data.get('consecutiveDays', '')}天"},
                {"name": "今日签到状态", "value": "已签到" if completed else "未签到"}
            ]
            if not completed:
                self.sign(session, msg)
        else:
            msg = [
                {"name": "cookie信息", "value": f"{err_info}"},
            ]
        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return msg


@GetConfig(script_name='NINEBOT')
def main(*args, **kwargs):
    accounts = kwargs.get('accounts')
    accounts_env = kwargs.get('accounts_env')
    if accounts_env:
        accounts = parse_accounts(accounts_env)
    res = ""
    for index, account in enumerate(accounts):
        res = f'{res}账号{index + 1}：\n{Ninebot(account).main()}\n'
    print(res)
    send('九号出行', res)


if __name__ == "__main__":
    main()
