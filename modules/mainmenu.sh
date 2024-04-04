#!/bin/bash

# 主界面
mainmenu()
{
    local mainmenu_dialog

    while true
    do
        cd "$start_path"

        mainmenu_dialog=$(dialog --erase-on-exit --notags \
        --title "Ani2xcur" \
        --backtitle "主界面" \
        --ok-label "确认" --cancel-label "退出" \
        --menu "请选择 Ani2xcur 的功能\n当前 Win2xcur 安装状态: $(which win2xcur > /dev/null 2>&1 && echo "已安装" || echo "未安装")\n当前使用 Python : $([ $use_custom_python_path = 0 ] && echo $ani_python_path || [ ! -z "$VIRTUAL_ENV" ] && echo "虚拟环境" || echo "系统环境")" \
        $ani_dialog_height $ani_dialog_width $ani_dialog_menu_height \
        "1" "> 更新 Ani2xcur" \
        "2" "> 安装 win2xcur 核心" \
        "3" "> 卸载 win2xcur 核心" \
        "4" "> 进入文件浏览器" \
        "5" "> 退出 Ani2xcur" \
        3>&1 1>&2 2>&3)

        case $mainmenu_dialog in
            1)
                ani_echo "更新 Ani2xcur 中"
                git pull
                if [ $? = 0 ];then
                    chmod +x ani2xcur.sh
                    dialog --erase-on-exit \
                    --title "Ani2xcur" \
                    --backtitle "Ani2xcur 更新选项" \
                    --ok-label "确认" \
                    --msgbox "Ani2xcur 更新成功" $ani_dialog_height $ani_dialog_width
                    . ./ani2xcur.sh
                else
                    dialog --erase-on-exit \
                    --title "Ani2xcur" \
                    --backtitle "Ani2xcur 更新选项" \
                    --ok-label "确认" \
                    --msgbox "Ani2xcur 更新成功" $ani_dialog_height $ani_dialog_width
                fi
                ;;
            2)
                ani_echo "安装 wi2n2xcur 中"
                if which win2xcur > /dev/null 2>&1; then
                    ani_pip install numpy wand win2xcur --upgrade --force-reinstall
                else
                    ani_pip install numpy wand win2xcur --upgrade
                fi
                if [ $? = 0 ];then
                    dialog --erase-on-exit \
                    --title "Ani2xcur" \
                    --backtitle "win2xcur 安装选项" \
                    --ok-label "确认" \
                    --msgbox "win2xcur 安装成功" $ani_dialog_height $ani_dialog_width
                else
                    dialog --erase-on-exit \
                    --title "Ani2xcur" \
                    --backtitle "win2xcur 安装选项" \
                    --ok-label "确认" \
                    --msgbox "win2xcur 安装失败" $ani_dialog_height $ani_dialog_width
                fi
                ;;
            3)
                ani_echo "卸载 wi2n2xcur 中"
                ani_pip uninstall win2xcur -y
                if [ $? = 0 ];then
                    dialog --erase-on-exit \
                    --title "Ani2xcur" \
                    --backtitle "win2xcur 卸载选项" \
                    --ok-label "确认" \
                    --msgbox "win2xcur 卸载成功" $ani_dialog_height $ani_dialog_width
                else
                    dialog --erase-on-exit \
                    --title "Ani2xcur" \
                    --backtitle "win2xcur 卸载选项" \
                    --ok-label "确认" \
                    --msgbox "win2xcur 卸载失败" $ani_dialog_height $ani_dialog_width
                fi
                ;;
            4)
                if which win2xcur > /dev/null 2>&1 ;then
                    cd ..
                    file_browser
                else
                    dialog --erase-on-exit \
                    --title "Ani2xcur" \
                    --backtitle "文件浏览器" \
                    --ok-label "确认" \
                    --msgbox "win2xcur 核心未安装, 请安装后重试" $ani_dialog_height $ani_dialog_width
                fi
                ;;
            *)
                break
                ;;
        esac
    done
}