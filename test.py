from cryptography.fernet import Fernet

# 只需執行一次來生成密鑰
key = Fernet.generate_key()
print(key.decode())