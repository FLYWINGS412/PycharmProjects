import time
import requests
import urllib.parse

# 用户信息 API 地址
user_info_url = "https://me-api.jd.com/user_new/info/GetJDUserInfoUnion"
# 验证地址
verify_url = "https://plogin.m.jd.com/cgi-bin/ml/islogin"

# 从 cookies.txt 文件中读取 Cookie 列表，并移除每个 Cookie 中的空格
def load_cookies_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

# 将验证结果写回 result.txt 文件
def write_cookies_to_file(file_path, cookies_with_results):
    with open(file_path, 'w', encoding='utf-8') as f:
        for cookie in cookies_with_results:
            f.write(cookie + "\n")

def extract_pin_key(cookie):
    pt_pin = None
    pt_key = None
    for item in cookie.split(';'):
        if 'pt_pin=' in item:
            pt_pin = item.split('=')[1].strip()
        if 'pt_key=' in item:
            pt_key = item.split('=')[1].strip()
    return pt_pin, pt_key

def is_already_validated(cookie):
    # 如果 cookie 已经包含验证结果"（有效）"、"（无效）"，则跳过验证
    return "（有效）" in cookie or "（无效）" in cookie or "（有效，但" in cookie

def validate_cookie(cookie, retry_count=3):
    # 检查是否已经验证过，避免重复验证
    if is_already_validated(cookie):
        return cookie

    pt_pin, pt_key = extract_pin_key(cookie)
    if not pt_pin or not pt_key:
        return f"{cookie}（无效，缺少 pt_pin 或 pt_key）"

    # URL 编码 cookie 以避免编码错误
    encoded_cookie = urllib.parse.quote(cookie, safe='=;')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
        "Cookie": encoded_cookie,
        "Referer": "https://my.m.jd.com",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    for attempt in range(retry_count):
        try:
            # 第一步：验证 pt_key 是否有效
            response = requests.get(verify_url, headers=headers, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code == 200:
                data = response.json()
                if data.get('islogin') != "1":
                    return f"{cookie}（无效）"
            else:
                return f"{cookie}（请求失败，状态码: {response.status_code}）"

            # 第二步：获取用户信息并验证 pt_pin 是否匹配
            response = requests.get(user_info_url, headers=headers)
            response.encoding = 'utf-8'

            if response.status_code == 200:
                data = response.json()
                # 检查返回的 data 是否符合预期
                if 'data' in data and 'userInfo' in data['data']:
                    cur_pin = data['data']['userInfo']['baseInfo'].get('curPin', '')
                    if cur_pin == pt_pin:
                        return f"{cookie}（有效）"
                    else:
                        return f"{cookie}（有效，但 pt_pin 不匹配）"
                else:
                    print(f"调试信息: 返回的原始数据 {data}, 处理的 Cookie: {cookie}")
                    return f"{cookie}（返回的数据结构不符合预期）"
            else:
                return f"{cookie}（请求失败，状态码: {response.status_code}）"

        except requests.exceptions.RequestException as e:
            return f"{cookie}（请求失败: {e}）"

    # 如果多次重试后依然失败
    return f"{cookie}（请求失败，状态码: 503，多次尝试后放弃）"

# 从文件中加载 Cookie 列表，并移除空格
cookies = load_cookies_from_file('cookies.txt')

cookies_with_results = []

# 只对尚未验证为 "（有效）" 或 "（无效）" 的 Cookie 进行验证
for cookie in cookies:
    result = validate_cookie(cookie)
    cookies_with_results.append(result)
    print(result)  # 输出每条 Cookie 的验证结果到控制台
    # time.sleep(5)  # 每条 Cookie 验证后等待 30 秒

# 将验证结果写回 result.txt 文件
write_cookies_to_file('result.txt', cookies_with_results)
