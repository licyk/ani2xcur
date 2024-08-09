#!/bin/bash

# 文件浏览器
file_browser()
{
    local file_name
    local path

    while true; do
        path=$(pwd)
        get_dir_list "${path}" # 获取当前目录的所有文件 / 文件夹, 并返回 LOCAL_DIR_LIST 全局变量

        if [[ "${path}" == "/" ]]; then
            file_name=$(dialog --erase-on-exit \
                --ok-label "确认" --cancel-label "取消" \
                --title "Ani2xcur" \
                --backtitle "文件浏览器" \
                --menu "使用方向键和回车键进行选择\n当前路径: ${path}" \
                $(get_dialog_size_menu) \
                "-->返回主界面" "X" \
                "${LOCAL_DIR_LIST[@]}" \
                3>&1 1>&2 2>&3)
        else
            file_name=$(dialog --erase-on-exit \
                --ok-label "确认" --cancel-label "取消" \
                --title "Ani2xcur" \
                --backtitle "文件浏览器" \
                --menu "使用方向键和回车键进行选择\n当前路径: ${path}" \
                $(get_dialog_size_menu) \
                "-->返回上一个目录" "X" \
                "-->返回主界面" "X" \
                "${LOCAL_DIR_LIST[@]}" \
                3>&1 1>&2 2>&3)
        fi

        # 选择判断
        if [[ "$?" == 0 ]]; then
            if [[ "${file_name}" == "-->返回上一个目录" ]]; then # 选择返回上一个目录
                cd ..
            elif [[ "${file_name}" == "-->返回主界面" ]]; then
                break
            elif [[ -d "${file_name}" ]]; then # 选择的是目录
                cd "${file_name}"
                continue
            elif [[ -f "${file_name}" ]]; then # 选择的是文件
                case "${file_name}" in
                    *.$file_format_1)
                    # 选择的文件是指定格式
                        ani_win2xcur_start "${path}/${file_name}" # 转换完成后返回 EXEC_TIME 全局变量作为文件夹名
                        dialog --erase-on-exit \
                            --title "Ani2xcur" \
                            --backtitle "鼠标指针转换结果" \
                            --ok-label "确认" \
                            --msgbox "鼠标指针转换完成, 可在 ${START_PATH}/output/${EXEC_TIME} 文件夹中查看" \
                            $(get_dialog_size)
                        ;;
                    *.ani|*.cur)
                        # 选择的文件是指定格式
                        ani_win2xcur_start "${path}/$(ls -a | grep \.inf$ | awk 'NR==1')"
                        dialog --erase-on-exit \
                            --title "Ani2xcur" \
                            --backtitle "鼠标指针转换结果" \
                            --ok-label "确认" \
                            --msgbox "鼠标指针转换完成, 可在 ${START_PATH}/output/${EXEC_TIME} 文件夹中查看" \
                            $(get_dialog_size)
                        ;;
                    *.zip|*.7z)
                        # 文件解压缩功能，暂不支持自动检测编码，所以默认使用系统编码，如果压缩包是在windows系统中制作的，有可能会出现乱码
                        ani_echo "解压 ${file_name} 中"
                        7z x "${file_name}"
                        ;;
                    *.rar)
                        ani_echo "解压 ${file_name} 中"
                        unrar x "${file_name}"
                        ;;
                    *.tar|*.tar.Z|*.tar.lz|*.tar.lzma|*.tar.lzo)
                        ani_echo "解压 ${file_name} 中"
                        tar xvf "${file_name}"
                        ;;
                    *.tar.bz2)
                        ani_echo "解压 ${file_name} 中"
                        tar xvjf "${file_name}"
                        ;;
                    *.tar.7z)
                        ani_echo "解压 ${file_name} 中"
                        7z e -so "${file_name}" | tar xvf -
                        ;;
                    *.tar.gz)
                        ani_echo "解压 ${file_name} 中"
                        tar xvzf "${file_name}"
                        ;;
                    *.tar.xz)
                        ani_echo "解压 ${file_name} 中"
                        tar xvJf "${file_name}"
                        ;;
                    *.tar.zst)
                        ani_echo "解压 ${file_name} 中"
                        tar -I zstd -xvf "${file_name}"
                        ;;
                    *)
                        # 不是脚本指定的格式
                        dialog --erase-on-exit \
                            --ok-label "确认" \
                            --title "Ani2xcur" \
                            --backtitle "文件浏览器" \
                            --msgbox "文件格式错误, 请选择以 inf 后缀或 ani 后缀的文件" \
                            $(get_dialog_size)
                        ;;
                esac
            else 
                dialog --erase-on-exit \
                    --ok-label "确认" \
                    --title "Ani2xcur" \
                    --backtitle "文件浏览器" \
                    --msgbox "打开路径失败, 可能是文件夹名称包含空格, 或者是文件名包括空格, 软件认为该文件为文件夹" \
                    $(get_dialog_size)
            fi
        else
            # 选择取消
            break
        fi
    done

    unset LOCAL_DIR_LIST
    unset EXEC_TIME
}
