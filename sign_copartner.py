# -*- coding: utf-8 -*-
"""
cron: 0 8 * * *
new Env('网易音乐合伙人');
"""
import random
from time import sleep

import requests
import base64
import codecs
import execjs
import json

from Crypto.Cipher import AES
from notify import send


def to_16(key):
    while len(key) % 16 != 0:
        key += '\0'
    return str.encode(key)


def aes_encrypt(text, key, iv):
    bs = AES.block_size
    pad2 = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
    encryptor = AES.new(to_16(key), AES.MODE_CBC, to_16(iv))
    encrypt_aes = encryptor.encrypt(str.encode(pad2(text)))
    encrypt_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')
    return encrypt_text


def rsa_encrypt(text, pubKey, modulus):
    text = text[::-1]
    rs = int(codecs.encode(text.encode('utf-8'), 'hex_codec'), 16) ** int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)


# 获取i值的函数，即随机生成长度为16的字符串
get_i = execjs.compile(r"""
    function a(a) {
        var d, e, b = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", c = "";
        for (d = 0; a > d; d += 1)
            e = Math.random() * b.length,
            e = Math.floor(e),
            c += b.charAt(e);
        return c
    }
""")


class Copartner():
    name = "音乐合伙人"

    def __init__(self, check_item):
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
        self.i = get_i.call('a', 16)  # 随机生成长度为16的字符串
        self.iv = "0102030405060708"  # 偏移量
        self.headers = {
            "Accept": "application/json, text/javascript",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "http://mp.music.163.com",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 CloudMusic/0.1.1 NeteaseMusic/8.8.01"
        }
        self.musicScoreRandomRange = [2,4]
        self.waitRange = [15,20]
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
        self.check_item = check_item

    def get_enc_sec_key(self):
        return rsa_encrypt(self.i, self.b, self.c)

    def get_params(self, data):
        enc_text = str(data)
        return aes_encrypt(aes_encrypt(enc_text, self.g, self.iv), self.i, self.iv)

    def wait_listen(self):
        wait = random.randint(self.waitRange[0], self.waitRange[1])
        sleep(wait)

    def sign(self, session, music_data, msg):
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
                data = {
                    "params": self.get_params({
                        "taskId": task_id,
                        "workId": _work['id'],
                        "score": score,
                        "tags": tags,
                        "customTags": "[]",
                        "comment": "",
                        "syncYunCircle": "true",
                        "csrf_token": self.csrf
                    }).replace("\n", ""),
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
                return;
        except Exception as e:
            print(f"歌曲 {work['name']} 上报失败,原因{str(e)}")
            return;

        # reportListen
        score = self.get_random_score()
        tags = self.get_random_tags(score)
        data = {
            "params": self.get_params({
                "taskId": task_id,
                "workId": work['id'],
                "score": score,
                "tags": tags,
                "customTags": "[]",
                "comment": "",
                "syncYunCircle": "true",
                "extraResource": "true",
                "csrf_token": self.csrf
            }).replace("\n", ""),
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
        return random.randint(self.musicScoreRandomRange[0], self.musicScoreRandomRange[1])

    def get_random_tags(self, score):
        num_to_select = random.randint(1, 3)
        current_score_tags = self.musicTags[score - 1]
        selected_values = random.sample(current_score_tags, num_to_select)
        return ','.join(selected_values)

    def get_extra_music(self, session):
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
            extra_count = 7 - len(computed_music)
            return [] if extra_count < 0 else undone_music[:extra_count], len(computed_music)
        return [], "登录信息异常"

    def login_info(self, session):
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
        session = requests.session()
        cookie = self.check_item.get("cookie")
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


if __name__ == "__main__":
    with open("/ql/config/sg_check.json", "r", encoding="utf-8") as f:
        all_data = json.loads(f.read())
        _check_item = all_data.get("MUSIC_COPARTNER", [])
        res = ""
        for index, item in enumerate(_check_item):
            res = f'{res}账号{index + 1}：\n{Copartner(item).main()}\n'
        print(res)
        send('网易音乐合伙人', res)
