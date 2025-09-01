#!/bin/bash

# 为 win2xcur 解析启动参数, 并保存到 WIN2XCUR_ARGS 参数中
# 如果设置 ORIGIN_WIN2XCUR_ARGS 全局变量优先使用该变量中的参数, 否则使用 <Start Path>/win2xcur_args.conf 文件中的参数
parse_win2xcur_args() {
    local char
    local in_quote
    local quote_char
    local current
    local launch_args_string
    local i
    unset WIN2XCUR_ARGS

    if [[ ! -z "${ORIGIN_WIN2XCUR_ARGS}" ]]; then
        launch_args_string=$ORIGIN_WIN2XCUR_ARGS
    elif [[ -f "${START_PATH}/win2xcur_args.conf" ]]; then
        launch_args_string=$(cat "${START_PATH}/win2xcur_args.conf")
    else
        launch_args_string=""
    fi

    for (( i=0; i<${#launch_args_string}; i++ )); do
        char="${launch_args_string:$i:1}"

        # 处理引号逻辑
        if [[ "$char" == \" || "$char" == "'" ]]; then
            if (( in_quote )); then
                if [[ "$char" == "$quote_char" ]]; then  # 结束引号
                    in_quote=0
                    quote_char=""
                    WIN2XCUR_ARGS+=("$current")  # 保存引号内内容
                    current=""
                else  # 其他引号字符作为普通字符
                    current+="$char"
                fi
            else  # 开始引号
                if [[ -n "$current" ]]; then  # 保存引号前的内容
                    WIN2XCUR_ARGS+=("$current")
                    current=""
                fi
                in_quote=1
                quote_char="$char"
            fi
        # 处理空格逻辑
        elif [[ "$char" == " " ]]; then
            if (( in_quote )); then  # 引号内空格保留
                current+="$char"
            else  # 非引号空格作为分隔符
                if [[ -n "$current" ]]; then
                    WIN2XCUR_ARGS+=("$current")
                    current=""
                fi
            fi
        else  # 普通字符累积
            current+="$char"
        fi
    done

    # 处理最后未完成的缓存
    [[ -n "$current" ]] && WIN2XCUR_ARGS+=("$current")
}

win2xcur_args_setting() {
    local dialog_arg
    local launch_args

    if [[ ! -f "${START_PATH}/win2xcur_args.conf" ]]; then
        touch "${START_PATH}/win2xcur_args.conf"
    fi

    while true; do
        launch_args=$(cat "${START_PATH}/win2xcur_args.conf")

        dialog_arg=$(dialog --erase-on-exit --notags \
            --title "Ani2xcur" \
            --backtitle "win2xcur 启动参数选项" \
            --ok-label "确认" --cancel-label "取消" \
            --menu "请选择修改 / 清空 win2xcur 启动参数\n当前 win2xcur 启动参数: ${launch_args}" \
            $(get_dialog_size_menu) \
            "0" "> 返回" \
            "1" "> 修改自定义启动参数" \
            "2" "> 清空 win2xcur 启动参数" \
            3>&1 1>&2 2>&3)

        case "${dialog_arg}" in
            1)
                dialog_arg=$(dialog --erase-on-exit \
                    --title "Ani2xcur" \
                    --backtitle "win2xcur 自定义启动参数选项" \
                    --ok-label "确认" --cancel-label "取消" \
                    --inputbox "请输入 win2xcur 启动参数" \
                    $(get_dialog_size) \
                    "${launch_args}" \
                    3>&1 1>&2 2>&3)

                if [[ "$?" == 0 ]]; then
                    ani_echo "设置 win2xcur 启动参数: ${dialog_arg}"
                    echo "${dialog_arg}" > "${START_PATH}/win2xcur_args.conf"
                else
                    ani_echo "取消修改 win2xcur 启动参数"
                fi
                ;;
            2)
                if (dialog --erase-on-exit \
                    --title "Ani2xcur" \
                    --backtitle "win2xcur 重置启动参数选项" \
                    --yes-label "是" --no-label "否" \
                    --yesno "是否重置 win2xcur 启动参数 ?" \
                    $(get_dialog_size)); then
                    ani_echo "清空 win2xcur 启动参数"
                    echo "" > "${START_PATH}/win2xcur_args.conf"
                else
                    ani_echo "取消清空 win2xcur 参数"
                fi
                ;;
            *)
                break
                ;;
        esac
    done
}
