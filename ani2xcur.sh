#!/bin/bash

# 格式化信息输出
ani_echo()
{
    echo -e "[\033[33m$(date "+%Y-%m-%d %H:%M:%S")\033[0m]\033\033[36m::\033[0m "$@""
}

# 终端横线显示功能
ani_print_line()
{
    local shellwidth
    local print_word_to_shell
    local shell_word_width
    local shell_word_width_zh_cn
    local print_line_info
    local print_word_info
    local print_mode

    if [ -z "$@" ];then # 输出方法选择
        print_mode=1
    else
        shellwidth=$ani_shell_width # 获取终端宽度
        print_word_to_shell=$(echo "$@" | awk '{gsub(/ /,"-")}1') # 将空格转换为"-"
        shell_word_width=$(( $(echo "$print_word_to_shell" | wc -c) - 1 )) # 总共的字符长度
        shell_word_width_zh_cn=$(( $(echo "$print_word_to_shell" | awk '{gsub(/[a-zA-Z]/,"") ; gsub(/[0-9]/, "") ; gsub(/[=+()（）、。,./\-_\\]/, "")}1' | wc -c) - 1 )) # 计算中文字符的长度
        shell_word_width=$(( $shell_word_width - $shell_word_width_zh_cn )) # 除去中文之后的长度
        # 中文的字符长度为3,但终端中只占2个字符位
        shell_word_width_zh_cn=$(( $shell_word_width_zh_cn / 3 * 2 )) # 转换中文在终端占用的实际字符长度
        shell_word_width=$(( $shell_word_width + $shell_word_width_zh_cn )) # 最终显示文字的长度

        # 横线输出长度的计算
        shellwidth=$(( ($shellwidth - $shell_word_width) / 2 )) # 除去输出字符后的横线宽度

        # 判断终端宽度大小是否是单双数
        print_line_info=$(( $shellwidth % 2 ))
        # 判断字符宽度大小是否是单双数
        print_word_info=$(( $shell_word_width % 2 ))
        
        case $print_line_info in
            0) # 如果终端宽度大小是双数
                case $print_word_info in
                    0) # 如果字符宽度大小是双数
                        print_mode=2
                        ;;
                    1) # 如果字符宽度大小是单数
                        print_mode=3
                        ;;
                esac
                ;;
            1) # 如果终端宽度大小是单数数
                case $print_word_info in
                    0) # 如果字符宽度大小是双数
                        print_mode=2
                        ;;
                    1) # 如果字符宽度大小是单数
                        print_mode=3
                        ;;
                esac
                ;;
        esac
    fi

    # 输出
    case $print_mode in
        1)
            shellwidth=$ani_shell_width # 获取终端宽度
            yes "-" | sed $shellwidth'q' | tr -d '\n' # 输出横杠
            ;;
        2) # 解决显示字符为单数时少显示一个字符导致不对成的问题
            echo "$(yes "-" | sed $shellwidth'q' | tr -d '\n')"$@"$(yes "-" | sed $shellwidth'q' | tr -d '\n')"
            ;;
        3)
            echo "$(yes "-" | sed $shellwidth'q' | tr -d '\n')"$@"$(yes "-" | sed $(( $shellwidth + 1 ))'q' | tr -d '\n')"
            ;;
    esac
}

# 启动参数处理
ani_launch_args_manager()
{
    local ani_launch_args_input
    local ani_launch_args
    local i

    # 用别的方法实现了getopt命令的功能
    # 加一个--null是为了增加一次循环,保证那些需要参数的选项能成功执行
    for i in "$@" "--null" ;do
        ani_launch_args=$i # 用作判断是参数还是选项

        # 参数检测部分
        if [ ! -z $ani_launch_args_input ];then
            if [ "$(ani_test_args "$ani_launch_args")" = 0 ];then # 测试输入值是参数还是选项
                ani_launch_args= # 检测到选项的下一项是选项,直接清除
            fi

            # 检测输入的选项
            case $ani_launch_args_input in
                --set-python-path)
                    set_python_path $ani_launch_args
                    ;;
                --inf)
                    set_inf_file_path $ani_launch_args
                    ;;
            esac
            ani_launch_args_input= # 清除选项,留给下一次判断
        fi

        ####################

        # 选项检测部分(如果选项要跟参数值,则将启动选项赋值给ani_launch_args_input)
        case $i in
            --help)
                ani_print_line
                ani_args_help
                ani_print_line
                exit 1
                ;;
            --set-python-path)
                ani_launch_args_input="--set-python-path"
                ;;
            --inf)
                ani_launch_args_input="--inf"
                ;;
            *)
                ani_unknown_args_echo $i
                ;;
        esac

    done
}

# 启动参数帮助
ani_args_help()
{
    cat<<EOF
    使用: 
        ./ani2xcur.sh --help [--set-python-path python_path] [--inf inf_file_path]
    
    参数:
        --help
            显示 Ani2xcur 启动参数帮助
        --set-python-path python_path
            指定 Python 解释器路径。推荐在 Python 虚拟环境中启动 Ani2xcur, 这将可省去使用启动参数指定 Python 路径
        --inf inf_file_path
            指定 inf 鼠标配置文件路径, 若路径有效, 则 Ani2xcur 将以命令行模式启动, 直接进行鼠标指针转换
EOF
}

# 设置python解释器路径
set_python_path()
{
    if [ -z "$*" ];then
        ani_echo "输入 Python 解释器路径为空"
        ani_echo "使用系统默认 Python"
    else
        ani_echo "设置 Python 解释器路径: $@"
        ani_python_path=$@
    fi
}

# 设置鼠标指针配置文件路径
set_inf_file_path()
{
    if [ -z "$*" ];then
        ani_echo "inf 鼠标指针配置文件路径为空"
    else
        if [ -f "$@" ];then
            ani_echo "指定 inf 鼠标指针配置文件路径: $@"
            inf_file_path=$@
        else
            ani_echo "inf 鼠标指针配置文件路径无效"
        fi
    fi
}

# 测试输入值是参数还是选项,选项输出0,参数输出1(用于实现getopt命令的功能)
ani_test_args()
{
    echo $@ | awk '{for (i=1; i<=NF; i++) {if (substr($i, 1, 2) == "--") {print "0"} else {print "1"}}}'
}

# 提示未知启动参数
ani_unknown_args_echo()
{
    if [ "$(ani_test_args "$@")" = 0 ] && [ ! "$@" = "--null" ];then # 测试输入值是参数还是选项
        ani_echo "未知参数: \"$@\""
    fi
}

# 主程序
main()
{
    local cli_mode=1
    local missing_depend_info=0
    local missing_depend
    start_path=$(pwd)
    ani_shell_width=$(stty size | awk '{print $2}') # 获取终端宽度
    ani_shell_height=$(stty size | awk '{print $1}') # 获取终端高度
    #文件后缀设置
    file_format_1="inf"
    file_format_2="ani"
    file_format_3="cur"
    use_custom_python_path=1
    # pip镜像源设置
    export PIP_INDEX_URL="https://mirrors.cloud.tencent.com/pypi/simple"
    export PIP_EXTRA_INDEX_URL="https://mirror.baidu.com/pypi/simple https://mirrors.bfsu.edu.cn/pypi/web/simple https://mirror.nju.edu.cn/pypi/web/simple"
    # 设置dialog界面的大小
    export ani_dialog_menu_height=10 #dialog高度条目

    if [ $(( $ani_shell_width -20 )) -le 12 ];then # dialog宽度
        export ani_dialog_width=-1
    else
        export ani_dialog_width=$(( $ani_shell_width -20 ))
    fi

    if [ $(( $ani_shell_height - 6 )) -le 6 ];then # dialog高度
        export ani_dialog_height=-1
    else
        export ani_dialog_height=$(( $ani_shell_height - 6 ))
    fi

    # 创建输出文件夹
    mkdir -p "$start_path"/output
    mkdir -p "$start_path"/task

    # 启动参数处理
    ani_launch_args_manager "$@"

    # 依赖检查
    if [ -z "$ani_python_path" ];then
        if python3 --version > /dev/null 2>&1 || python --version > /dev/null 2>&1 ;then # 判断是否有可用的python
            if [ ! -z "$(python3 --version 2> /dev/null)" ];then
                export ani_python_path=$(which python3)
            elif [ ! -z "$(python --version 2> /dev/null)" ];then
                export ani_python_path=$(which python)
            fi
        else
            missing_depend_info=1
            missing_depend="$missing_depend python,"
        fi
    else
        if which "$ani_python_path" > /dev/null 2>&1 ;then
            ani_echo "使用自定义 Python 解释器路径: $ani_python_path"
            use_custom_python_path=0
        else
            missing_depend_info=1
            missing_depend="$missing_depend python,"
        fi
    fi

    if [ -z "$inf_file_path" ];then # 未指定inf文件路径
        if ! which dialog > /dev/null 2>&1; then
            missing_depend_info=1
            missing_depend="$missing_depend dialog,"
        fi
    else
        if [ "$inf_file_path" = *.inf ];then
            ani_echo "以命令行模式启动 Ani2xcur"
        else
            ani_echo "寻找 inf 鼠标指针配置文件"
            inf_file_path="$(dirname "$inf_file_path")/$(ls -a "$(dirname "$inf_file_path")" | grep \.inf$ | awk 'NR==1')"
            ani_echo "以命令行模式启动 Ani2xcur"
        fi
        cli_mode=0
    fi

    if [ $missing_depend_info = 0 ];then
        . ./modules/init.sh
    else
        ani_echo "缺失依赖"
        ani_print_line
        echo $missing_depend
        ani_print_line
        ani_echo "请安装以上依赖后重试"
        ani_echo "退出 Ani2xcur"
    fi
}


###############


# 运行目录检查
if && [ ! -d ".git" ] && [ ! -d "modules" ] && [ ! -f "modules/init.sh" ] && [ ! -d "source" ];then
    ani_echo "检测到目录错误"
    ani_echo "请进入 Ani2xcur 目录里再运行 Ani2xcur"
    ani_echo "退出 Ani2xcur"
    exit 1
elif [ ! "$(dirname "$(echo $0)")" = "." ];then
    ani_echo "检测到未在 ani2xcur.sh 文件所在目录运行 Ani2xcur"
    ani_echo "请进入 ani2xcur.sh 文件所在目录后再次运行 Ani2xcur"
    ani_echo "退出 Ani2xcur"
    exit 1
fi

main "$@"