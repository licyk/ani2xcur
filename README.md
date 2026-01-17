# ani2xcur
>[!IMPORTANT]好消息🎉  
>基于 Python 重构的 [Ani2xcur CLI](https://github.com/licyk/ani2xcur-cli) 现已发布，支持 Windows 鼠标指针与 Linux 鼠标指针双向转换，并提供安装、应用和卸载鼠标主题的全套管理功能。
>
>**项目地址**：https://github.com/licyk/ani2xcur-cli


## 简介
一个将 Windows 鼠标指针转换为 Linux 鼠标指针的脚本，基于 GNU 项目的 Dialog 实现显示界面，转换核心基于 win2xcur

## 环境要求
- Python（3.6 ~ 3.11）
- Dialog

> [!NOTE]  
> Python 的版本推荐 3.9，其他版本也可以，可自行测试。这里推荐一些 Python 版本管理器。  
> 1. [Pyenv](https://github.com/pyenv/pyenv)（Windows 系统上使用 [Pyenv-Win](https://github.com/pyenv-win/pyenv-win)）
> 2. [MicroMamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html)
> 3. [MiniConda](https://docs.anaconda.com/free/miniconda/index.html)
>
> 在 Linux 上安装指定版本的 Python 并不方便，所以可以用上面的 Python 版本管理器安装 Python，并在启动 Ani2xcur 时加上`--set-python-path`启动参数来指定 Python 的路径。  
> 具体方法可参考该文档：[《在 Linux 上使用 Python 版本管理器安装 Python》](https://github.com/licyk/README-collection/blob/main/term-sd/README_install_python_on_linux.md)

## 安装
- 1、克隆项目
```sh
git clone https://github.com/licyk/ani2xcur
```

- 2、进入目录并给予执行权限
```sh
cd ani2xcur
chmod +x ani2xcur.sh
```

- 3、创建并进入虚拟环境

> 该步骤为可选步骤

```sh
python3 -m venv venv
source venv/bin/activate
```

- 4、安装 dialog
```sh
# Debian / Ubuntu 系
sudo apt install dialog
```
```sh
# Arch 系
sudo pacman -S dialog
```


- 5、运行
```sh
./ani2xcur.sh
```

## 使用
进入 Ani2xcur 界面后，可以主界面选择 `安装 win2xcur 核心` 安装转换鼠标指针所需的必要核心  

安装核心完成后，可选择 `进入文件浏览器` 进入 Ani2xcur 的文件浏览器来寻找鼠标指针文件，一般 Windows 的鼠标指针文件包含 `cur` / `ani` 格式的文件（鼠标指针图标）和 `inf` 格式的文件（安装鼠标指针的配置文件）  
> 这是 Windows 鼠标指针安装文件的结构
```
咩咩
├── bashi.ani
├── dianliu.ani
├── DJye1.ani
├── DJye2.ani
├── doki.ani
├── help.ani
├── lightning.ani
├── lingdang.ani
├── merry.ani
├── Mye.ani
├── Pye.ani
├── Sye.ani
├── wink.ani
├── woniu.ani
├── yangtuo.ani
└── 右键安装.inf
```

在 Ani2xcur 文件浏览器中选中其中一种格式后即可开始转换，转换好的鼠标指针文件将保存在 Ani2xcur 文件夹中的 `output` 文件夹

Ani2xcur 也支持命令行模式运行（以命令行模式启动时不再检测 Dialog 是否安装），通过启动参数指定 `安装鼠标指针的配置文件` 的路径后即可进行转换  
例如:
```sh
./ani2xcur.sh --inf "/home/licyk/Downloads/咩咩/lingdang.ani"
./ani2xcur.sh --inf "/home/licyk/Downloads/咩咩/右键安装.inf"
```
> 以上命令的执行效果等效

Ani2xcur 支持以下启动参数
```
使用: 
    ./ani2xcur.sh [--help] [--set-python-path python_path] [--win2xcur-path WIN2XCUR_PATH] [--inf inf_file_path] [--win2xcur-args WIN2XCUR_ARGS] [--install-win2xcur] [--remove-win2xcur]

参数:
    --help
        显示 Ani2xcur 启动参数帮助
    --set-python-path python_path
        指定 Python 解释器路径。推荐在 Python 虚拟环境中启动 Ani2xcur, 这将可省去使用启动参数指定 Python 路径
    --win2xcur-path WIN2XCUR_PATH
        指定 win2xcur 的路径
    --inf inf_file_path
        指定 inf 鼠标配置文件路径, 若路径有效, 则 Ani2xcur 将以命令行模式启动, 直接进行鼠标指针转换
    --win2xcur-args WIN2XCUR_ARGS
        调用 win2xcur 执行鼠标指针转换时传入的额外启动参数
        例如需要传入 --scale 0.9 --shadow --shadow-opacity 60 参数, 则使用参数 --win2xcur-args "--scale 0.9 --shadow --shadow-opacity 60" 进行传入
        当使用命令行参数配置 win2xcur 额外启动参数时, 若在 Ani2xcur 设置中配置了 win2xcur 启动参数, 则该设置将被忽略
        win2xcur 可用的额外参数可执行 win2xcur --help 命令进行查看, 或者查看 win2xcur 项目源码: https://github.com/quantum5/win2xcur/blob/master/win2xcur/main/win2xcur.py
    --install-win2xcur
        安装 win2xcur 核心
    --remove-win2xcur
        卸载 win2xcur 核心
```

>[!IMPORTANT]  
>Ani2xcur 使用的 [win2xcur](https://github.com/quantum5/win2xcur) 原项目在 PyPI 上未更新，则使用 Ani2xcur 安装的 win2xcur 会出现部分新增参数不可用，如`--scale`参数（**如果不使用 win2xcur 额外的参数则可忽略该说明**）。解决该问题需要在使用 Ani2xcur 安装 win2xcur 后，退出 Ani2xcur，并使用下面的命令更新 win2xcur：
>
>```bash
>python3 -m pip install git+https://github.com/quantum5/win2xcur --upgrade --force-reinstall
>```
>更新后再重新启动 Ani2xcur 即可正常使用。


## 使用项目

[win2xcur](https://github.com/quantum5/win2xcur) @quantum5 --- 转换核心  
[breeze cursor](https://store.kde.org/p/999927) --- 用作鼠标指针的补全
