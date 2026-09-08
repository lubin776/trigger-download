# Vercel 方案部署说明

## 整体架构
```
GitHub Actions 触发
  → python/download.py 下载文件到 zip/tvboxqq.zip
  → 发布到 GitHub Release (tag: latest)
  → Vercel rewrites 把 d.12yue.de5.net/tvboxqq.zip 透明转发到 GitHub Release
  → 用户 / TVBox 只看到你的域名
```

## 一、部署 Vercel 站点
1. 把 `vercel-app/` 下的 `vercel.json` + `index.html` 放到仓库根目录
   （Vercel 要求 `vercel.json` 在项目根，别放进子目录）
2. 打开 vercel.com，用 GitHub 登录 → Import 该仓库 → Deploy
3. Settings → Domains → 添加 `d.12yue.de5.net`
4. Cloudflare DNS 里把 `d.12yue.de5.net` 的 CNAME 指向 Vercel 提供的地址

## 二、测试
```bash
# 应该直接开始下载，响应头里看不到 github
curl -I https://d.12yue.de5.net/tvboxqq.zip
```

## 三、工作流
每次手动触发 `触发下载` workflow：
- 脚本从 `DOWNLOAD_URL` 下载到 `zip/tvboxqq.zip`
- 自动覆盖 Release 的 `latest` tag
- Vercel rewrite 永远指向 `latest`，所以用户拿到的总是最新版

## 四、修改链接/文件名
只改 `python/download.py` 顶部的「用户配置区」：
- `DOWNLOAD_URL`：下载源
- `FILENAME`：保存文件名（需与 vercel.json 里的 source 对应）
- `EXTRACT`：是否解压
