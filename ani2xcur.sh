#!/bin/bash

# 格式化信息输出
ani_echo() {
    echo -e "[\033[33m$(date "+%Y-%m-%d %H:%M:%S")\033[0m][\033[36mAni2xcur\033[0m]\033\033[36m::\033[0m $@"
}

# 终端横线显示功能
ani_print_line() {
    local shell_width
    local input_text
    local input_text_length
    local input_zh_text_length
    local shell_width_info
    local text_length_info
    local print_mode

    if [[ -z "$@" ]]; then # 输出方法选择
        print_mode=1
    else
        shell_width=$SHELL_WIDTH # 获取终端宽度
        input_text=$(echo "$@" | awk '{gsub(/ /,"-")}1') # 将空格转换为"-"
        input_text_length=$(( $(echo "${input_text}" | wc -c) - 1 )) # 总共的字符长度
        input_zh_text_length=$(( $(echo "${input_text}" | awk '{gsub(/[a-zA-Z]/,"") ; gsub(/[0-9]/, "") ; gsub(/[=+()（）、。,./\-_\\]/, "")}1' | wc -c) - 1 )) # 计算中文字符的长度
        input_text_length=$(( input_text_length - input_zh_text_length )) # 除去中文之后的长度
        # 中文的字符长度为3,但终端中只占2个字符位
        input_zh_text_length=$(( input_zh_text_length / 3 * 2 )) # 转换中文在终端占用的实际字符长度
        input_text_length=$(( input_text_length + input_zh_text_length )) # 最终显示文字的长度

        # 横线输出长度的计算
        shell_width=$(( (shell_width - input_text_length) / 2 )) # 除去输出字符后的横线宽度

        # 判断终端宽度大小是否是单双数
        shell_width_info=$(( shell_width % 2 ))
        # 判断字符宽度大小是否是单双数
        text_length_info=$(( input_text_length % 2 ))
        
        case "${shell_width_info}" in
            0)
                # 如果终端宽度大小是双数
                case "${text_length_info}" in
                    0) 
                        # 如果字符宽度大小是双数
                        print_mode=2
                        ;;
                    1)
                        # 如果字符宽度大小是单数
                        print_mode=3
                        ;;
                esac
                ;;
            1)
                # 如果终端宽度大小是单数数
                case "${text_length_info}" in
                    0)
                        # 如果字符宽度大小是双数
                        print_mode=2
                        ;;
                    1)
                        # 如果字符宽度大小是单数
                        print_mode=3
                        ;;
                esac
                ;;
        esac
    fi

    # 输出
    case "${print_mode}" in
        1)
            shell_width=$SHELL_WIDTH # 获取终端宽度
            yes "-" | sed $shell_width'q' | tr -d '\n' # 输出横杠
            ;;
        2)
            # 解决显示字符为单数时少显示一个字符导致不对成的问题
            echo "$(yes "-" | sed "${shell_width}"'q' | tr -d '\n')"$@"$(yes "-" | sed "${shell_width}"'q' | tr -d '\n')"
            ;;
        3)
            echo "$(yes "-" | sed "${shell_width}"'q' | tr -d '\n')"$@"$(yes "-" | sed $(( shell_width + 1 ))'q' | tr -d '\n')"
            ;;
    esac
}

# 启动参数处理
ani_launch_args_manager() {
    local ani_launch_args_input
    local ani_launch_args
    local i

    # 用别的方法实现了getopt命令的功能
    # 加一个--null是为了增加一次循环,保证那些需要参数的选项能成功执行
    for i in "$@" "--null"; do
        ani_launch_args=$i # 用作判断是参数还是选项

        # 参数检测部分
        if [[ ! -z "${ani_launch_args_input}" ]]; then
            if ani_is_arg "${ani_launch_args}"; then # 测试输入值是参数还是选项
                unset ani_launch_args # 检测到选项的下一项是选项, 直接清除
            fi

            # 检测输入的选项
            case "${ani_launch_args_input}" in
                --set-python-path)
                    set_python_path "${ani_launch_args}"
                    ;;
                --inf)
                    set_inf_file_path "${ani_launch_args}"
                    ;;
                --win2xcur-path)
                    set_win2xcur_path "${ani_launch_args}"
                    ;;
            esac
            unset ani_launch_args_input # 清除选项, 留给下一次判断
        fi

        ####################

        # 选项检测部分(如果选项要跟参数值, 则将启动选项赋值给 ani_launch_args_input)
        case "${i}" in
            --help)
                ani_print_line
                ani_args_help
                ani_print_line
                exit 1
                ;;
            --set-python-path)
                ani_launch_args_input="--set-python-path"
                ;;
            --win2xcur-path)
                ani_launch_args_input="--win2xcur-path"
                ;;
            --inf)
                ani_launch_args_input="--inf"
                ;;
            --install-win2xcur)
                INSTALL_WIN2XCUR=1
                ;;
            --remove-win2xcur)
                INSTALL_WIN2XCUR=2
                ;;
            *)
                ani_unknown_args_echo "${i}"
                ;;
        esac

    done
}

# 启动参数帮助
ani_args_help() {
    cat<<EOF
    使用: 
        ./ani2xcur.sh [--help] [--set-python-path python_path] [--win2xcur-path WIN2XCUR_PATH] [--inf inf_file_path] [--install-win2xcur] [--remove-win2xcur]

    参数:
        --help
            显示 Ani2xcur 启动参数帮助
        --set-python-path python_path
            指定 Python 解释器路径。推荐在 Python 虚拟环境中启动 Ani2xcur, 这将可省去使用启动参数指定 Python 路径
        --win2xcur-path WIN2XCUR_PATH
            指定 win2xcur 的路径
        --inf inf_file_path
            指定 inf 鼠标配置文件路径, 若路径有效, 则 Ani2xcur 将以命令行模式启动, 直接进行鼠标指针转换
        --install-win2xcur
            安装 win2xcur 核心
        --remove-win2xcur
            卸载 win2xcur 核心
EOF
}

# 设置python解释器路径
set_python_path() {
    if [[ -z "$@" ]]; then
        ani_echo "输入 Python 解释器路径为空"
        ani_echo "使用系统默认 Python"
        sleep 3
    else
        ani_echo "设置 Python 解释器路径: $@"
        ANI_PYTHON_PATH=$@
    fi
}

# 设置鼠标指针配置文件路径
set_inf_file_path() {
    if [[ -z "$@" ]]; then
        ani_echo "inf 鼠标指针配置文件路径为空"
        ani_echo "取消使用命令行模式, 将启动 Ani2xcur 界面"
        sleep 3
    else
        if [[ -f "$@" ]]; then
            ani_echo "指定 inf 鼠标指针配置文件路径: $@"
            INF_FILE_PATH=$@
        else
            ani_echo "inf 鼠标指针配置文件路径无效"
            ani_echo "取消使用命令行模式, 将启动 Ani2xcur 界面"
            sleep 3
        fi
    fi
}

# 设置 win2xcur 路径
set_win2xcur_path() {
    if [[ -z "$@" ]]; then
        ani_echo "win2xcur 路径为空"
        ani_echo "将使用默认值"
        WIN2XCUR_PATH="win2xcur"
        sleep 3
    elif which "$@" &> /dev/null; then
        ani_echo "使用自定义 win2xcur 路径: $@"
        WIN2XCUR_PATH=$@
    else
        ani_echo "win2xcur 路径无效"
        ani_echo "将使用默认值"
        WIN2XCUR_PATH="win2xcur"
        sleep 3
    fi
}

# 测试输入值是参数还是选项, 是选项返回 0, 是参数返回 1 (用于实现 getopt 命令的功能)
ani_is_arg() {
    local result

    result=$(awk '{for (i = 1; i <= NF; i++) {if (substr($i, 1, 2) == "--") {print "0"} else {print "1"}}}' <<< $@)

    if [[ "${result}" == 0 ]]; then
        return 0
    else
        return 1
    fi
}

# 提示未知启动参数
ani_unknown_args_echo() {
    if ani_is_arg "$@" && [[ ! "$@" = "--null" ]]; then # 测试输入值是参数还是选项
        ani_echo "未知参数: \"$@\""
    fi
}

# 获取 Dialog 的宽高度
get_dialog_size() {
    echo "${DIALOG_HEIGHT}" "${DIALOG_WIDTH}"
}

# 获取 Dialog 的宽高度(附带 Dialog 菜单高度)
get_dialog_size_menu() {
    echo "${DIALOG_HEIGHT}" "${DIALOG_WIDTH}" "${DIALOG_MENU_HEIGHT}"
}

# 主程序
main() {
    ani_echo "初始化 Ani2xcur 中"
    # 运行目录检查
    if [[ ! -d "modules" ]] && [[ ! -f "modules/init.sh" ]] && [[ ! -d "source" ]]; then
        ani_echo "检测到目录错误"
        ani_echo "请进入 Ani2xcur 目录里再运行 Ani2xcur"
        ani_echo "退出 Ani2xcur"
        exit 1
    elif [ ! "$(dirname "$(echo $0)")" = "." ]; then
        ani_echo "检测到未在 ani2xcur.sh 文件所在目录运行 Ani2xcur"
        ani_echo "请进入 ani2xcur.sh 文件所在目录后再次运行 Ani2xcur"
        ani_echo "退出 Ani2xcur"
        exit 1
    fi

    ANI2XCUR_VER="0.0.5"
    CLI_MODE=0
    local missing_depend_info=0
    local missing_depend
    local i
    START_PATH=$(pwd)
    SHELL_WIDTH=$(stty size | awk '{print $2}') # 获取终端宽度
    SHELL_HEIGHT=$(stty size | awk '{print $1}') # 获取终端高度
    INSTALL_WIN2XCUR=0
    # Pip 镜像源设置
    export PIP_INDEX_URL="https://mirrors.cloud.tencent.com/pypi/simple"
    export PIP_EXTRA_INDEX_URL="https://mirror.baidu.com/pypi/simple"
    export PIP_DISABLE_PIP_VERSION_CHECK=1
    # 设置 Dialog 界面的大小
    DIALOG_MENU_HEIGHT=10 # Dialog 列表高度

    if [ $(( SHELL_WIDTH -20 )) -le 12 ]; then # Dialog 宽度
        DIALOG_WIDTH=-1
    else
        DIALOG_WIDTH=$(( SHELL_WIDTH - 20 ))
    fi

    if [ $(( SHELL_HEIGHT - 6 )) -le 6 ]; then # Dialog 高度
        DIALOG_HEIGHT=-1
    else
        DIALOG_HEIGHT=$(( SHELL_HEIGHT - 6 ))
    fi

    # 创建输出文件夹
    mkdir -p "${START_PATH}"/output
    mkdir -p "${START_PATH}"/task

    # 启动参数处理
    ani_launch_args_manager "$@"

    # 依赖检查
    ani_echo "检测依赖中"
    if [[ -z "${ANI_PYTHON_PATH}" ]]; then
        if python3 --version &> /dev/null || python --version &> /dev/null; then # 判断是否有可用的 Python
            if [[ ! -z "$(python --version 2> /dev/null)" ]]; then
                ANI_PYTHON_PATH=$(which python)
            elif [[ ! -z "$(python3 --version 2> /dev/null)" ]]; then
                ANI_PYTHON_PATH=$(which python3)
            fi
        else
            missing_depend_info=1
            missing_depend="${missing_depend} python,"
        fi
    else
        if which "${ANI_PYTHON_PATH}" &> /dev/null; then
            ani_echo "使用自定义 Python 解释器路径: ${ANI_PYTHON_PATH}"
        else
            missing_depend_info=1
            missing_depend="${missing_depend} python,"
        fi
    fi

    # 检测可用的 Pip 命令
    if [[ ! -z "${VIRTUAL_ENV}" ]]; then
        if [[ ! -z "$(python --version 2> /dev/null)" ]]; then
            if ! python -c "import pip" &> /dev/null; then
                missing_depend_info=1
                missing_depend="${missing_depend} pip,"
            fi
        elif [[ ! -z "$(python3 --version 2> /dev/null)" ]]; then
            if ! python3 -c "import pip" &> /dev/null; then
                missing_depend_info=1
                missing_depend="${missing_depend} pip,"
            fi
        fi
    else
        if ! "${ANI_PYTHON_PATH}" -c "import pip" &> /dev/null; then
            missing_depend_info=1
            missing_depend="${missing_depend} pip,"
        fi
    fi

    # 检测自定义 Win2xcur 路径
    if [[ -z "${WIN2XCUR_PATH}" ]]; then
        WIN2XCUR_PATH="win2xcur"
    elif ! which "${WIN2XCUR_PATH}" &> /dev/null; then
        WIN2XCUR_PATH="win2xcur"
    fi

    if [[ -z "${INF_FILE_PATH}" ]]; then # 未指定 inf 文件路径, 则检查启动图形界面所需的依赖
        if ! which dialog &> /dev/null; then
            missing_depend_info=1
            missing_depend="$missing_depend dialog,"
        fi
    else
        if [[ "${INF_FILE_PATH}" = *.inf ]]; then
            ani_echo "以命令行模式启动 Ani2xcur"
        else
            ani_echo "寻找 inf 鼠标指针配置文件"
            INF_FILE_PATH="$(dirname "${INF_FILE_PATH}")/$(ls -a "$(dirname "${INF_FILE_PATH}")" | grep \.inf$ | awk 'NR==1')"
            ani_echo "inf 鼠标指针配置文件路径: ${INF_FILE_PATH}"
            ani_echo "以命令行模式启动 Ani2xcur"
        fi
        CLI_MODE=1
    fi

    if [[ "${missing_depend_info}" == 0 ]]; then
        . ./modules/init.sh
    else
        ani_echo "缺失依赖"
        ani_print_line
        for i in ${missing_depend}; do
            echo "${i}"
        done
        ani_print_line
        ani_echo "请安装以上依赖后重试"
        ani_echo "退出 Ani2xcur"
	exit 1
    fi

    # 安装 win2xcur
    case "${INSTALL_WIN2XCUR}" in
        1)
            ani_echo "安装 wi2n2xcur 中"
            if which win2xcur &> /dev/null; then
                ani_pip install numpy wand win2xcur --upgrade --force-reinstall
            else
                ani_pip install numpy wand win2xcur --upgrade
            fi
            if [[ "$?" == 0 ]]; then
                ani_echo "win2xcur 核心安装成功"
            else
                ani_echo "win2xcur 核心安装成功"
            fi
            ;;
        2)
            ani_echo "卸载 wi2n2xcur 中"
            ani_pip uninstall win2xcur -y
            if [[ "$?" == 0 ]]; then
                ani_echo "win2xcur 核心卸载成功"
            else
                ani_echo "win2xcur 核心卸载成功"
            fi
            ;;
    esac

    # 启动
    if [ "${CLI_MODE}" == 1 ]; then
        ani_echo "启动转换"
        ani_win2xcur_start "${INF_FILE_PATH}"
        ani_echo "转换完成"
        ani_echo "退出 Ani2xcur"
    else
        mainmenu
    fi
}

main "$@"
