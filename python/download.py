#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TVBox 伪装下载器（多文件版·带网速监控）
所有配置由环境变量传入，不在脚本内写死。
"""
import os
import sys
import time
import zipfile
import requests

# ================== 配置区（全部从环境变量读取） ==================
# JOBS 格式: "文件名|下载地址;文件名|下载地址;..."
# 例如: "tvboxX4.zip|https://xxx/a.zip;tvboxqq.zip|https://xxx/b.zip"
JOBS = os.getenv("JOBS", "").strip()
SAVE_DIR = os.getenv("SAVE_DIR", "zip").strip()
EXTRACT = os.getenv("EXTRACT", "").lower() in ("1", "true", "yes")
# ==================================================================


def parse_jobs(jobs_str):
    """把 '文件名|地址;文件名|地址' 解析成 [(filename, url), ...]"""
    jobs = []
    if not jobs_str:
        return jobs
    for item in jobs_str.split(";"):
        item = item.strip()
        if not item:
            continue
        if "|" not in item:
            print(f"  ⚠️ 跳过无效配置: {item}")
            continue
        filename, url = item.split("|", 1)
        filename = filename.strip()
        url = url.strip()
        if not filename or not url:
            print(f"  ⚠️ 跳过无效配置: {item}")
            continue
        jobs.append((filename, url))
    return jobs


def download_file(url, save_path, extract=False):
    headers = {
        "User-Agent": "okhttp/3.15",
        "Accept-Encoding": "gzip",
    }

    save_dir = os.path.dirname(save_path)
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)

    print("=" * 60)
    print("  TVBox 伪装下载器（多文件版）")
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
        return False


def main():
    jobs = parse_jobs(JOBS)
    if not jobs:
        print("❌ 未配置任何下载任务 (JOBS 为空)")
        sys.exit(1)

    print(f"📋 共 {len(jobs)} 个任务\n")

    ok, fail = 0, 0
    for idx, (filename, url) in enumerate(jobs, 1):
        print(f"\n{'#' * 60}")
        print(f"# 任务 {idx}/{len(jobs)}: {filename}")
        print(f"{'#' * 60}")
        save_path = os.path.join(SAVE_DIR, filename)
        if download_file(url, save_path, EXTRACT):
            ok += 1
        else:
            fail += 1

    print(f"\n{'=' * 60}")
    print(f"  汇总: 成功 {ok} / 失败 {fail} / 共 {len(jobs)}")
    print(f"{'=' * 60}")

    if fail > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()