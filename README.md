# ani2xcur
一个将windows鼠标指针转换为linux鼠标指针的脚本，拥有TUI界面，转换核心基于win2xcur
使用前需要安装python，aria2，dialog

## 使用方法：

下载ani2xcur

    aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/ani2xcur.sh &&chmod +x ani2xcur.sh

如果下载失败可以使用代理站下载

    aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/ani2xcur.sh &&chmod +x ani2xcur.sh

运行ani2xcur

    ./ani2xcur.sh

# ani2xcur-core
这个是ani2xcur的核心版本，去掉了dialog,只保留基本的转换功能

## 使用方法：

下载ani2xcur-core

    aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/ani2xcur-core.sh &&chmod +x ani2xcur-core.sh

如果下载失败可以使用代理站下载

    aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/ani2xcur-core.sh &&chmod +x ani2xcur-core.sh

将ani2xcur-core脚本和鼠标指针放在一起(所在目录要有.inf文件)，运行

    ./ani2xcur-core.sh

# 使用项目

[win2xcur](https://github.com/quantum5/win2xcur)@quantum5  --- 转换核心  
[breeze cursor](https://store.kde.org/p/999927)   --- 用作鼠标指针的补全