#!/bin/bash

# 文件浏览器
file_browser()
{
    local file_select

    while true
    do
        # 界面显示
        if [ "$(pwd)" = "/" ];then
            file_select=$(dialog --erase-on-exit \
                --title "Ani2xcur" \
                --backtitle "文件浏览器" \
                --menu "使用方向键和回车键进行选择\n注:\n1、名称后面带有\"/\"的是文件夹\n2、文件和文件夹按时间排序, 最新的排在前面\n当前路径: $(pwd)" \
                $ani_dialog_height $ani_dialog_width $ani_dialog_menu_height \
                "-->返回主界面" "X" \
                $(ls -lhFt --time-style=+"%Y-%m-%d" | awk -F ' ' ' {print $7 " " $5 } ') \
                3>&1 1>&2 2>&3)
        else
            file_select=$(dialog --erase-on-exit \
                --title "Ani2xcur" \
                --backtitle "文件浏览器" \
                --menu "使用方向键和回车键进行选择\n注:\n1、名称后面带有\"/\"的是文件夹\n2、文件和文件夹按时间排序, 最新的排在前面\n当前路径: $(pwd)" \
                $ani_dialog_height $ani_dialog_width $ani_dialog_menu_height \
                "-->返回上一个目录" "X" \
                "-->返回主界面" "X" \
                $(ls -lhFt --time-style=+"%Y-%m-%d" | awk -F ' ' ' {print $7 " " $5 } ') \
                3>&1 1>&2 2>&3)
        fi

        # 选择判断
        if [ $? = 0 ];then
            if [ $file_select = "-->返回上一个目录" ];then #选择返回上一个目录
                cd ..
            elif [ $file_select = "-->返回主界面" ];then
                break
            elif [ -d "$file_select" ];then # 选择的是目录
                cd $file_select
                continue
            elif [[ -f $file_select ]];then # 选择的是文件
                case $file_select in
                    *.$file_format_1) # 选择的文件是指定格式
                        ani_win2xcur_start "$(pwd)/$file_select"
                        dialog --erase-on-exit \
                            --title "Ani2xcur" \
                            --backtitle "鼠标指针转换结果" \
                            --ok-label "确认" \
                            --msgbox "鼠标指针转换完成, 可在 ${start_path}/output/${exec_time} 文件夹中查看" $ani_dialog_height $ani_dialog_width
                        ;;
                    *.$file_format_2|*.$file_format_3) # 选择的文件是指定格式
                        ani_win2xcur_start "$(pwd)/$(ls -a | grep \.inf$ | awk 'NR==1')"
                        dialog --erase-on-exit \
                            --title "Ani2xcur" \
                            --backtitle "鼠标指针转换结果" \
                            --ok-label "确认" \
                            --msgbox "鼠标指针转换完成, 可在 ${start_path}/output/${exec_time} 文件夹中查看" $ani_dialog_height $ani_dialog_width
                        ;;
                    *.zip|*.7z) # 文件解压缩功能，暂不支持自动检测编码，所以默认使用系统编码，如果压缩包是在windows系统中制作的，有可能会出现乱码
                        7z x "$file_select"
                        ;;
                    *.rar)
                        unrar x "$file_select"
                        ;;
                    *.tar|*.tar.Z|*.tar.lz|*.tar.lzma|*.tar.lzo)
                        tar xvf "$file_select"
                        ;;
                    *.tar.bz2)
                        tar xvjf "$file_select"
                        ;;
                    *.tar.7z)
                        7z e -so "$file_select" | tar xvf -
                        ;;
                    *.tar.gz)
                        tar xvzf "$file_select"
                        ;;
                    *.tar.xz)
                        tar xvJf "$file_select"
                        ;;
                    *.tar.zst)
                        tar -I zstd -xvf "$file_select"
                        ;;
                    *) # 不是脚本指定的格式
                        dialog --erase-on-exit \
                        --title "文件管理" \
                        --backtitle "文件浏览器" \
                        --msgbox "文件格式错误, 请选择以 inf 后缀或 ani 后缀的文件" \
                        $ani_dialog_height $ani_dialog_width
                        ;;
                esac
            else 
                dialog --erase-on-exit \
                --title "文件管理" \
                --backtitle "文件浏览器" \
                --msgbox "打开路径失败, 可能是文件夹名称包含空格, 或者是文件名包括空格, 软件认为该文件为文件夹" \
                $ani_dialog_height $ani_dialog_width
            fi
        else # 选择取消
            break
        fi
    done
}
