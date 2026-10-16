# Electron

## 简介

简单来说，Electron = Chromium + Node.js + Native APIS.

- Chromium: 提供了浏览器的渲染引擎，负责显示界面
- Node.js: 提供了后端能力，可以访问文件系统、网络等
- Native APIS: 提供了操作系统级别的能力，比如菜单、通知、剪贴板等

### 核心概念

- Main 进程：Election 的入口，负责创建 BrowserWindow、管理应用生命周期与原生API。运行单实例。
- Renderer 进程：每个 BrowserWindow 对应一个 renderer，运行网页（Chromium），不直接访问 Node（可通过 preload 暴露受限 API）。
- Preload 脚本 & contextIsolation：推荐用 preload 在 renderer 中注入受限 API，开启 contextIsolation 提高安全性。
- IPC（ipcMain / ipcRenderer / contextBridge）：主、渲染进程通信机制。
- 打包工具：Electron Builder / Electron Forge / electron-packager 等，用于生成安装包与自动更新。
- Auto-updater：实现应用自动升级（需服务端/发布配置）。
