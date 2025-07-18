import os
import asyncio
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import aiofiles


async def decrypt_ts_file(encrypted_file_path, decrypted_file_path, key, iv):
    try:
        # 异步读取加密的 TS 文件内容
        async with aiofiles.open(encrypted_file_path, 'rb') as encrypted_file:
            encrypted_data = await encrypted_file.read()

        # 创建 AES 解密器对象，使用 CBC 模式
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # 解密密文
        decrypted_data = cipher.decrypt(encrypted_data)

        # 去除填充
        unpadded_data = unpad(decrypted_data, AES.block_size)

        # 异步写入解密后的内容到新文件
        async with aiofiles.open(decrypted_file_path, 'wb') as decrypted_file:
            await decrypted_file.write(unpadded_data)

        print(f"解密成功: {encrypted_file_path} -> {decrypted_file_path}")
    except Exception as e:
        print(f"解密失败: {encrypted_file_path}, 错误信息: {e}")


async def decrypt_all_ts_files(input_folder, output_folder, key, iv):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 收集所有 TS 文件的解密任务
    tasks = []
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.ts'):
                # 构建加密文件的完整路径
                encrypted_file_path = os.path.join(root, file)
                # 构建解密文件的完整路径
                decrypted_file_path = os.path.join(output_folder, file)
                # 创建解密任务
                task = decrypt_ts_file(encrypted_file_path, decrypted_file_path, key, iv)
                tasks.append(task)

    # 并发执行所有解密任务
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # 包含加密 TS 文件的文件夹路径
    input_folder = './film'
    # 保存解密后 TS 文件的文件夹路径
    output_folder = './downloads'
    # 加密密钥，需要替换为实际的密钥
    #读取密钥获取密钥的值
    with open('./film/enc.key', 'rb') as key_file:
        key = key_file.read()
    # key = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10'
    # 初始向量，需要替换为实际的 IV  m3u8文件带的IV
    iv_hex = "0x00000000000000000000000000000000"
    # 这个必须解析一下才能用
    iv = bytes.fromhex(iv_hex[2:])

    asyncio.run(decrypt_all_ts_files(input_folder, output_folder, key, iv))
    