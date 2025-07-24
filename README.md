# ZidooWatcher

一个简单易用的Zidoo播放器监控工具，让您的观影体验更智能。

## 🎬 这个软件做什么？

**ZidooWatcher** 会实时监控您的Zidoo播放器，当您开始播放视频时：

1. **自动发送通知** - 告诉您的其他设备有新视频开始播放
2. **路径转换** - 将Zidoo路径转换外部设备可识别的路径

## ✨ 主要功能

- 🔍 **实时监控** - 24小时监控Zidoo播放器状态
- 📱 **网页控制** - 简单的网页界面，手机电脑都能用
- 🗂️ **路径管理** - 灵活的文件路径映射规则
- 📊 **日志查看** - 实时查看运行日志，了解系统状态

## 🚀 快速开始

### 方法一：Docker运行

   ```bash
   docker run -d \
     --name zidoo-watcher \
     -p 7502:7502 \
     -v ./config:/config \
     --restart unless-stopped \
     narapeka/zidoowatcher:latest
   ```

### 方法二：使用 Docker Compose

   ```yaml
   version: '3.8'
   services:
     zidoo-watcher:
       image: narapeka/zidoowatcher:latest
       container_name: zidoo-watcher
       ports:
         - "7502:7502"
       volumes:
         - ./config:/config
       environment:
         - TZ=Asia/Shanghai
       restart: unless-stopped
   ```

## ⚙️ 基本配置

### 第一次使用

1. 打开网页界面 `http://<ip>:7502`
2. 点击"配置"标签
3. 填写您的Zidoo播放器IP地址
4. 设置通知接收地址
5. 添加文件路径映射规则
6. 点击"启动服务"开始监控

### 配置说明

**请详细阅读应用内帮助页面**

**Zidoo设置**：
- IP地址：您的Zidoo播放器在局域网中的IP

**通知设置**：
- 接收地址：当有新视频播放时，通知发送到这个地址。
- 超时时间：通知发送的等待时间
- 建议搭配：`https://github.com/narapeka/BlurayPoster`，可实现拉起蓝光机播放。

**路径映射**：
- 本地路径：Zidoo播放事件产生文件路径
- 目标路径：转换后的路径
- 可以添加多个映射规则，支持启用/禁用

## 🔧 常见问题

**Q: 找不到Zidoo播放器怎么办？**
A: 检查IP地址是否正确，确保Zidoo和服务器在同一局域网内。

**Q: 通知发送失败怎么办？**
A: 检查通知接收地址是否正确，网络是否畅通。

**Q: 路径映射不生效？**
A: 确保路径映射规则已启用，路径格式正确匹配。

**Q: 服务无法启动？**
A: 查看日志页面的错误信息，通常是配置问题。

## 📞 技术支持

- 在网页界面的"日志"页面查看详细运行信息
- 配置文件保存在 `config/config.yaml`
- 日志文件保存在 `config/logs/` 目录

## 🐳 Docker 镜像

本软件已发布到 Docker Hub：**`narapeka/zidoowatcher`**

- **最新版本**：`narapeka/zidoowatcher:latest`
- **自动更新**：镜像会定期更新，建议使用 `latest` 标签
- **多架构支持**：支持 AMD64 和 ARM64 架构
