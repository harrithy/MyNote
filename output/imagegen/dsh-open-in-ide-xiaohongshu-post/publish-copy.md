# 小红书发布文案

## 推荐标题

AI都指出来了，还要手动找代码？

## 备选标题

- 给 DeepSeek Harness 加个直达键
- 做了个小插件，把对话接到IDE
- 点一下文件，直接跳到代码那一行
- 少找一次文件，多写一行代码

## 正文（可直接复制）

给 DeepSeek Harness 写了个小插件：dsh-open-in-ide。

想解决一个很小、但很容易打断思路的动作：AI 已经指出文件和行号，自己还要切回编辑器找位置。

装好后，点击回答里的文件引用，比如 src/app.ts:42，就能在你选的 IDE 中打开文件，定位到第 42 行。点目录引用，也能直接打开文件夹。

支持 VS Code、Cursor、Windsurf 和 JetBrains 系列。用 VS Code 家族时，还会识别所属项目，打开或复用对应的项目窗口。

安装也很直接：
① 设置 → 插件 → 安装，填入 dsh-open-in-ide
② 刷新页面，在已安装插件中启用
③ 设置 → 通用设置 → 打开文件的 IDE，选你常用的编辑器

已经开源，项目地址放在最后一张图。欢迎试用，有问题可以提 issue。

你平时主要用哪款 IDE？

#DeepSeekHarness #AI编程 #开源项目 #开发工具 #Cursor #VSCode

## 图片发布顺序

1. 01-cover.png：封面，点一下文件，直达 IDE。
2. 02-workflow.png：解释使用痛点，对比手动找位置与点击跳转。
3. 03-editors.png：说明支持的编辑器及选择入口。
4. 04-install.png：安装插件、刷新启用、选择 IDE。
5. 05-tips.png：目录打开、保留预览、VS Code 家族项目识别，以及开源地址。

## 项目来源

GitHub：https://github.com/harrithy/dsh-open-in-ide
中文说明：https://github.com/harrithy/dsh-open-in-ide/blob/main/README.zh.md

本套 5 张图片均使用内置 image_gen 工具生成。详情页的界面为功能示意。
