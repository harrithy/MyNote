# GMS（Google Mobile Services，谷歌移动服务）

GMS 是 Google 提供的一系列核心应用程序与API的集合，运行在 Android 系统之上。

## 1. 组成部分

- **Google Play 服务**：：运行在后台的核心软件环境，为定位、登录、推送通知（如 GCM/FCM）、安全验证、广告和各种 API 提供支持
- **Google 服务框架 GSF（Google Services Framework）**：运行在底层的系统服务，负责协助其他谷歌应用与谷歌服务器进行通信、身份验证和数据同步。
- **Play 商店**：应用下载、更新 Play 服务。

## 2. 为什么 FCM 必须依赖 GMS

FCM 在 Android 设备端的接收端和服务维持程序，并不是内置在应用 SDK 或开源 Android 系统（AOSP）中的，而是作为 GMS 核心系统服务的一部分运行的。

- 系统长连接：FCM 在设备后台只需要维持一条由谷歌服务器`mtalk.google.com`到手机的系统级 TCP 长连接。
- 长连接的维护：由 Google Play 服务统一维护。如果没有 GMS，设备上就没有合法的系统进程去与谷歌的 FCM 服务器握手并保持在线。
- 推送消息的分发：当 FCM 服务器向设备发送消息时，GMS 会接收这些消息并通过广播的方式唤醒对应的应用程序。

## 3. 为什么 GMS 能实现长连接而不被系统杀掉

- 对于港版，国际版的手机，GMS 预装在 /system/priv-app 或 /product/priv-app 等系统分区，厂商通过 privapp 权限白名单授予它特权权限
- GMS 授权与兼容性认证要求厂商保证 Google 应用正常可用——所以国际版 ROM 从出厂起就不把它当普通第三方应用清理。

简单来说手机把 GMS 当作系统服务，Android 的省电机制从设计上就不针对它，不会限制它的后台执行、后台启动、网络访问等能力。即使在 Doze、App Standby、后台执行限制和厂商省电策略下，GMS 也能长期持有 socket 并维持长连接。

## 4. 判断设备能不能用 FCM

1. 设置 → 应用 → 显示系统应用 → 搜「Google Play 服务」，看是否存在、未停用、版本不太旧；
2. 拨号 `*#*#426#*#*` → FCM Diagnostics，状态 `Connected` 说明 GMS 在跑且连着 FCM；
3. 注意：**有 GMS ≠ FCM 可用**，还要网络可达、通知权限（Android 13+ `POST_NOTIFICATIONS`）、省电策略放行、包名与 `google-services.json` 一致、App 内拿到本机 Token。
