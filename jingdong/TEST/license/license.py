import os
import rsa
from datetime import datetime
from cryptography.fernet import Fernet

# 检查是否已有密钥文件
if not os.path.exists("public_key.pem") or not os.path.exists("private_key.pem"):
    # 如果没有，生成新的 RSA 密钥对，并保存到文件
    (public_key, private_key) = rsa.newkeys(512)
    with open("public_key.pem", "wb") as pub_file:
        pub_file.write(public_key.save_pkcs1())
    with open("private_key.pem", "wb") as priv_file:
        priv_file.write(private_key.save_pkcs1())
    print("新密钥对已生成并保存为 public_key.pem 和 private_key.pem")
else:
    # 如果已有密钥，直接从文件加载
    with open("public_key.pem", "rb") as pub_file:
        public_key = rsa.PublicKey.load_pkcs1(pub_file.read())
    with open("private_key.pem", "rb") as priv_file:
        private_key = rsa.PrivateKey.load_pkcs1(priv_file.read())
    print("已加载现有的密钥对")

# 设置授权日期
expiration_date_str = "2024-11-11"

# 使用对称加密生成加密密钥（Fernet密钥）并加密授权日期
fernet_key = Fernet.generate_key()
cipher_suite = Fernet(fernet_key)
encrypted_date = cipher_suite.encrypt(expiration_date_str.encode())

# 使用私钥签名加密的授权日期
signature = rsa.sign(encrypted_date, private_key, 'SHA-1')

# 创建 `license_key.lic` 文件
with open("license_key.lic", "wb") as f:
    f.write(fernet_key + b"\n")  # 写入 Fernet 加密密钥
    f.write(encrypted_date + b"\n")  # 写入加密的授权日期
    f.write(signature)  # 写入签名

print("已生成带授权日期的 license_key.lic 文件")
