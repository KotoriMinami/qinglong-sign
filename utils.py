import os
import json

from functools import wraps

path_list = [
    "/ql/config/sg_check.json",
    "/ql/data/config/sg_check.json",
    "sg_check.json",
    "./config/sg_check.json",
    "../config/sg_check.json",
]


class GetConfig(object):
    def __init__(self, script_name):
        self.script_name = script_name

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 优先取环境变量
            configs_env = os.getenv(f'{self.script_name}_ENV')
            if configs_env is None:
                config_path = None
                for path in path_list:
                    _config_path = os.path.join(os.getcwd(), path)
                    if os.path.exists(_config_path):
                        config_path = os.path.normpath(_config_path)
                        break
                if config_path:
                    print(f'配置地址：{config_path}')
                    with open(config_path, encoding="utf-8") as f:
                        try:
                            json_data = json.loads(f.read())
                            accounts = json_data.get(self.script_name, [])
                            func(*args, **kwargs, accounts = accounts)
                        except Exception as e:
                            print(e)
                            print("获取JSON数据失败，请检查 sg_check.json 文件格式是否正确！")
                    return;
            func(*args, **kwargs, accounts_env = configs_env)

        return wrapper