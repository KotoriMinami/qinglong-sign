# -*- coding: utf-8 -*-
"""
cron: 0 9 * * *
new Env('九号出行');
"""

import requests
import json
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from notify import send
from utils import GetConfig
from datetime import datetime
import time
import random

def create_session():
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[408, 429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    return session

def parse_accounts(env_str):
    accounts = env_str.split('&')
    result = []
    for account in accounts:
        device_id, authorization, ua = account.split('#')
        result.append({
            "deviceId": device_id, 
            "authorization": authorization,
            "ua": ua
        })
    return result

class Ninebot():
    name = "九号出行"

    def __init__(self, check_item):
        self.signUrl = "https://cn-cbu-gateway.ninebot.com/portal/api/user-sign/v2/sign"
        self.validUrl = "https://cn-cbu-gateway.ninebot.com/portal/api/user-sign/v2/status"
        self.headers = {
            "Authorization": check_item.get("authorization"),
            "language": "zh",
            "User-Agent": check_item.get("ua"),
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
        self.check_item = check_item
        self.session = create_session()

    def safe_request(self, method, url, **kwargs):
        try:
            # 添加随机延迟避免高频请求
            time.sleep(random.uniform(0.5, 1.5))
            
            response = self.session.request(
                method=method,
                url=url,
                timeout=(10, 30),
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {str(e)}")
            return {"code": -1, "msg": str(e)}

    def sign(self, msg):
        try:
            response_data = self.safe_request(
                "POST",
                self.signUrl,
                headers=self.headers,
                json={"deviceId": self.check_item.get("deviceId")}
            )
            
            if response_data.get("code") == 0:
                msg.append({"name": "签到成功", "value": response_data.get("msg", "")})
            else:
                msg.append({"name": "签到失败", "value": response_data.get("msg", str(response_data))})
        except Exception as e:
            msg.extend([
                {"name": "签到信息", "value": "签到失败"},
                {"name": "错误信息", "value": str(e)},
            ])

    def valid(self):
        try:
            response_data = self.safe_request(
                "GET",
                f"{self.validUrl}?t={int(datetime.now().timestamp() * 1000)}",
                headers=self.headers
            )
            
            if response_data.get("code") == 0:
                return response_data.get("data", False), ""
            return False, response_data.get("msg", "验证失败")
        except Exception as e:
            return False, f"登录验证异常: {str(e)}"

    def main(self):
        valid_data, err_info = self.valid()
        msg = []
        if valid_data:
            completed = valid_data.get("currentSignStatus") == 1
            msg.extend([
                {"name": "连续签到天数", "value": f"{valid_data.get('consecutiveDays', '')}天"},
                {"name": "今日签到状态", "value": "已签到" if completed else "未签到"}
            ])
            if not completed:
                self.sign(msg)
        else:
            msg.append({"name": "验证信息", "value": err_info})
        
        return "\n".join([f"{item.get('name')}: {item.get('value')}" for item in msg])

@GetConfig(script_name='NINEBOT')
def main(*args, **kwargs):
    accounts = kwargs.get('accounts')
    accounts_env = kwargs.get('accounts_env')
    if accounts_env:
        accounts = parse_accounts(accounts_env)
    
    results = []
    for index, account in enumerate(accounts):
        try:
            result = f"账号{index + 1}：\n{Ninebot(account).main()}"
            results.append(result)
            print(result)
        except Exception as e:
            error_msg = f"账号{index + 1}处理异常: {str(e)}"
            results.append(error_msg)
            print(error_msg)
    
    send('九号出行', "\n\n".join(results))

if __name__ == "__main__":
    main()
