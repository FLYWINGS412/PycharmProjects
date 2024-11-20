import requests
import json
import time
import hmac
import hashlib
import base64


def read_wskey_file(filepath):
    """读取 wskey.txt 文件内容"""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            wskey_list = [line.strip() for line in file if line.strip()]
        return wskey_list
    except FileNotFoundError:
        print(f"文件 {filepath} 不存在，请检查！")
        return []


def genJDUA():
    """生成京东用户代理"""
    return (
        "jdapp;android;11.1.6;;;appBuild/98230;ef/1;"
        "ep/;Mozilla/5.0 (Linux; Android 13; Build/TP1A.220905.004; wv)"
        " AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/102.0.5005.125 Mobile Safari/537.36"
    )


def genParams():
    """生成请求参数，包含签名生成"""
    st = int(time.time() * 1000)
    sv = "121"
    functionId = "genToken"
    clientVersion = "11.1.6"
    client = "android"
    build = "98230"
    partner = "google"
    sdkVersion = "32"
    lang = "zh_CN"

    # 拼接用于签名的原始参数
    raw_string = f"functionId={functionId}&client={client}&clientVersion={clientVersion}&build={build}&partner={partner}&sdkVersion={sdkVersion}&lang={lang}&st={st}&sv={sv}"
    sign = generate_sign(raw_string)

    return {
        'functionId': functionId,
        'clientVersion': clientVersion,
        'build': build,
        'client': client,
        'partner': partner,
        'sdkVersion': sdkVersion,
        'lang': lang,
        'st': st,
        'sv': sv,
        'sign': sign
    }


def generate_sign(data):
    """生成签名（示例使用 HMAC-SHA256）"""
    secret = b"your_secret_key_here"  # 替换为真实的密钥
    hash_obj = hmac.new(secret, data.encode('utf-8'), hashlib.sha256)
    return base64.b64encode(hash_obj.digest()).decode()


def get_token(wskey):
    """通过 wskey 获取 token"""
    url = "https://api.m.jd.com/client.action"
    headers = {
        "cookie": wskey,
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": genJDUA(),
    }
    params = genParams()
    data = 'body=%7B%22to%22%3A%22https%253a%252f%252fplogin.m.jd.com%252fjd-mlogin%252fstatic%252fhtml%252fappjmp_blank.html%22%7D&'

    try:
        response = requests.post(url, headers=headers, params=params, data=data, timeout=10)
        print(f"请求 token URL: {response.url}")
        print(f"请求 headers: {headers}")
        print(f"请求 body: {data}")
        response.raise_for_status()
        result = response.json()
        print(f"响应结果: {result}")
        return result.get("tokenKey")
    except requests.exceptions.RequestException as e:
        print(f"获取 token 失败：{e}")
        return None


def convert_to_cookie(wskey, token_key):
    """通过 token_key 转换为浏览器可用的 cookie"""
    url = "https://un.m.jd.com/cgi-bin/app/appjmp"
    params = {
        "tokenKey": token_key,
        "to": "https://plogin.m.jd.com/jd-mlogin/static/html/appjmp_blank.html"
    }
    headers = {
        "user-agent": genJDUA(),
    }

    try:
        response = requests.get(url, headers=headers, params=params, allow_redirects=False, timeout=10)
        response.raise_for_status()
        cookies = response.cookies.get_dict()
        if "pt_key" in cookies and "pt_pin" in cookies:
            return f"pt_key={cookies['pt_key']}; pt_pin={cookies['pt_pin']};"
        else:
            print(f"未能从响应中提取有效 cookie: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"转换失败：{e}")
        return None


def main():
    wskey_file = "wskey.txt"
    output_file = "cookies.txt"

    wskeys = read_wskey_file(wskey_file)
    if not wskeys:
        print("未找到 wskey，退出。")
        return

    cookies = []
    for wskey in wskeys:
        print(f"正在处理 wskey: {wskey}")
        token_key = get_token(wskey)
        if token_key:
            cookie = convert_to_cookie(wskey, token_key)
            if cookie:
                print(f"转换成功：{cookie}")
                cookies.append(cookie)
            else:
                print(f"转换失败：{wskey}")
        else:
            print(f"获取 token 失败：{wskey}")

    if cookies:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write("\n".join(cookies))
        print(f"所有转换的 cookie 已保存到 {output_file}")
    else:
        print("未生成任何有效 cookie")


if __name__ == "__main__":
    main()
