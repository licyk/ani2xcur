#!/bin/bash

# 主界面
mainmenu() {
    local dialog_arg
    local win2xcur_status

    while true; do
        cd "${START_PATH}"

        if which "${WIN2XCUR_PATH}" &> /dev/null; then
            win2xcur_status="已安装"
        else
            win2xcur_status="未安装"
        fi

        dialog_arg=$(dialog --erase-on-exit --notags \
            --title "Ani2xcur" \
            --backtitle "主界面" \
            --ok-label "确认" --cancel-label "退出" \
            --menu "请选择 Ani2xcur 的功能\n当前 win2xcur 安装状态: ${win2xcur_status}\n当前使用 Python: ${ANI_PYTHON_PATH}\n当前 Ani2xcur 版本: ${ANI2XCUR_VER}" \
            $(get_dialog_size_menu) \
            "1" "> 更新 Ani2xcur" \
            "2" "> 安装 win2xcur 核心" \
            "3" "> 卸载 win2xcur 核心" \
            "4" "> 进入文件浏览器" \
            "5" "> 退出 Ani2xcur" \
            3>&1 1>&2 2>&3)

        case "${dialog_arg}" in
            1)
                if update_ani2xcur; then
                    chmod +x ani2xcur.sh
                    dialog --erase-on-exit \
                        --title "Ani2xcur" \
                        --backtitle "Ani2xcur 更新选项" \
                        --ok-label "确认" \
                        --msgbox "Ani2xcur 更新成功" \
                        $(get_dialog_size)

                    . "${START_PATH}/ani2xcur.sh"
                else
                    dialog --erase-on-exit \
                        --title "Ani2xcur" \
                        --backtitle "Ani2xcur 更新选项" \
                        --ok-label "确认" \
                        --msgbox "Ani2xcur 更新失败" \
                        $(get_dialog_size)
                fi
                ;;
            2)
                ani_echo "安装 wi2n2xcur 中"
                if which "${WIN2XCUR_PATH}" &> /dev/null; then
                    ani_pip install numpy wand win2xcur --upgrade --force-reinstall
                else
                    ani_pip install numpy wand win2xcur --upgrade
                fi
                if [[ "$?" == 0 ]]; then
                    dialog --erase-on-exit \
                        --title "Ani2xcur" \
                        --backtitle "win2xcur 安装选项" \
                        --ok-label "确认" \
                        --msgbox "win2xcur 安装成功" \
                        $(get_dialog_size)
                else
                    dialog --erase-on-exit \
                        --title "Ani2xcur" \
                        --backtitle "win2xcur 安装选项" \
                        --ok-label "确认" \
                        --msgbox "win2xcur 安装失败" \
                        $(get_dialog_size)
                fi
                ;;
            3)
                ani_echo "卸载 wi2n2xcur 中"
                ani_pip uninstall win2xcur -y
                if [[ "$?" == 0 ]]; then
                    dialog --erase-on-exit \
                        --title "Ani2xcur" \
                        --backtitle "win2xcur 卸载选项" \
                        --ok-label "确认" \
                        --msgbox "win2xcur 卸载成功" \
                        $(get_dialog_size)
                else
                    dialog --erase-on-exit \
                        --title "Ani2xcur" \
                        --backtitle "win2xcur 卸载选项" \
                        --ok-label "确认" \
                        --msgbox "win2xcur 卸载失败" \
                        $(get_dialog_size)
                fi
                ;;
            4)
                if which "${WIN2XCUR_PATH}" &> /dev/null; then
                    cd ..
                    file_browser
                else
                    dialog --erase-on-exit \
                        --title "Ani2xcur" \
                        --backtitle "文件浏览器" \
                        --ok-label "确认" \
                        --msgbox "win2xcur 核心未安装, 请安装后重试" \
                        $(get_dialog_size)
                fi
                ;;
            *)
                ani_echo "退出 Ani2xcur"
                exit 0
                ;;
        esac
    done
}
