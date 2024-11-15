# -*- coding: utf-8 -*-
"""
cron: 0 9 * * *
new Env('九号出行');
"""

import requests
import json


from notify import send

class Ninebot():
    name = "九号出行"

    def __init__(self, check_item):
        self.signUrl = "https://cn-cbu-gateway.ninebot.com/portal/api/user-sign/v1/sign"
        self.validUrl = "https://cn-cbu-gateway.ninebot.com/portal/api/user-sign/v1/status"
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": check_item.get("authorization"),
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "cn-cbu-gateway.ninebot.com",
            "Origin": "https://api5-h5-app-bj.ninebot.com",
            "from_platform_1": "1",
            "language": "zh",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Segway v6 C 606093338",
            "Referer": "https://api5-h5-app-bj.ninebot.com/"
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
                    checkin_num = response.json().get("data", {}).get('consecutiveDays')
                    msg.append({"name": "签到成功", "value": f"已连续签到{checkin_num}天"})
                else:
                    msg.append({"name": "签到失败", "value": f"{response_data.get('msg')}"})
        except Exception as e:
            msg.extend([
                {"name": "签到信息", "value": "签到失败"},
                {"name": "错误信息", "value": str(e)},
            ])

    def valid(self, session):
        try:
            content = session.get(url=self.validUrl, headers={**self.headers})
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


if __name__ == "__main__":
    with open("/ql/config/sg_check.json", "r", encoding="utf-8") as f:
        all_data = json.loads(f.read())
        _check_item = all_data.get("NINEBOT", [])
        res = ""
        for index, item in enumerate(_check_item):
            res = f'{res}账号{index + 1}：\n{Ninebot(item).main()}\n'
        print(res)
        send('九号出行', res)
