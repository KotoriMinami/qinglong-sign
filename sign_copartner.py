# -*- coding: utf-8 -*-
"""
cron: 0 8 * * *
new Env('网易音乐合伙人');
"""
import random
import requests
import base64
import codecs

from Crypto.Cipher import AES
from time import sleep
from utils import GetConfig
from notify import send


def pkcs7padding(text):
    """
    实现PKCS#7填充算法
    
    Args:
        text: 需要填充的文本
        
    Returns:
        填充后的文本
    """
    bs = AES.block_size  # 16
    length = len(text)
    bytes_length = len(bytes(text, encoding='utf-8'))
    padding_size = length if (bytes_length == length) else bytes_length
    padding = bs - padding_size % bs
    padding_text = chr(padding) * padding
    return text + padding_text


def aes_encrypt(text, key, iv):
    """
    AES加密函数
    
    Args:
        text: 待加密文本
        key: 加密密钥
        iv: 初始化向量
        
    Returns:
        加密后的base64编码文本
    """
    key_bytes = bytes(key, encoding='utf-8')
    _iv = bytes(iv, encoding='utf-8')
    cipher = AES.new(key_bytes, AES.MODE_CBC, _iv)
    # 处理明文
    content_padding = pkcs7padding(text)
    # 加密
    encrypt_bytes = cipher.encrypt(bytes(content_padding, encoding='utf-8'))
    # 重新编码
    encrypt_text = str(base64.b64encode(encrypt_bytes), encoding='utf-8')
    return encrypt_text


def rsa_encrypt(text, pubKey, modulus):
    """
    RSA加密函数
    
    Args:
        text: 待加密文本
        pubKey: 公钥
        modulus: 模数
        
    Returns:
        加密后的十六进制文本
    """
    text = text[::-1]
    rs = int(codecs.encode(text.encode('utf-8'), 'hex_codec'), 16) ** int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)


def get_one_text():
    """
    获取一条关于网易云的一言
    
    Returns:
        一条随机的一言文本
    """
    url = "https://v1.hitokoto.cn/?c=j"
    res = requests.get(url).json()
    return res["hitokoto"]


def parse_accounts(env_str):
    """
    解析账号配置字符串
    
    Args:
        env_str: 账号配置字符串，格式为cookie&extra_count#comment
        
    Returns:
        解析后的账号配置列表
    """
    accounts = env_str.split('&')
    result = []
    for account in accounts:
        cookie, extra_count, comment = (account.split('#') + [None] * 3)[:3]
        result.append({
            "cookie": cookie, "extra_count": extra_count, "comment": comment
        })
    return result


# 获取i值的函数，即随机生成长度为16的字符串
def get_random_string(length):
    """
    生成指定长度的随机字符串
    
    Args:
        length: 要生成的字符串长度
        
    Returns:
        指定长度的随机字符串
    """
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    result = ""
    for i in range(length):
        result += random.choice(chars)
    return result


class Copartner():
    """网易音乐合伙人签到类"""
    name = "音乐合伙人"

    def __init__(self, check_item):
        """
        初始化音乐合伙人签到类
        
        Args:
            check_item: 包含cookie、extra_count和comment的字典
        """
        self.csrf = None
        self.musicDataUrl = "https://interface.music.163.com/api/music/partner/daily/task/get"
        self.userInfoUrl = "https://music.163.com/api/nuser/account/get"
        self.signUrl = "https://interface.music.163.com/weapi/music/partner/work/evaluate?csrf_token="
        self.extraMusicDataUrl = "https://interface.music.163.com/api/music/partner/extra/wait/evaluate/work/list"
        self.reportListenUrl = 'https://interface.music.163.com/weapi/partner/resource/interact/report?csrf_token='
        self.g = '0CoJUm6Qyw8W8jud'  # buU9L(["爱心", "女孩", "惊恐", "大笑"])的值
        self.b = "010001"  # buU9L(["流泪", "强"])的值
        # buU9L(Rg4k.md)的值
        self.c = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        self.i = get_random_string(16)  # 随机生成长度为16的字符串
        self.iv = "0102030405060708"  # 偏移量
        self.headers = {
            "Accept": "application/json, text/javascript",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "http://mp.music.163.com",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 CloudMusic/0.1.1 NeteaseMusic/8.8.01"
        }
        self.musicScoreRandomRange = [2, 4]
        self.waitRange = [15, 20]
        self.musicTags = [
            [
                "1-A-1",
                "1-B-1",
                "1-C-1",
                "1-D-1",
                "1-D-2"
            ],
            [
                "2-A-1",
                "2-B-1",
                "2-C-1",
                "2-D-1",
                "2-D-2"
            ],
            [
                "3-A-1",
                "3-A-2",
                "3-B-1",
                "3-C-1",
                "3-D-1",
                "3-D-2",
                "3-E-1",
                "3-E-2"
            ],
            [
                "4-A-1",
                "4-A-2",
                "4-B-1",
                "4-C-1",
                "4-D-1",
                "4-D-2",
                "4-E-1",
                "4-E-2"
            ],
            [
                "5-A-1",
                "5-A-2",
                "5-B-1",
                "5-C-1",
                "5-D-1",
                "5-D-2",
                "5-E-1",
                "5-E-2"

            ]
        ]
        self.cookie = check_item.get('cookie')
        self.extra_count = min(15, int(check_item.get('extra_count') or 7))
        self.enable_comment = check_item.get('comment') is not None and check_item.get('comment') != '0'

    def get_enc_sec_key(self):
        """
        获取加密的SecKey
        
        Returns:
            加密后的SecKey
        """
        return rsa_encrypt(self.i, self.b, self.c)

    def get_params(self, data):
        """
        获取加密后的参数
        
        Args:
            data: 需要加密的数据
            
        Returns:
            双重AES加密后的参数
        """
        enc_text = str(data)
        return aes_encrypt(aes_encrypt(enc_text, self.g, self.iv), self.i, self.iv)

    def wait_listen(self):
        """
        模拟听歌等待时间
        """
        wait = random.randint(self.waitRange[0], self.waitRange[1])
        sleep(wait)

    def merge_comment_params(self, params):
        """
        合并评论参数
        
        Args:
            params: 原始参数字典
            
        Returns:
            合并评论后的参数字典
        """
        if self.enable_comment:
            params["comment"] = get_one_text()
            params["syncComment"] = "true"
        return params

    def sign(self, session, music_data, msg):
        """
        执行基础评定签到
        
        Args:
            session: 请求会话
            music_data: 音乐数据
            msg: 消息列表，用于记录签到结果
        """
        works = music_data['works']
        task_id = music_data['id']
        begin = False
        for work in works:
            _work = work['work']
            if work['completed']:
                msg.append({
                    "name": f"{_work['name']}（{_work['authorName']}）",
                    "value": f"评分完成：{work['score']}分"
                })
            else:
                if not begin:
                    msg.append({"name": "本次进度", "value": ""})
                    begin = True
                self.wait_listen()  # 等都等了，一起等吧.. 要是加了获取列表时间和提交时间，也能用
                score = self.get_random_score()
                tags = self.get_random_tags(score)
                params = self.merge_comment_params({
                    "taskId": task_id,
                    "workId": _work['id'],
                    "score": score,
                    "tags": tags,
                    "customTags": "[]",
                    "comment": "",
                    "syncYunCircle": "true",
                    "syncComment": "false",
                    "extraScore": str({
                        "1": self.get_random_score(),
                        "2": self.get_random_score(),
                        "3": self.get_random_score(),
                    }),
                    "source": "mp-music-partner",
                    "csrf_token": self.csrf
                })
                data = {
                    "params": self.get_params(params).replace("\n", ""),
                    "encSecKey": self.get_enc_sec_key()
                }
                try:
                    response = session.post(
                        url=f"{self.signUrl}={self.csrf}",
                        data=data, headers=self.headers).json()
                    if response["code"] == 200:
                        msg.append({
                            "name": f"{_work['name']}（{_work['authorName']}）",
                            "value": f"评分完成：{score}分"
                        })
                except Exception as e:
                    print(f"歌曲 {_work['name']} 评分异常,原因{str(e)}")

    def sign_extra(self, session, music_data, task_id, msg):
        """
        执行额外评定签到
        
        Args:
            session: 请求会话
            music_data: 音乐数据
            task_id: 任务ID
            msg: 消息列表，用于记录签到结果
        """
        work = music_data['work']
        # 先上报，再提交
        report_data = {
            "params": self.get_params({
                "workId": work['id'],
                "resourceId": work['resourceId'],
                "bizResourceId": "",
                "interactType": "PLAY_END"
            }),
            "encSecKey": self.get_enc_sec_key()
        }
        try:
            response = session.post(
                url=f"{self.reportListenUrl}={self.csrf}",
                data=report_data, headers=self.headers).json()
            if response["code"] != 200:
                msg.append({
                    "name": f"{work['name']}（{work['authorName']}）",
                    "value": f"上报失败：{response['message']}"
                })
                return
        except Exception as e:
            print(f"歌曲 {work['name']} 上报失败,原因{str(e)}")
            return

        # reportListen
        score = self.get_random_score()
        tags = self.get_random_tags(score)
        params = self.merge_comment_params({
            "taskId": task_id,
            "workId": work['id'],
            "score": score,
            "tags": tags,
            "customTags": "[]",
            "comment": "",
            "syncYunCircle": "true",
            "syncComment": "false",
            "extraScore": str({
                "1": self.get_random_score(),
                "2": self.get_random_score(),
                "3": self.get_random_score(),
            }),
            "extraResource": "true",
            "source": "mp-music-partner",
            "csrf_token": self.csrf
        })

        data = {
            "params": self.get_params(params).replace("\n", ""),
            "encSecKey": self.get_enc_sec_key()
        }
        try:
            response = session.post(
                url=f"{self.signUrl}={self.csrf}",
                data=data, headers=self.headers).json()
            if response["code"] == 200:
                msg.append({
                    "name": f"{work['name']}（{work['authorName']}）",
                    "value": f"评分完成：{score}分"
                })
            else:
                msg.append({
                    "name": f"{work['name']}（{work['authorName']}）",
                    "value": f"评分失败：{response['message']}"
                })
        except Exception as e:
            print(f"歌曲 {work['name']} 评分异常,原因{str(e)}")

    def valid(self, session):
        """
        验证登录状态并获取音乐数据
        
        Args:
            session: 请求会话
            
        Returns:
            成功返回(音乐数据, 用户名)，失败返回(False, 错误信息)
        """
        try:
            content = session.get(url=self.musicDataUrl,
                                  headers={**self.headers, "Referer": "https://mp.music.163.com/"})
        except Exception as e:
            return False, f"登录验证异常,错误信息: {e}"
        data = content.json()
        if data["code"] == 301:
            return False, data["message"]
        if data["code"] == 200:
            music_data = data["data"]
            user_name = self.login_info(session=session)["profile"]["nickname"]
            return music_data, user_name
        return False, "登录信息异常"

    def get_random_score(self):
        """
        获取随机评分
        
        Returns:
            随机评分值(2-4)
        """
        return random.randint(self.musicScoreRandomRange[0], self.musicScoreRandomRange[1])

    def get_random_tags(self, score):
        """
        根据评分获取随机标签
        
        Args:
            score: 评分值
            
        Returns:
            随机选择的标签字符串，以逗号分隔
        """
        num_to_select = random.randint(1, 3)
        current_score_tags = self.musicTags[score - 1]
        selected_values = random.sample(current_score_tags, num_to_select)
        return ','.join(selected_values)

    def get_extra_music(self, session):
        """
        获取额外评定音乐列表
        
        Args:
            session: 请求会话
            
        Returns:
            (未完成的额外评定列表, 已完成的额外评定数量)
        """
        try:
            content = session.get(url=self.extraMusicDataUrl,
                                  headers={**self.headers, "Referer": "https://mp.music.163.com/"})
        except Exception as e:
            return [], f"登录验证异常,错误信息: {e}"
        data = content.json()
        if data["code"] == 301:
            return False, data["message"]
        if data["code"] == 200:
            extra_music_data = data["data"]
            computed_music = []
            undone_music = []
            for x in extra_music_data:
                if x['completed']:
                    computed_music.append(x)
                else:
                    undone_music.append(x)
            extra_count = self.extra_count - len(computed_music)
            return [] if extra_count < 0 else undone_music[:extra_count], len(computed_music)
        return [], "登录信息异常"

    def login_info(self, session):
        """
        获取登录用户信息
        
        Args:
            session: 请求会话
            
        Returns:
            用户信息字典
        """
        try:
            return session.get(url=self.userInfoUrl, headers=self.headers).json()
        except Exception as e:
            print(e)
            return {
                "profile": {
                    "nickname": "获取用户信息异常"
                }
            }

    def main(self):
        """
        主函数，执行签到流程
        
        Returns:
            签到结果消息
        """
        session = requests.session()
        cookie = self.cookie
        music_cookie = {item.split("=")[0]: item.split("=")[1] for item in cookie.split("; ")}
        self.csrf = music_cookie['__csrf']
        requests.utils.add_dict_to_cookiejar(session.cookies, music_cookie)
        music_data, user_name = self.valid(session)
        if music_data:
            completed = music_data['completed']
            msg = [
                {"name": "帐号信息", "value": f"{user_name}"},
                {"name": "当前进度", "value": ""},
                {"name": "基础评定完成状态", "value": f"{'已完成' if completed else '未完成'}"},
                {"name": "基础评定获得积分", "value": music_data['integral']},
                {"name": "基础评定已完成数", "value": music_data["completedCount"]},
            ]
            if not completed:
                self.sign(session, music_data, msg)
            extra_music_data, extra_music_computed_count = self.get_extra_music(session)
            if len(extra_music_data):
                msg.append({"name": "待额外评定数", "value": len(extra_music_data)})
                task_id = music_data['id']
                for x in extra_music_data:
                    self.wait_listen()  # 此接口单次提交，随机等待15-20s，假装在听歌？
                    self.sign_extra(session, x, task_id, msg)
            else:
                msg.append({"name": "额外评定完成数", "value": f"{extra_music_computed_count}"})
        else:
            msg = [
                {"name": "帐号信息", "value": user_name},
                {"name": "cookie信息", "value": "Cookie 可能过期"},
            ]
        msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return msg


@GetConfig(script_name='MUSIC_COPARTNER')
def main(*args, **kwargs):
    """
    主入口函数
    
    Args:
        *args: 可变参数
        **kwargs: 关键字参数，包含accounts和accounts_env
    """
    accounts = kwargs.get('accounts')
    accounts_env = kwargs.get('accounts_env')
    if accounts_env:
        accounts = parse_accounts(accounts_env)
    res = ""
    for index, account in enumerate(accounts):
        res = f'{res}账号{index + 1}：\n{Copartner(account).main()}\n'
    print(res)
    send('网易音乐合伙人', res)


if __name__ == "__main__":
    main()
