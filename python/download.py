#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TVBox 伪装下载器（带网速监控）
配置集中在「用户配置区」，无需外部传参。
"""
import os
import sys
import time
import zipfile
import requests

# ================== 用户配置区（改这里就行） ==================
DOWNLOAD_URL = "https://mpimg.cn/down.php/fe15c27aeb01b77b9f6708a1dac89fd0"
SAVE_DIR = "zip"          # 保存目录（仓库根下的 zip/）
FILENAME = "tvboxqq.zip"  # 文件名
# FILENAME = time.strftime("tvbox_%Y%m%d_%H%M%S.zip")  # 按时间命名就开这个
EXTRACT = os.getenv("EXTRACT", "").lower() in ("1", "true", "yes")
# ============================================================
SAVE_PATH = os.path.join(SAVE_DIR, FILENAME)


def download_file(url, save_path, extract=False):
    headers = {
        "User-Agent": "okhttp/3.15",
        "Accept-Encoding": "gzip",
    }

    save_dir = os.path.dirname(save_path)
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)

    print("=" * 60)
    print("  TVBox 伪装下载器（带网速监控）")
    print("=" * 60)
    print(f"  链接: {url}")
    print(f"  保存: {save_path}")
    print("=" * 60)

    try:
        response = requests.get(url, headers=headers, stream=True, timeout=60)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0
        start_time = time.time()

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                f.write(chunk)
                downloaded += len(chunk)

                if total_size > 0:
                    percent = downloaded / total_size * 100
                    done = int(30 * downloaded / total_size)
                    elapsed = time.time() - start_time
                    speed = downloaded / elapsed / 1024 / 1024 if elapsed > 0 else 0
                    sys.stdout.write(
                        f"\r  [{'█' * done}{'░' * (30 - done)}] "
                        f"{percent:.1f}% | {downloaded/1024/1024:.1f}MB/{total_size/1024/1024:.1f}MB | "
                        f"{speed:.1f}MB/s | 耗时{int(elapsed)}s"
                    )
                    sys.stdout.flush()

        elapsed = time.time() - start_time
        print(f"\n\n  ✅ 完成!")
        print(f"     大小: {downloaded/1024/1024:.1f}MB")
        print(f"     均速: {downloaded/elapsed/1024/1024:.1f}MB/s")
        print(f"     耗时: {elapsed:.1f}s")
        print(f"     路径: {os.path.abspath(save_path)}")

        if extract and save_path.endswith(".zip"):
            with zipfile.ZipFile(save_path, "r") as zip_ref:
                zip_ref.extractall(save_dir)
            print(f"  📦 已解压到: {save_dir}")

        print("🎉 下载成功！")
        return True
    except Exception as e:
        print(f"\n  ❌ 下载失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    download_file(DOWNLOAD_URL, SAVE_PATH, EXTRACT)
