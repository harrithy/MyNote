# Google FCM 接入总结

更新日期：2026-11-05。已结合 `D:\yin\appdemo` 与 `D:\yin\myblog_last_new` 最新代码、测试及打包验证结论同步更新。适用场景：**普通 uni-app、仅 Android、主要面向香港用户、自行分发 APK、已有自己的业务后端和数据库**。

当前项目采用：**Jairo-FCM UTS 插件 + myblog_last_new Go 博客后端（MySQL 持久化） + Firebase Admin SDK**，同时在 `appdemo` 内保留独立的 **Node.js 22+ 示例后端（`http://localhost:3001`）** 供无数据库快速测试。客户端通过 [common/fcm-api.js](/D:/yin/appdemo/common/fcm-api.js) 同时兼容 Go 后端的 `{ code, data, msg }` 响应信封与 Node.js 示例后端的直接 JSON 返回。

**当前进展：服务账号已配置并通过 Google 认证；MuMu Android 12L 模拟器与小米 17（澎湃 OS）真机正式 APK 均已验证收到真实 FCM 推送；开启 `appdemo` 的「后台自启动」与「无限制」省电策略后，真机在关闭（划掉）App 状态下同样能正常接收系统通知；发送台已支持角标计数（1～9999），推送服务与设备持久化（`push_devices` 表）已完整迁入 Go 博客后端（`http://localhost:8080/static/push.html`），App 端新增 `targetSdkVersion: 33`、自动权限状态同步、稳定设备 ID 展示与双后端响应兼容校验（16 项本地单元/接口测试全部通过）。**

## 1. 先记住这几个结论

| 问题 | 结论 |
| --- | --- |
| FCM 是什么？ | Google 的消息推送服务，把后端发送的通知或数据投递到 App |
| 是否必须上架 Google Play？ | 不需要，可以自行分发 APK |
| 手机能使用 Play Store 就一定能收到推送？ | 只能作为初步判断，还要验证 Play 服务、FCM 注册、网络和通知权限 |
| 是否必须使用 uniCloud？ | 直连 FCM 不需要；普通 uni-app 使用 uni-push 2.0 的标准发送方案会用到 uniCloud |
| 是否只接后端 SDK 就够了？ | 不够，App 要注册接收，后端要管理设备并编写业务触发逻辑 |
| 能否在后台或锁屏时收到？ | 满足设备、网络、权限及系统条件时可以；手机断网不能实时收到，系统“强行停止”不能保证接收 |
| 手机和电脑必须同一个 Wi-Fi？ | FCM 投递不要求；手机访问电脑的本地测试后端时，需要能连通电脑地址 |
| 通知到了就一定有横幅或数字角标？ | 不一定，分别取决于通知频道、系统设置和桌面的支持 |
| 是否免费？ | FCM 本身免费；服务器、数据库、云函数和第三方插件等分别计算成本 |

应用分发和设备要求见 [Android FCM 接入文档](https://firebase.google.com/docs/cloud-messaging/android/get-started)，费用见 [Firebase 官方定价](https://firebase.google.com/pricing)。

## 2. FCM 在业务里负责什么

发送链路：**业务事件 → 自己的后端 → Google FCM → 对应手机上的 App / 系统通知栏**。

以聊天系统为例：

1. A 给 B 发送消息。
2. 后端保存消息及未读状态。
3. 后端查询 B 绑定的有效推送标识，按业务规则决定是否提醒。
4. 后端调用 FCM，向 B 的设备发送通知。
5. B 点击通知，App 根据业务 ID 打开会话，再从业务接口同步完整消息。

**WebSocket 可以负责在线消息，FCM 负责后台提醒，完整记录和未读数仍由业务后端管理。**安装 Admin SDK 后不会自动监控数据库，发送时机仍要接入自己的业务流程。

## 3. 两种接入方式

### 3.1 自己的后端直连 FCM：当前 Demo 的路线

**App 集成 FCM 插件 → 获取注册标识 → 上传业务后端 → 后端通过 Admin SDK / HTTP v1 发送 → FCM 投递**。

需要自己处理 App 原生集成、设备注册更新、用户绑定、发送逻辑和通知点击。适合已有后端、主要需要 FCM、希望发送逻辑留在自己服务器的项目。

### 3.2 uni-push 2.0 配置 FCM 通道

**App 获取 cid → 上传业务后端 → 业务后端调用 uniCloud 云函数 → uni-push → FCM 通道 → 手机**。

这是配置 FCM 通道后的离线投递链路；uni-push 还包含在线通道，前台收到消息不能证明 FCM 离线通道已经验证成功。

| 对比项 | 直连 FCM | uni-push 2.0 + FCM |
| --- | --- | --- |
| App 端 | 独立 FCM 插件或自行封装原生 SDK | 开启 uni-push，配置 FCM 厂商通道 |
| 业务后端使用的设备标识 | 当前 Demo 为 FCM registration token | uni-push 的 cid |
| 标准发送入口 | 自有后端调用 Admin SDK / HTTP v1 | uniCloud 的 uni-push 服务端接口 |
| 业务数据 | 保存在自己的数据库 | 也可以保存在自己的数据库 |
| uniCloud 用量 | 此推送链路不使用 | 云函数及内部依赖资源可能产生用量 |
| 需要维护的内容 | 原生桥接、设备管理、发送及点击处理 | 云函数转发、通道配置、cid 管理及点击处理 |

普通 uni-app 与 uni-app x 的可用方案存在区别，以上按当前项目的普通 uni-app 整理。参见 [uni-push 2.0 官方说明](https://uniapp.dcloud.net.cn/unipush-v2.html)。

uni-push 方案可以只让云函数转发推送，用户、聊天记录、未读数及用户与 cid 的关系继续保留在自有数据库。但官方扩展库还依赖 `opendb-tempdata`、`opendb-device`、`uni-id-device` 等内部表，不能理解为完全没有 uniCloud 数据库用量。参见 [扩展库依赖说明](https://uniapp.dcloud.net.cn/unipush-v2.html)。

## 4. 接入前要准备什么

| 类别 | 准备内容 |
| --- | --- |
| 账号和项目 | Google 账号、Firebase 项目及管理权限 |
| 应用身份 | 固定 Android 包名，Firebase 注册包名、原生配置和实际打包包名一致 |
| App 开发能力 | 能集成插件、修改原生配置，并重新制作基座或 APK |
| 客户端配置 | 对应 Android 应用的 google-services.json |
| 测试设备 | 有兼容、正常运行的 Google Play 服务；模拟器需要合适的 Google APIs / Play 服务环境 |
| 系统版本 | 当前 Google 入门文档要求 Android 7.0+，实际还要符合所选 SDK 和插件版本的要求 |
| 手机网络 | 能连接 FCM；公司 Wi-Fi、防火墙、省电策略都需要实际验证 |
| 通知展示 | Android 13+ 申请 POST_NOTIFICATIONS；确认 App 通知和通知渠道未被关闭 |
| 后端 | 能访问 Google 认证及 FCM API，使用可信的服务端环境 |
| 发送权限 | 启用 Firebase Cloud Messaging API（HTTP v1），准备有发送权限的服务账号身份 |
| 设备管理 | 保存用户与安装实例的关系，支持一个用户多个设备、标识更新和退出解绑 |

设备与通知要求参见 [Android 接入要求](https://firebase.google.com/docs/cloud-messaging/android/get-started)。**插件页面写 Android 5.0+，不代表当前所有 Firebase SDK 组合都支持 Android 5.0。**

香港是本次选型的使用场景，但地区本身不是送达保证，应使用目标机型和实际运营商、Wi-Fi 测试。若服务器部署在大陆，也要单独验证后端出站连接；后端能发送，不代表手机网络能接收。

网络受限时参照 [FCM 网络配置](https://firebase.google.com/docs/cloud-messaging/network-configuration) 检查出站连接及域名规则。官方列出的相关 TCP 端口包括 `5228`、`5229`、`5230`、`443`；这不表示需要给业务服务器开放这些入站端口。

### 4.1 两个 JSON 文件不要混淆

| 文件 | 用途 | 放置位置 |
| --- | --- | --- |
| google-services.json | Android 客户端的 Firebase 项目和应用配置 | 按原生工程或插件要求参与 App 构建 |
| 服务账号私钥 JSON | 后端身份认证，用于取得发送权限 | 后端受控目录；uni-push 方案则按后台要求配置给推送服务 |

服务账号私钥不能打进 APK、放进 `static`、发给浏览器或提交到仓库。`google-services.json` 不能代替后端凭据。支持的部署环境也可以使用运行环境提供的身份，无需强制下载长期私钥。参见 [Admin SDK 初始化与认证](https://firebase.google.com/docs/admin/setup)。

### 4.2 几种标识不要混用

| 标识 | 含义 | 当前项目中的使用方式 |
| --- | --- | --- |
| DCloud AppID | 例如 __UNI__XXXXXX，标识 DCloud 应用 | 不能当 Android 包名 |
| Android 包名 | 例如 com.example.appdemo | 与 Firebase 应用注册及打包配置一致 |
| Firebase project ID | 例如 hellofcm-e7e57 | 确定发送目标项目及对应配置 |
| FCM registration token | 传统 FCM 注册得到的推送地址 | 当前插件返回此值，后端用 token / Java setToken() |
| 已向 FCM 注册的 FID | 新接入方式使用的 Firebase Installation ID | 配套客户端完成注册后，按新版接口使用 fid / Java setFid() |
| uni-push cid | uni-push 设备标识 | 只能用于对应的 uni-push 接口 |

截至整理日期，[Admin SDK 官方发送文档](https://firebase.google.com/docs/cloud-messaging/send/admin-sdk) 已推荐注册后的 FID，并将传统 `token` 字段标记为弃用，迁移期仍支持传统 Token。**当前 Demo 返回什么，就按什么发送；不能仅把字段名改成 fid，也不能将任意未注册的 FID 当作推送地址。**未来迁移需要一起调整客户端注册、插件接口、后端存储及 SDK 版本。

## 5. 直连 FCM 的实际接入步骤

### 第一步：创建 Firebase 项目并注册 Android 应用

1. 打开 [Firebase 控制台](https://console.firebase.google.com/)，创建或选择项目。
2. 添加 Android 应用，填写真实包名。当前 Demo 为 `com.example.appdemo`。
3. 下载 `google-services.json`，保持文件名不变。
4. 核对配置中的包名与实际安装包一致；Android 包名与 DCloud AppID 是两回事。

当前 Demo 的配置路径是 `D:\yin\appdemo\nativeResources\android\google-services.json`，这是**该插件和工程的接法**。原生 Android 工程通常放在应用模块目录，其他插件以自己的构建规则为准。还应确认 Google Services 构建插件实际读取了配置。

### 第二步：接入 App 端插件

当前使用的插件市场页面为 [FCM（推送），ID 27379](https://ext.dcloud.net.cn/plugin?id=27379)。页面名称为 Lak-FCM，实际下载到 Demo 的 UTS 模块目录是 `uni_modules/Jairo-FCM`。

现有工程通过模块导入调用 `initFCM`、`getFCMToken`、`pullFCMMessages`、`requestNotificationPermission`，由 [common/fcm.js](/D:/yin/appdemo/common/fcm.js) 封装。

**不要直接用市场页面旧版的 uni.requireNativePlugin('Lak-FCM') 示例覆盖当前代码。**页面示例与实际下载包不同，Demo 已按源码适配，并修复部分 UTS / Kotlin 兼容问题。修改记录见 [LOCAL_CHANGES.md](/D:/yin/appdemo/uni_modules/Jairo-FCM/LOCAL_CHANGES.md)。

### 第三步：制作并选中自定义基座，或安装正式 APK

新环境接入或原生配置变化后，需要重新打包。当前模拟器已经完成自定义运行环境中的收发验证，下面是复现接入时的操作方式。

调试时：

1. HBuilderX 选择“发行 → 原生 App-云打包”。
2. 使用与 Firebase 一致的包名，选择“打自定义调试基座”。
3. 完成后确认生成 `unpackage/debug/android_debug.apk`。
4. 选择“运行 → 运行到手机或模拟器”，在设备窗口选中“自定义基座 → 本地基座”。

安装到真机测试或自行分发时，按正式打包流程生成 APK：

| 云打包选项 | 当前 Demo 的设置 |
| --- | --- |
| Android 包名 | `com.example.appdemo`，与 [AndroidManifest.xml](/D:/yin/appdemo/AndroidManifest.xml) 及 [google-services.json](/D:/yin/appdemo/nativeResources/android/google-services.json) 一致 |
| Android 证书 | 使用云端证书（`google-services.json` 未绑定特定 SHA-1 指纹，可直接用云端证书） |
| 包类型 | 打正式包 |
| 渠道包 | 无 |
| GooglePlay（AAB） | 当前自行安装 APK 不需要选择；用于相应的商店发布流程 |
| 打包方式 | 快速安心打包（若提示包含原生插件/资源或必选图标，可配置图标或切换为传统打包） |

> **真机安装避坑提示**：若手机此前安装过同包名的自定义调试基座（`unpackage/debug/android_debug.apk`），由于调试基座与正式云打包 APK 的签名不同，**安装正式包前需先卸载手机上的旧包**，否则系统会提示签名冲突无法安装。

FCM SDK 已由插件集成，不靠勾选 GooglePlay 渠道才生效。调试基座用于 HBuilderX 联调，正式分发使用正式包。渠道选项参见 [DCloud Android 渠道包说明](https://uniapp.dcloud.net.cn/tutorial/build/AndroidChannel.html)。

**标准基座 io.dcloud.HBuilder 使用 DCloud 自己的包名和原生配置，不能承载当前项目新增的 Firebase 配置与依赖。**引入或修改原生 SDK、权限、配置后，需要重新制作包含变更的基座或 APK。参见 [DCloud 自定义基座说明](https://uniapp.dcloud.net.cn/tutorial/run/run-app.html)。

模拟器也需要 Google 服务和可达网络，并与插件的 ABI 匹配。当前插件配置包含 ARM 架构，使用 x86 / x86_64 模拟器时要先核对兼容性。

### 第四步：获取当前设备的 Token，验证接收链路

当前 Demo 已有可用后端，可以按第五步直接发送。对于首次接入、需要分开排查 App 与后端的情况，也可以先用 Firebase 控制台测试：

1. 打开手机上的 Demo，申请并允许通知权限。
2. 点击“初始化 / 刷新 Token”，成功后复制 Token。
3. 电脑进入相同 Firebase 项目的 Messaging，创建通知，选择“发送测试消息”。
4. 粘贴该手机的 Token。
5. 手机按 Home 键退到后台或锁屏，再从电脑发送。
6. 在系统通知栏确认标题和正文。

填写谁的 Token，就向谁的 App 安装实例发送。**从模拟器换到真机后，必须重新获取真机自己的 Token，替换电脑网页中的模拟器 Token。**重装、清除数据后也要重新核对，不能把 Token 当固定的手机号码。控制台测试流程参见 [Google 官方测试步骤](https://firebase.google.com/docs/cloud-messaging/android/get-started#send-a-notification-message)。

### 第五步：后端接入发送能力

| 方式 | 后端需要做的事 | 选择建议 |
| --- | --- | --- |
| Firebase Admin SDK | 引入官方库，由库处理认证和发送请求 | 后端语言支持时优先采用 |
| HTTP v1 API | 获取 OAuth 2.0 access token，构造 HTTPS 请求并处理刷新及错误 | 不便引入 SDK 时采用 |

两者选一种即可，都运行在后端。HTTP v1 的发送地址为 `https://fcm.googleapis.com/v1/projects/PROJECT_ID/messages:send`，认证使用 `Authorization: Bearer ACCESS_TOKEN`；此 access token 与手机的 FCM Token 完全不同。参见 [HTTP v1 发送及认证](https://firebase.google.com/docs/cloud-messaging/send/v1-api)。

当前 Demo 的服务账号凭据已放到 `D:\app-secrets\firebase-admin.json`，并在新增聊天中确认 Google 认证成功。当前环境不需要再重复生成私钥；换电脑或部署服务器时再配置对应凭据。

当前项目提供**两套等价的后端运行方案**（App 端通过 [common/fcm-api.js](/D:/yin/appdemo/common/fcm-api.js) 的 `readBackendResponse` 自动兼容两者的响应格式）：

#### 方案 A：连接 `myblog_last_new` Go 博客后端（主推，MySQL 持久化）

完整说明见 [博客推送集成文档](/D:/yin/myblog_last_new/docs/PUSH_INTEGRATION.md)。设备记录持久化到 MySQL 的 `push_devices` 表（按安装级稳定 `device_id` 覆盖更新 Token，服务重启不丢失）；手机使用 `X-Demo-Key` 调用 `POST /api/devices` 登记设备，电脑推送管理页使用博客管理员 **Owner JWT (`Authorization: Bearer <JWT>`)** 调用 `/api/push/*`。

在 `D:\yin\myblog_last_new\.env` 中补充配置：

```dotenv
# 与 Android App 的 google-services.json 中的 project_id 一致
FIREBASE_PROJECT_ID=hellofcm-e7e57

# 填运行 Go 服务的机器上的凭证路径；Linux 部署时换成服务器的实际路径
GOOGLE_APPLICATION_CREDENTIALS=D:/app-secrets/firebase-admin.json

# 替换为原 server/.env 的 DEMO_API_KEY，或新生成的随机 Key（至少 16 位）；App 填相同的值
PUSH_DEMO_KEY=your-existing-demo-key
```

启动 Go 服务（默认端口 `8080`）：

```powershell
Set-Location D:\yin\myblog_last_new
go run main.go
```

Go 后端使用流程：

1. 手机 App 的「连接博客后端」填写后端根地址（例如 `http://192.168.1.10:8080` 或线上 HTTPS 域名，**末尾不加 `/api`**），填写 `PUSH_DEMO_KEY` 后点击「同步 Token」。
2. 电脑打开 [博客推送台](http://localhost:8080/static/push.html)，使用博客管理员登录后的 JWT 刷新设备列表，直接选中 App 页面显示的**本机设备 ID**（或粘贴 Token），即可发送通知和角标计数。

#### 方案 B：运行 `appdemo` 独立 Node.js 示例后端（保留供无数据库独立测试）

后端读取项目根目录下的 `server/.env`。当前实际配置是 **PORT=3001**，因为原来的 3000 端口被其他项目占用。源码默认值及旧 README 示例仍可能是 3000，使用时以实际配置和启动日志为准。

首次安装后端依赖、启动或重启服务：

```powershell
# 在 Demo 根目录安装依赖；当前工程要求 Node.js 22 或更高版本。
Set-Location D:\yin\appdemo
npm install --omit=optional

# 仅在配置不存在时复制模板，保留已有本地配置。
if (-not (Test-Path -LiteralPath 'server/.env')) {
    Copy-Item -LiteralPath 'server/.env.example' -Destination 'server/.env'
}

# 当前环境已有配置，直接启动；若终端已运行，先 Ctrl+C 再重新启动。
npm start
```

`server/.env` 的关键配置结构如下。当前文件已配置好，下面用于理解或迁移；Demo Key 使用自己生成的随机值，不要用示例占位内容覆盖现有配置：

```dotenv
# Firebase 项目应与 App 的客户端配置对应。
FIREBASE_PROJECT_ID=hellofcm-e7e57

# 后端私钥存放在项目外，Windows 路径可使用正斜杠。
GOOGLE_APPLICATION_CREDENTIALS=D:/app-secrets/firebase-admin.json

# 本地演示接口使用随机测试 Key，至少 16 位；正式业务换成真实鉴权。
DEMO_API_KEY=replace-with-a-long-random-demo-key

# 手机同步 Token 时需要访问电脑；只在电脑使用时可监听 127.0.0.1。
HOST=0.0.0.0
PORT=3001
```

Node.js 本地发送台操作：

1. 保持后端终端运行，电脑打开 [本地发送台](http://localhost:3001)。
2. 填写 `server/.env` 中的 Demo API Key，以及接收设备自己的 FCM Token。
3. 填写标题、正文，消息类型选“通知 + 数据”；角标计数可先保持默认 1。
4. 在接收设备上允许通知，按 Home 键退到后台，再在电脑点击发送。
5. 下拉系统通知栏确认到达；不要仅凭网页返回 accepted 判断手机已经收到。

#### 手机打包安装后与电脑发送台的网络关系

- **方式 1（直接粘贴手机 Token 发送，无需局域网互通）**：手机安装正式 APK 获取 Token 后，把 Token 复制到电脑 `http://localhost:3001` 或 `http://localhost:8080/static/push.html` 直接发送。此时走的是 `电脑 -> Google FCM 云端 -> 手机 Google Play 服务`，**手机完全不需要访问电脑的 `3001`/`8080` 端口**，使用 4G/5G 移动流量或不同 Wi-Fi 同样能收到。
- **方式 2（在手机 App 内点击「同步 Token」，需要网络可达后端）**：手机主动调用后端的 `POST /api/devices`，此时服务器地址需填写电脑的局域网 IP（例如 `http://192.168.1.10:8080` 或 `http://192.168.1.10:3001`）且防火墙放行对应端口。**手机上的 `localhost` 指向手机自己；`0.0.0.0` 是服务监听地址，都不是手机应填写的电脑地址。**

Demo 的局域网 HTTP（通过 `AndroidManifest.xml` 的 `usesCleartextTraffic="true"` 开启）仅用于开发测试，正式服务应使用 HTTPS。完整使用说明见 [Demo README](/D:/yin/appdemo/README.md)。

移入 Java 后端时，同样是初始化一次 Admin SDK，再在业务触发时构造通知和 data。当前插件对应 `setToken(fcmToken)`；完成新版 FID 注册迁移后才对应 `setFid(registeredFid)`。服务端凭据的配置方式参见 [Admin SDK 官方说明](https://firebase.google.com/docs/admin/setup)。

## 6. 前台、后台和“离线”分别是什么表现

### 6.1 消息类型与 App 状态

下表针对**当前 Demo 使用的传统 AndroidConfig 消息机制**，不直接套用到新版 AndroidConfigV2。官方已区分两套接收行为，迁移时要重新检查通知展示策略。参见 [Android 消息接收说明](https://firebase.google.com/docs/cloud-messaging/android/receive-messages)。

| 消息类型 | App 在前台 | App 在后台 |
| --- | --- | --- |
| 通知消息 | 进入原生回调，是否展示由 App 处理 | 通常由 SDK / 系统展示到通知栏 |
| 纯数据消息 | 进入原生回调，由 App 处理 | 依赖系统调度及消息优先级，不自动变成通知 |
| 通知 + 数据 | 原生回调可获得内容 | 通知进入通知栏，点击后的 data 通过启动 Activity 的 Intent 传递 |

当前 Demo 在前台把消息存到插件本地缓存，页面每 3 秒读取一次；代码没有主动弹出前台系统通知。**这 3 秒是在读手机本地缓存，不是在轮询业务服务器。**后台会停止 JS 定时器，FCM 投递仍由原生 SDK 与 Google 服务承担。

后台通知不一定经过插件的 `onMessageReceived`，因此“通知栏收到了，但页面消息列表没有记录”可能是预期行为。点击后的 Intent 参数还需要桥接给 uni-app，当前 Demo 尚未完成业务跳转。

| 设备或 App 状态 | 接收边界 |
| --- | --- |
| 按 Home 退后台、锁屏 | 正常的离线通知验证场景，仍需权限、网络、Google 服务正常 |
| 进程被系统回收 | 通知可由系统通道处理，但要验证目标机型及省电策略 |
| 从最近任务划掉（关闭 App） | 港版/原生 Android 系统可直接收到；**国行系统（如小米 17 澎湃 OS）默认将其视为强行停止并拦截 GMS 唤醒广播，需开启 App 的「后台自启动」与「省电无限制」后才可在关闭状态下收到** |
| 手机断网或关机 | 无法实时接收，恢复网络后是否补投递受消息有效期等影响 |
| 系统设置中“强行停止” | 通常要用户重新打开 App，不能承诺该状态下仍能收到 |

这里的“离线”指 App 没有保持自己的业务连接，**不表示手机不需要联网**。强行停止等状态限制也可参考 [FCM 官方接收前提](https://firebase.google.com/docs/cloud-messaging/flutter/receive-messages)。

当前 Demo 与 Go 后端的消息 TTL 已由原先的 60 秒调整为 **24 小时（`86400000` ms）**，避免手机因网络或代理短暂断连超过 1 分钟就被 FCM 直接丢弃消息。后端返回 `messageId` / `accepted` 表示 FCM 接受了请求，不能当作手机已送达或用户已阅读。

### 6.2 通知栏有消息，为什么没有顶部横幅

当前模拟器已经确认生成系统通知，但使用普通重要级别的通知频道，可能只出现在下拉通知栏，不弹顶部横幅。

要支持横幅，需要 App 创建相应的高重要级别频道，并让消息使用该频道；还要由用户允许横幅通知，设备的勿扰等设置也会影响展示。**FCM 的 android.priority=high 控制投递优先级，不等于通知频道的重要级别。**

Android 8.0+ 的频道创建后，不能靠重新创建同 ID 的频道直接提升已有重要级别；已有频道由用户在设置中调整，或按产品需要创建新频道。参见 [Android 通知频道说明](https://developer.android.com/develop/ui/compose/notifications/channels)。

### 6.3 国行真机（如小米 17 澎湃 OS）实测常见问题

1. **为什么需要先点开「Play 商店」才能收到推送？**
   - Android 上的 FCM 推送由系统底层的 **Google Play 服务（GMS）** 维护长连接（`mtalk.google.com:5228-5230`），再通过广播唤醒 `appdemo`。
   - **国行系统省电冻结**：国行 ROM 默认不把 Google Play 服务当作核心免杀白名单，后台或锁屏后容易将其休眠；手动点开 Play 商店会通过系统 Binder 强行唤醒 GMS 并立即重建 FCM 长连接。
   - **代理晚于开机启动**：若先开机后开代理，GMS 此前重连失败已进入指数退避休眠（需等十余分钟才重试），打开 Play 商店会强制触发立即重连。
   - **解决设置**：在手机「设置 → 应用管理 → 显示系统应用」中，将 **Google Play 服务**、**Google 服务框架** 及 **`appdemo`** 的省电策略设为「无限制」，并开启 **`appdemo` 的自启动 / 关联启动**。
2. **为什么有时候能收到、有时候收不到？**
   - **前后台查看位置不同**：App 在前台时，消息由插件 `onMessageReceived` 写入本地缓存，显示在页面底部「收到的消息」列表，**不弹系统通知栏**；App 在后台/锁屏时，「通知 + 数据」由系统直接弹在**系统通知栏**，**不进页面消息列表**。
   - **代理节点掐断空闲 TCP 长连接**：许多代理节点会将空闲 1～3 分钟无流量的 TCP 长连接静默掐断，导致 GMS 处于“假在线”状态，直到下次心跳超时才重连。
   - **从最近任务上滑划掉 App**：国产系统会将划掉后台视为接近“强行停止”，拦截 GMS 广播唤醒。
   - **拨号盘诊断彩蛋**：在手机拨号盘输入 **`*#*#426#*#*`** 可调出 Google Play 服务的 **FCM Diagnostics** 面板，查看是否处于 `Connected` 状态及 `EVENTS` 收发日志。
3. **为什么 Android 13+（小米 17）打开 App 没弹出通知权限框，或每次打开显示“尚未申请”？**
   - HBuilderX 未显式配置 `targetSdkVersion` 时默认按 `30`（Android 11）打包；在 Android 13+（API 33+）上，`targetSdkVersion < 33` 的应用调用 `requestPermissions(POST_NOTIFICATIONS)` 会被系统忽略而不弹窗。
   - **已修复**：在 [manifest.json](/D:/yin/appdemo/manifest.json) 中显式设置 `"targetSdkVersion": 33`，并在 [common/fcm-demo.js](/D:/yin/appdemo/common/fcm-demo.js) 的 `initializeFcm` 与 `onDemoShow` 中自动检查和刷新通知权限状态（修改 `manifest.json` 后需重新云打包 APK 生效；旧包可直接长按桌面图标 → 应用信息 → 通知管理手动开启）。
4. **为什么把 App 关闭（从最近任务上滑划掉）后就收不到通知了？（已实测验证解决）**
   - **原因**：当 `appdemo` 被关闭后，手机里的 Google Play 服务收到 FCM 推送时，需要发送系统广播（`com.google.android.c2dm.intent.RECEIVE`）唤醒 `appdemo` 的 `LakFirebaseMessagingService` 来生成通知。在国行小米 17（澎湃 OS / HyperOS）等国产 ROM 中，只要普通应用未开启「自启动」，一旦从最近任务划掉卡片，系统就会将其置入类似 `Force Stop` 的冻结状态，**直接拦截 Google Play 服务的唤醒广播**。
   - **解决办法（小米 17 实测通过）**：
     1. 长按桌面 `appdemo` 图标 → 点击「应用信息 ⓘ」→ 开启 **「自启动（后台自启动）」**（允许 Google Play 服务通过广播在后台拉起 `appdemo`）；
     2. 进入「省电策略 / 电量消耗」→ 设为 **「无限制」**；
     3. 电脑发送台消息类型选择 **「通知 + 数据」**（纯数据消息不会自动生成系统通知栏消息）。
   - **香港业务场景区分**：港版/海外版 Android 手机（含港版小米国际版 ROM）将 FCM 作为系统级原生推送通道，划掉后台卡片不会拦截 GMS 推送广播；若香港用户使用的是内地购买的国行手机，则可在 App 内引导用户开启「后台自启动」权限。

## 7. 接入真实业务还要补齐什么

### 7.1 用户和设备绑定

- 一个用户可以有多个安装实例，不能只保存一个 Token。
- App 启动、登录、回到前台时同步当前标识，并记录更新时间。
- 原生标识更新后同步后端；卸载重装、清数据或迁移设备后不要继续依赖旧值。
- 后端根据明确的无效注册错误清理绑定；不要把所有请求参数错误都当作设备失效。
- 退出登录、切换账号时解除或更新绑定，避免向上一位用户的设备身份继续发送。

传统 Token 可以反复使用，但不能保存一次就永久不管。Android 注册连续 **270 天不活跃**可能被 FCM 判定过期，这不是从创建日起固定有效 270 天。参见 [FCM 注册管理最佳实践](https://firebase.google.com/docs/cloud-messaging/manage-tokens)。

当前插件的 `onNewToken` 会更新本地缓存，Demo 在启动、回到前台等时机读取并同步；尚无实时 JS Token 更新事件，后台轮换后的即时上报仍需完善和验证。

### 7.2 通知点击与数据一致性

通知附带会话 ID、消息 ID 或业务 ID，点击后先处理登录和页面就绪，再按业务权限查询详情。要覆盖 App 已打开和冷启动两种情况。

聊天记录和未读数以业务后端为准，收到推送只作为提醒或同步触发。可用业务消息 ID 去重，避免 WebSocket 与 FCM 同时到达时重复插入。

### 7.3 演示服务与博客 Go 后端的演进

原 Node.js 示例服务将设备记录保存在进程内存 Map 中，重启会丢失；现已将设备管理与推送能力等价迁移至 `D:\yin\myblog_last_new` 的 Go 博客后端：

- **持久化**：使用 MySQL 的 `push_devices` 表按安装级 `device_id` 唯一索引保存 `token`、`platform`、`app_version` 及 `last_seen_at`，服务重启不丢失，FCM 返回 `registration-token-not-registered` 时自动删除失效绑定。
- **权限分离**：手机设备登记（`POST /api/devices`）使用 `X-Demo-Key`（常量时间比较）；推送管理端（`/api/push/health`、`GET/DELETE /api/push/devices`、`POST /api/push/send`）使用博客管理员 **Owner JWT** 鉴权，列表接口仅返回掩码后的 Token。
- **客户端防误报**：App 端的 [common/fcm-api.js](/D:/yin/appdemo/common/fcm-api.js) 解包 Go 的 `{ code, data, msg }` 响应信封，若遇 Key 错误、数据库失败、HTTP 200 内包裹非 2xx 业务码或误填网页地址返回 HTML，均会明确抛出错误，不会误报同步成功。
- **正式业务仍需补齐**：将 `push_devices.user_id` 与真实登录用户关联、退出登录解绑、失败重试与推送审计日志。

### 7.4 桌面图标角标：已增加计数，展示取决于桌面

当前发送台已增加“角标计数”，在“通知 + 数据”模式下默认 **1**，允许 **1～9999 的整数**。后端接收 `badgeCount`，转换为 Admin SDK 的 `android.notification.notificationCount`；纯数据模式不提交通知计数。

**这次修改在后端和发送网页，现有 Android Firebase SDK 可以处理，不需要仅因新增计数就重新打包手机端。**重启后端服务并刷新电脑网页即可使用。

需要区分三层：

| 内容 | 当前实现和边界 |
| --- | --- |
| 后端发送的计数 | 表示这一条通知代表的消息数量；Demo 默认 1 |
| Android 系统通知 | 已在模拟器通知记录中确认计数 3；最新排查的通知也带有计数 1 |
| 桌面图标 | 桌面决定是否显示、显示圆点还是数字；已在开启 Lawnchair 通知使用权后确认长按菜单显示通知计数 |

当前 MuMu 的“有通知没角标”已定位并验证：**通知频道允许角标，但桌面 Lawnchair（app.lawnchair）默认没有获得通知使用权，无法读取通知来生成桌面角标；授权后用户截图已确认长按图标菜单显示通知计数（图标右上角圆点/数字样式取决于具体桌面支持）。** 开启步骤如下：

1. 打开模拟器系统设置，搜索“通知使用权”或“通知访问权限”。
2. 找到“桌面 / Lawnchair”，开启允许。
3. 长按桌面空白处进入桌面设置，开启“通知圆点 / 角标”。
4. 保留通知栏里的消息，回到桌面查看；必要时在 App 退后台后重发一条。

上述权限步骤针对当前 Lawnchair 桌面，不代表所有 Android 手机都需要同样的设置入口。真机还要检查 App 通知开关、频道角标开关和桌面设置。

Android 8.0+ 的标准通知角标依附于活动通知，清除通知后角标可能消失；部分桌面只显示圆点。前台仅缓存消息、发送纯数据消息，都不会自动创建当前 Demo 的系统通知和角标。参见 [Android 桌面通知角标](https://developer.android.com/develop/ui/views/notifications/badges)。

`notificationCount` 的含义见 [Firebase Admin SDK 通知计数](https://firebase.google.com/docs/reference/admin/node/firebase-admin.messaging.androidnotification#androidnotificationnotificationcount)。它不是 Demo 自动计算出的全局未读数，多条通知也可能被桌面合并计数。正式聊天系统仍需以后端未读数为准，并按目标桌面设计更新策略；当前没有接入厂商专用的常驻数字角标接口。

## 8. 费用怎么理解

| 项目 | 费用边界 |
| --- | --- |
| FCM 推送服务 | 免费，不按推送条数额外计价 |
| Admin SDK / HTTP v1 发送 FCM | 调用方式本身不另外收费 |
| 自己的服务器、数据库、文件存储 | 按现有基础设施和网络用量承担成本 |
| Firebase 的数据库、存储、云函数等 | 属于其他产品，按对应规则计算 |
| uni-push 2.0 | 推送服务本身免费，配套 uniCloud 资源可能产生费用 |
| 第三方 uni-app 插件 | 单独看插件授权和定价，不代表所有插件都免费 |

只用 FCM 可以使用不要求支付方式的 Spark 方案。**免费不等于无限速或无限资源**，仍需遵守 [FCM 配额与限制](https://firebase.google.com/docs/cloud-messaging/throttling-and-quotas)。费用依据见 [Firebase 定价](https://firebase.google.com/pricing)。

uniCloud 的免费空间、调用量、计算资源、出网及数据库额度取决于云厂商和方案，不能直接把某个云函数的免费次数当作“FCM 免费推送条数”。正式选用时查 [uniCloud 当前价格](https://doc.dcloud.net.cn/uniCloud/price.html)。

## 9. Demo 已有记录和排查要点

Demo 位于 [D:\yin\appdemo](/D:/yin/appdemo)，博客推送后端位于 [D:\yin\myblog_last_new](/D:/yin/myblog_last_new)。以下状态根据现有源码、测试及文档核对。

| 项目 | 已有记录 / 当前边界 |
| --- | --- |
| App 功能 | 初始化、申请通知权限、获取及同步 Token、展示本机稳定 `deviceId`、读取前台消息缓存、兼容 Go/Node 双后端响应 |
| 后端功能 | 已集成至 `myblog_last_new` Go 后端（MySQL `push_devices` 表持久化、Owner JWT 推送台 `http://localhost:8080/static/push.html`）；同时保留 `appdemo` Node.js 独立发送台（`http://localhost:3001`） |
| 客户端配置 | `nativeResources/android/google-services.json` 已放入项目，包名 `com.example.appdemo`，应用已成功获取 FCM Token |
| 后端凭据 | `D:\app-secrets\firebase-admin.json` 已配置；Google 认证与真实发送已确认成功 |
| 本地端口 | Go 博客后端默认 `8080`；独立 Node.js 示例后端使用 `3001`（原 3000 端口被占用） |
| 本地验证 | `appdemo` 共 **16 项测试通过**（`fcm.test.js` 11 项 + `fcm-api.test.js` 5 项，涵盖 HTTP/UTS 桥接、角标计数、Go 响应解包与异常拦截）；Go 后端推送模块单元与路由测试通过 |
| Kotlin | 修复兼容问题后编译通过，生成 `classes.dex` |
| 模拟器真实收发 | MuMu Android 12L（API 32）自定义运行环境已收到真实 FCM，完成广播分发并生成后台通知 |
| 真机正式 APK 收发 | 小米 17（澎湃 OS）已安装云打包正式 APK 并收到真实 FCM；开启「后台自启动」与「无限制」省电策略后，确认关闭（划掉）App 仍可正常收到通知 |
| 通知计数与角标 | 模拟器系统通知记录已确认 `number=3`；Lawnchair 桌面开启通知使用权后，已确认长按应用图标菜单显示通知计数 |
| 仍需独立验证 | 重新云打包验证 `targetSdkVersion: 33` 自动弹窗、Token 轮换、通知点击和冷启动业务跳转、香港本地运营商直连网络 |

| 现象 | 优先排查 |
| --- | --- |
| 找不到 firebase / FirebaseMessaging | 编译依赖是否下载；运行时是否选中含 Firebase 的自定义基座；SDK 是否真正打入包 |
| Kotlin 提示 getAppActivity 不存在或类型不匹配 | 对照现有 LOCAL_CHANGES.md，保留已修复的 getUniActivity、Void 回调及数组类型适配 |
| 源码编译成功，运行仍缺少类 | 源码通过不等于安装的基座含有依赖，重新制作并切换基座 |
| 获取不到 Token | Google 服务、网络、包名、客户端配置、初始化结果 |
| 3000 端口报 EADDRINUSE | Node 示例已改用 `3001`，Go 博客后端默认 `8080`；电脑页面、手机配置和启动日志的端口要一致 |
| App 同步 Token 提示非有效 JSON / 401 / 503 | 检查服务器地址是否误填了网页 HTML 路径（应填根地址如 `http://IP:8080`，末尾不加 `/api`），核对 `PUSH_DEMO_KEY` / `DEMO_API_KEY` |
| 后端返回认证或权限错误 | 服务账号、ADC 配置、目标项目权限及 HTTP v1 API 启用状态 |
| 后端接受但手机没有通知 | 前后台状态、通知权限、渠道、设备网络、消息类型及 TTL |
| 模拟器能收，真机收不到 | 先换成真机自己的 Token，再检查该机的 Google 服务、通知权限及网络 |
| 真机需先打开 Play 商店才能收到 | 国行系统休眠了 Google Play 服务或代理晚于开机启动；给 Google Play 服务设为省电「无限制」，或用 `*#*#426#*#*` 检查连接 |
| 真机把 App 划掉关闭后收不到通知 | 国行系统（如小米澎湃 OS）拦截了 GMS 唤醒广播；在 `appdemo`「应用信息」中开启**「自启动（后台自启动）」**并将省电策略设为**「无限制」** |
| 真机安装正式包提示签名冲突 | 先卸载手机上之前安装的同包名调试基座（`android_debug.apk`），再安装正式包 |
| 下拉通知栏有消息，没有顶部横幅 | 检查频道重要级别和用户横幅设置，投递优先级 high 不会自动提升频道 |
| 有通知但桌面没角标 | 当前 MuMu 先允许 Lawnchair 的通知使用权，并开启通知圆点；检查频道和桌面支持 |
| 填了角标 3，图标不是数字 3 | 计数是通知属性，桌面可能只显示圆点或在长按菜单展示计数；不能按全局未读数理解 |
| 更新原生配置或前端页面后效果不变 | 调试可用含 FCM 的自定义基座刷新；已安装的独立正式 APK 需重新打正式包安装 |
| 手机访问不到电脑后端 | 使用电脑局域网 IP（不能填 `localhost`），检查监听地址、端口及防火墙；仅从电脑粘贴 Token 发送则无需局域网互通 |

**不要照旧教程重新启用 Legacy API、寻找 Server Key。**DCloud 的部分旧页面仍保留旧配置截图，应使用 [FCM HTTP v1 认证说明](https://firebase.google.com/docs/cloud-messaging/send/v1-api) 和 [UniPush FCM v1 配置指南](https://ask.dcloud.net.cn/article/40982)。客户端 google-services.json 变化后，重新打包使配置生效。

## 10. 当前下一步怎么做

1. **真机打包与安装**：在 HBuilderX 云打包中选择包名 `com.example.appdemo`、云端证书、打正式包、渠道无；卸载手机旧调试基座后安装正式 APK。
2. **真机收发验证（直接粘贴 Token）**：在真机打开 App 允许通知权限并复制真机 Token，在电脑打开 `http://localhost:3001`（Node 独立发送台）或 `http://localhost:8080/static/push.html`（Go 博客推送台），选择“通知 + 数据”，验证真机前台、后台、锁屏通知和角标表现。
3. **真机与 Go 博客后端联调（同步设备）**：手机与电脑处于同一局域网（或通过公网 HTTPS），在 App 内填写 Go 后端地址与 `PUSH_DEMO_KEY` 点击“同步 Token”，在博客推送台按 `deviceId` 选中真机发送。
4. **通知横幅优化**：如需顶部弹出横幅，创建高重要级别（Importance High）通知频道并在发送时指定对应 `channelId`。
5. **业务深度整合**：在 Go 后端将 `push_devices.user_id` 与登录用户关联，补齐退出登录解绑、通知点击与冷启动业务跳转，并按香港目标机型和实际网络验证。

## 11. 原始聊天

- [了解 Google FCM](codex://threads/01a1a52b-9403-75c2-9b66-41937d066759)
- [查询 Google FCM 服务收费情况](codex://threads/01a1a429-3b2a-71f2-98f5-f7ab448f5be5)
- [创建 Google FCM 使用演示](codex://threads/01a1a559-9894-7912-b620-9bc24204e284)
