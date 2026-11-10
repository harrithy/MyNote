# Google FCM 接入总结：appdemo

更新日期：2026-11-06。

本文依据 `D:\yin\appdemo` 项目内的 Android 客户端、Node.js 示例服务和电脑发送页整理，按“前期准备 → 是什么 → 为什么 → 怎么做 → 总结”说明前端与后端的职责和接入过程。

整体链路：**Android App 获取 FCM Token → 可选上传本项目后端 → 电脑发送页提交消息 → Node.js 调用 Firebase Admin SDK → FCM 投递 → 手机接收**。

## 一、前期准备

### 1. 前端准备

| 准备项 | 本项目中的要求 |
| --- | --- |
| 开发工具 | HBuilderX，项目使用 uni-app、Vue 3 |
| 运行设备 | 有正常 Google Play 服务、能连接 FCM 的 Android 手机或模拟器 |
| Firebase 应用 | 注册 Android 应用，包名与实际安装包一致 |
| Android 包名 | `com.example.appdemo`，见根目录 AndroidManifest.xml |
| 客户端配置 | 对应应用的 google-services.json |
| 配置放置位置 | `D:\yin\appdemo\nativeResources\android\google-services.json` |
| 原生插件 | 项目已包含 `uni_modules/Jairo-FCM` |
| 通知权限 | manifest.json 已声明 POST_NOTIFICATIONS，targetSdkVersion 为 33；运行时还要检查、申请权限 |
| 调试安装包 | 使用包含 Firebase 原生依赖和本项目配置的自定义基座或正式 APK |

项目的 [插件构建配置](/D:/yin/appdemo/uni_modules/Jairo-FCM/utssdk/app-android/config.json) 声明了 `firebase-messaging:24.0.1`，ABI 为 `armeabi-v7a`、`arm64-v8a`；模拟器需要与这些配置兼容。H5 可以预览页面，但不能验证原生 FCM 推送。

### 2. 后端准备

| 准备项 | 本项目中的要求 |
| --- | --- |
| Node.js | 22 或更高版本，见 package.json |
| 依赖 | firebase-admin，项目锁定版本为 14.5.0 |
| Firebase 项目 | 与 App 的客户端配置对应 |
| 发送能力 | 按项目 README 确认 Firebase Cloud Messaging API（HTTP v1）已启用 |
| 服务端凭据 | 服务账号 JSON，由后端通过 GOOGLE_APPLICATION_CREDENTIALS 读取 |
| 本地配置 | `D:\yin\appdemo\server\.env` |
| 请求鉴权 | 本 Demo 自定义的 DEMO_API_KEY；FCM 本身不要求，但当前代码要求配置，手机同步和电脑发送使用相同的值 |
| 端口 | 当前本机配置为 3001；源码和模板默认端口为 3000 |
| 网络 | 后端能访问 Google 认证服务及 FCM；手机同步时能访问电脑后端 |

### 3. 需要准备的两个 JSON 文件

**本项目需要分别准备客户端配置和后端凭据。两个文件都来自对应的 Firebase 项目，但不是都放进 App 工程。**

| 文件 | 如何获取 | 本项目的放置位置 | 使用方与作用 |
| --- | --- | --- | --- |
| `google-services.json` | 在 Firebase 中注册 Android 应用后，下载该应用的配置文件 | `D:\yin\appdemo\nativeResources\android\google-services.json` | Android 构建使用，使 App 连接到对应的 Firebase 项目 |
| 服务账号私钥 JSON，本例命名为 `firebase-admin.json` | Firebase 项目设置 → 服务账号 → Firebase Admin SDK → 生成新的私钥 | `D:\app-secrets\firebase-admin.json`，保存在 App 项目外 | Node.js 后端通过 Admin SDK 向 Google 认证并发送推送 |

后端在 `server/.env` 中配置 `GOOGLE_APPLICATION_CREDENTIALS=D:/app-secrets/firebase-admin.json`，让它指向第二个文件。服务账号文件可以使用其他名称或目录，只要配置路径与实际文件一致。

**第二个文件含有私钥，不能放进 APK、static 或电脑发送网页，也不能用第一个 JSON 代替。**

Demo API Key 则是另外生成的随机字符串，写在 `.env` 的 `DEMO_API_KEY` 中，**不是第三个 JSON，也不是上述两个 JSON 的替代品**。获取 Token、加载 Firebase 配置与校验本项目接口密钥，是不同的步骤。

配置来源：[package.json](/D:/yin/appdemo/package.json)、[server/.env.example](/D:/yin/appdemo/server/.env.example)、[server/index.js](/D:/yin/appdemo/server/index.js)。

## 二、是什么

### 1. 前端是什么

本项目的前端包括 Android App 和电脑浏览器中的发送页。

**Android App 是接收端**：初始化 FCM、获取 Token、申请通知权限、登记设备、读取消息缓存。**电脑发送页是操作入口**：填写接收设备和消息，再请求 Node.js 后端。

| 文件 | 作用 |
| --- | --- |
| [App.vue](/D:/yin/appdemo/App.vue) | 监听 App 进入前台、退到后台 |
| [pages/index/index.vue](/D:/yin/appdemo/pages/index/index.vue) | 展示 Token、权限、服务器配置、设备 ID、消息和日志 |
| [common/fcm-demo.js](/D:/yin/appdemo/common/fcm-demo.js) | 管理页面状态、初始化流程、设备同步和前台定时读取 |
| [common/fcm.js](/D:/yin/appdemo/common/fcm.js) | 将 JS 调用映射到 UTS 插件接口，并限制运行平台 |
| [common/fcm-bridge.js](/D:/yin/appdemo/common/fcm-bridge.js) | 将 success/fail 回调封装成 Promise，处理失败、超时和重复回调 |
| [common/fcm-api.js](/D:/yin/appdemo/common/fcm-api.js) | 解析后端响应，阻止把 HTTP 错误或非 JSON 响应当作成功 |
| [UTS 原生入口](/D:/yin/appdemo/uni_modules/Jairo-FCM/utssdk/app-android/index.uts) | 调用 Firebase Android SDK，获取 Token、申请权限、读取缓存 |
| [hybrid.kt](/D:/yin/appdemo/uni_modules/Jairo-FCM/utssdk/app-android/hybrid.kt) | 接收原生消息、处理 Token 更新，保存到手机本地缓存 |
| [server/public/index.html](/D:/yin/appdemo/server/public/index.html) | 电脑上的推送发送页，由本项目 Node.js 服务提供 |

### 2. 后端是什么

本项目自带的后端是 `server` 目录中的 Node.js HTTP 服务，负责设备登记、请求校验和调用 Firebase Admin SDK。

| 文件 | 作用 |
| --- | --- |
| [server/index.js](/D:/yin/appdemo/server/index.js) | 读取环境变量、启动监听、初始化 Admin SDK 并发送消息 |
| [server/app.js](/D:/yin/appdemo/server/app.js) | 定义 HTTP 接口、鉴权、设备内存记录、消息构造及错误映射 |
| [server/public/index.html](/D:/yin/appdemo/server/public/index.html) | 提供发送表单，调用同源 /api/send |

| 接口 | 鉴权 | 作用 |
| --- | --- | --- |
| `GET /` | 不需要 | 返回电脑发送页 |
| `GET /api/health` | 不需要 | 返回项目 ID、项目和 Demo Key 是否填写；不检查真实 Google 凭据是否可用 |
| `POST /api/devices` | X-Demo-Key | 保存或更新 deviceId 对应的 Token |
| `POST /api/send` | X-Demo-Key | 接收 Token 或已登记的 deviceId，调用 FCM 发送 |

设备记录放在 `Map` 中，最多保留 100 个设备 ID，重启服务后会丢失。本项目的这套 Node.js 演示服务不需要安装数据库。

## 三、为什么这样做

### 1. 前端为什么需要这些处理

**为什么需要原生插件？**

页面 JS 通过 UTS 插件调用 Android Firebase SDK。App 退到后台后会停止本项目的 JS 定时器，接收推送由原生 SDK 与 Google 服务处理。

**为什么需要 Token 和 deviceId？**

Token 用于 FCM 定位 App 的注册实例；deviceId 是本项目在手机本地保存的安装级 ID，用来更新后端登记记录。两者用途不同，Token 变化时可以继续用原 deviceId 覆盖旧绑定。

**为什么要处理通知权限？**

本项目在初始化和回到前台时检查权限。原生权限函数发起弹窗后会立即返回当时的授权状态，因此一次返回 false 不代表用户最终拒绝；允许后可再次点击“申请通知权限”核验。

**为什么要自定义基座或重新打包？**

Firebase 是原生依赖。普通页面热更新不能替换安装包里的原生 SDK 和配置；项目提示标准基座无法验证当前 Firebase 集成。修改原生依赖、权限或打包配置后，需要重新制作相应安装包。

**为什么每 3 秒读一次消息？**

`common/fcm-demo.js` 每 3 秒读取的是**手机原生插件的本地消息缓存**，并非轮询后端。App 隐藏时停止定时器，返回前台后再读取。

### 2. 后端为什么需要这些处理

**为什么由后端发送？**

发送需要服务账号身份。服务端凭据由 Node.js 的 `applicationDefault()` 读取，电脑网页和 App 只提交业务参数，不能拿到服务账号私钥。

**为什么需要 Demo API Key？**

**Demo API Key 是本项目自行设置的测试接口密钥，不是 Google / Firebase 颁发的，也不是从 FCM Token 推导出来的。**通常由开发者生成随机字符串，写入 `server/.env` 的 `DEMO_API_KEY`，App 和电脑发送页填写同一个值。当前服务不会在启动时自动生成这个值。

`/api/devices` 和 `/api/send` 校验请求头 `X-Demo-Key`，用来判断调用者是否持有这个测试密钥。它与后端访问 Google 时使用的身份凭据是两回事：

| 内容 | 从哪里来 | 用途 | 是否能省略 |
| --- | --- | --- | --- |
| Demo API Key | 开发者自行生成，写入 server/.env | 保护本项目的设备登记和发送接口 | 不是 FCM 必需项，可以修改项目移除或替换鉴权；当前代码不能直接留空 |
| 服务账号凭据 | Firebase 项目的服务账号配置 | 后端通过 Admin SDK 向 Google 认证并发送 | 去掉 Demo Key 不代表可以去掉这部分身份凭据 |
| FCM Token | App 通过原生 Firebase SDK 获取 | 指定接收推送的 App 注册实例 | 当前单设备发送需要有效 Token，或用 deviceId 查出已登记的 Token |

**能不能不用 Demo API Key？可以，但需要同步修改前后端。**当前只删除 `.env` 中的值或在页面留空，会遇到启动检查、前端校验或接口错误，不能按本教程直接完成同步和发送。

如果决定移除这层测试鉴权，需要一起调整以下位置；这里只说明改动范围，项目代码仍保持现有鉴权：

| 位置 | 需要同步调整的逻辑 |
| --- | --- |
| [server/index.js](/D:/yin/appdemo/server/index.js) | 非本机监听时，要求 Demo Key 至少 16 位的启动检查 |
| [server/app.js](/D:/yin/appdemo/server/app.js) | 未配置 Key 返回 503、Key 不匹配返回 401 的接口校验 |
| [common/fcm-demo.js](/D:/yin/appdemo/common/fcm-demo.js) | requestApi 的 Key 必填检查及请求头；refreshToken 中依赖 serverUrl 和 apiKey 才自动同步的条件 |
| [server/public/index.html](/D:/yin/appdemo/server/public/index.html) | Key 输入框的 required 必填限制及发送 X-Demo-Key 的逻辑 |

相应的鉴权测试也要与新的接口规则一致。仅本机临时演示时可以选择移除；对外提供服务时，应保留有效的接口鉴权，也可以改成正式用户身份认证。

**以下操作步骤按项目当前实现保留 Demo API Key。**已有本地配置时，直接复制 `server/.env` 中 `DEMO_API_KEY=` 后面的值使用，不需要重新生成。

**为什么设备登记是可选的？**

`/api/send` 既支持直接传 Token，也支持根据 deviceId 查询内存记录。第一次测试可以直接粘贴 Token，减少联调步骤；使用 deviceId 发送时才需要先登记。

**为什么 accepted 不等于已收到？**

后端在 Admin SDK 返回消息 ID 后响应 `status: accepted`，表示发送请求被 FCM 接受。手机是否收到、是否显示通知，还要在设备上确认。

## 四、怎么做

### 1. 前端：配置并运行 Android App

#### 第一步：核对应用配置

1. 在 Firebase 中注册包名 `com.example.appdemo` 的 Android 应用。
2. 下载该 Android 应用的 `google-services.json`，放到 `D:\yin\appdemo\nativeResources\android\google-services.json`，保留文件名。
3. 核对 Firebase 配置、根目录 AndroidManifest.xml 和实际打包包名一致。
4. 检查 [manifest.json](/D:/yin/appdemo/manifest.json) 中的通知权限及 `targetSdkVersion: 33`。

当前 UTS 模块已经声明 Firebase 依赖和消息接收服务，不需要再用旧的 `uni.requireNativePlugin('Lak-FCM')` 示例替换现有导入方式。插件调整记录见 [LOCAL_CHANGES.md](/D:/yin/appdemo/uni_modules/Jairo-FCM/LOCAL_CHANGES.md)。

#### 第二步：制作安装包

在 HBuilderX 中制作包含当前 Firebase 插件及配置的自定义基座，运行时选中该基座；或打正式 APK，安装到目标手机。

如果原生配置发生变化，需要重新打包。已安装的正式 APK 也需要重新打包安装，才能包含后续页面和逻辑修改。

#### 第三步：初始化并获取 Token

打开 App 后，`App.vue` 的 onShow 会进入 `onDemoShow()`，首次自动执行初始化。也可以点击“初始化 / 刷新 Token”。当前主要流程为：

**初始化原生 FCM → 检查通知权限 → 读取 Token → 有后端配置则同步设备 → 读取缓存消息 → 启动前台定时读取**。

允许通知后核对权限状态，复制页面中的真实 Token。更换手机、从模拟器换到真机或重装后，要使用当前设备重新获取的 Token。

### 2. 后端：配置并启动 Node.js 服务

#### 第一步：安装依赖、准备配置

```powershell
# 进入本项目；package.json 要求 Node.js 22 或更高版本。
Set-Location D:\yin\appdemo
npm install --omit=optional

# 首次使用时复制模板；已有本地配置时保留。
if (-not (Test-Path -LiteralPath 'server/.env')) {
    Copy-Item -LiteralPath 'server/.env.example' -Destination 'server/.env'
}
```

在同一 Firebase 项目的“项目设置 → 服务账号 → Firebase Admin SDK”中生成新的私钥，下载第二个 JSON。按本项目示例，可将它命名为 `firebase-admin.json`，保存在 `D:\app-secrets\firebase-admin.json`，再将此路径填写到 `server/.env` 的 `GOOGLE_APPLICATION_CREDENTIALS`。

已有可用凭据时继续使用原文件，不必每次运行都重新生成。**不要将 Android 的 google-services.json 填到这个后端凭据路径。**

两个 JSON 配好以后，还要按当前 Demo 的实现设置接口密钥。首次配置、尚未设置 Demo Key 时，可以这样生成：

```powershell
# 生成 48 位十六进制随机字符串；命令只打印结果，不会自动写入 .env。
node -e "console.log(require('node:crypto').randomBytes(24).toString('hex'))"
```

将结果写到 `DEMO_API_KEY=` 后面，再在 App 和电脑发送页填写同一个值。已有配置则继续使用原值；若更换 Key，需要同步更新两端输入并重启后端。

下面只展示配置结构，Demo Key 的占位内容需要替换为自己的随机值：

```dotenv
# Firebase 项目应与 Android 客户端配置一致。
FIREBASE_PROJECT_ID=hellofcm-e7e57

# 服务账号凭据只供后端读取，不能放入手机安装包。
GOOGLE_APPLICATION_CREDENTIALS=D:/app-secrets/firebase-admin.json

# 本项目自行设置的接口密钥，不是 Firebase 发放的 Key；当前代码要求填写。
# App 同步设备、电脑发送消息时，使用相同的值。
DEMO_API_KEY=replace-with-your-own-random-key

# 监听局域网时，项目要求 Demo Key 至少 16 位。
HOST=0.0.0.0
PORT=3001
```

当前本地配置使用 3001；模板默认 3000。实际访问地址应以自己的配置和启动日志为准。

#### 第二步：启动服务

```powershell
# 从项目根目录启动，启动命令会读取 server/.env。
npm start
```

电脑打开 [本项目发送页](http://localhost:3001/)。修改 `.env` 或后端代码后，先 Ctrl+C 停止，再重新执行 `npm start`。

服务能启动、健康检查通过，不代表 Google 认证已经成功：当前代码在首次发送时才初始化 Admin SDK，凭据和网络问题可能到发送时才暴露。

### 3. 前后端联调：先直接粘贴 Token 发送

这是最少步骤的验证方式，暂时不需要手机访问电脑接口。

1. App 允许通知，复制当前设备的 FCM Token。
2. 电脑打开 `http://localhost:3001/`，填写 Demo API Key 和这个 Token。
3. 填写标题、正文，消息类型选择“通知 + 数据”。
4. 角标计数可以先保持默认 1。
5. 手机按 Home 键进入后台，再在电脑点击发送。
6. 下拉手机系统通知栏确认到达。

电脑发送页由本项目的 `server/public/index.html` 提供，地址是服务根路径 `/`。当前 App 首页的部分引导文案和示例地址与这套 Node.js 服务不一致，本节操作以 **server/.env、启动日志和上述根路径发送页**为准。

### 4. 前端：按需同步设备到后端

如果需要让后端通过 deviceId 查找 Token：

1. 在 App 的服务器地址输入区填写电脑地址，例如 `http://192.168.1.10:3001`，末尾不加 `/api`。
2. Demo API Key 填写 `server/.env` 中的相同值。
3. 点击“保存配置”，再点击“同步 Token”。
4. 确认页面显示“Token 已同步”。

`registerDevice()` 会向 `POST /api/devices` 提交 deviceId、token 和 platform；本项目 Node.js 服务使用其中的 deviceId 与 token 建立绑定。后续回到前台时，App 也会尝试同步当前 Token。

手机上的 localhost 指向手机自己，不能代替电脑局域网 IP。手机访问本地接口需要网络连通；仅从电脑粘贴 Token 发送 FCM 时，手机不必与电脑处于同一局域网。

### 5. 后端：消息怎样构造并发送

`server/app.js` 的 `buildMessage()` 校验输入、组装消息，再由 `server/index.js` 调用 `getMessaging(app).send(message)`。

下面是当前“通知 + 数据”模式的核心结构示意，字段对应项目实现：

```javascript
// 实际项目中，token、title、body 和 badgeCount 先由接口校验。
const message = {
  token, // 当前设备的 FCM 注册 Token。
  notification: { title, body }, // 用于通知标题和正文。
  data: { title, body, demoId, sentAt }, // 自定义数据字段均使用字符串。
  android: {
    priority: 'high', // FCM 投递优先级，不等于系统通知频道重要级别。
    ttl: 86400000, // 当前项目设为 24 小时，单位为毫秒。
    notification: { notificationCount: badgeCount }, // 此条通知代表的数量。
  },
}
```

| 参数 | 当前 Node.js 服务的处理 |
| --- | --- |
| token / deviceId | 直接使用 token，或根据已登记的 deviceId 查询 Token |
| title | 必填，最多 80 个字符 |
| body | 必填，最多 500 个字符 |
| mode | notification 或 data，默认 notification |
| badgeCount | 通知模式默认 1，必须为 1～9999 的整数 |
| data 模式 | 只保留数据，不添加 notification 和通知计数 |

FCM 明确返回 `registration-token-not-registered` 时，后端会删除内存中对应 Token 的绑定，并返回可操作的错误说明。

### 6. 前端：怎样观察消息与角标

| 场景 | 当前 Demo 的观察位置和行为 |
| --- | --- |
| App 在前台 | 原生回调将消息写入本地缓存，页面读取后显示；当前未主动创建前台系统通知 |
| App 在后台，“通知 + 数据” | 查看系统通知栏；该通知不一定出现在页面缓存列表 |
| 仅数据模式 | 交给 App 的原生消息处理，不会由当前代码自动生成系统通知和角标 |
| 电脑显示 accepted | 还需在接收设备上确认实际到达 |

页面消息按 messageId 或 demoId 去重，最多保留 50 条；原生缓存同样限制为 50 条。后台通知点击后的业务跳转，当前项目还未实现完整桥接。

角标计数由后端的 `badgeCount` 转为 `android.notification.notificationCount`，表示这一条通知代表的数量，不能直接当作完整业务未读总数。

项目 README 记录的 MuMu / Lawnchair 配置方式是：允许桌面的“通知使用权 / 通知访问权限”，再开启桌面“通知圆点 / 角标”。保留活动通知后检查图标或长按菜单；显示圆点还是数字取决于桌面，不是只填写计数就能统一控制。

### 7. 前后端检查方法

```powershell
# 运行项目已有测试，覆盖接口、设备绑定、消息参数和 JS/UTS 桥接等逻辑。
# 测试使用替代发送器，不会向 Google FCM 发送真实消息。
npm test

# 使用项目脚本检查 Vue 编译以及相关 JavaScript 语法。
# 该检查不能代替 Android 原生打包和设备收发验证。
npm run check
```

测试入口见 [tests/fcm.test.js](/D:/yin/appdemo/tests/fcm.test.js)、[tests/fcm-api.test.js](/D:/yin/appdemo/tests/fcm-api.test.js)；检查脚本见 [scripts/check.mjs](/D:/yin/appdemo/scripts/check.mjs)。真实推送仍按前面的联调步骤在手机或模拟器上确认。

## 五、总结

### 1. 前端总结

前端完成 **原生 SDK 接入、权限申请、Token 获取、设备登记、前台消息展示**。其中 UTS / Kotlin 负责与 Android Firebase SDK 交互，Vue 页面负责展示与操作，App 生命周期决定何时刷新和读取缓存。

需要记住：

- 当前设备的 Token 用于接收推送，deviceId 用于登记和更新绑定。
- 每 3 秒读取的是原生本地缓存，后台通知不依赖该定时器。
- 通知权限返回值可能早于用户完成弹窗操作，需要后续核验。
- Token 原生更新会写入缓存，后台尚无实时 JS 事件自动上报后端。
- 通知点击和冷启动业务跳转，仍需要继续完善。

### 2. 后端总结

后端完成 **接口鉴权、保存设备与 Token 的关系、校验并构造消息、调用 Admin SDK、返回发送结果**。电脑发送页只是后端接口的操作入口，服务账号始终由后端持有。

当前实现适合独立演示：设备记录在内存中，服务重启会丢失；接口使用共享 Demo Key，没有登录用户关联，也没有完整的业务消息库、重试队列和阅读回执。

**Demo Key 是可以改造移除的项目接口鉴权，当前代码却不能直接不填；Firebase 发送身份凭据和接收设备 Token 仍需分别配置。**

这份项目的最短使用流程是：**配好两端 Firebase 配置 → 安装 Android App → 获取 Token → 启动本项目 Node.js 服务 → 电脑根路径发送页填 Token → App 退后台 → 查看系统通知栏**。
