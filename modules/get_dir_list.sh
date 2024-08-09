#!/bin/bash

# 获取当前路径中所有的文件和文件夹
# 使用:
# get_dir_folder_list <路径>
# 执行完成后返回一个全局变量(数组) LOCAL_DIR_LIST
# 使用 ${LOCAL_DIR_LIST[@]} 进行调用
get_dir_list() {
    local i
    local path
    local file_name
    local list
    local type
    unset LOCAL_DIR_LIST

    if [[ -z "$@" ]]; then
        path="."
    else
        path=$@
    fi

    if [[ -d "${path}" ]]; then
        if [[ "${path}" == "/" ]]; then
            # 目录为根目录时
            for i in /*; do
                file_name=${i#${path}/}
                if [[ -f "${i}" ]]; then
                    type="<文件>"
                else
                    type="<目录>"
                fi
                LOCAL_DIR_LIST+=("${file_name}" "${type}")
            done
        else
            for i in "${path}"/*; do
                file_name=${i#${path}/}
                if [[ -f "${i}" ]]; then
                    type="<文件>"
                else
                    type="<目录>"
                fi
                LOCAL_DIR_LIST+=("${file_name}" "${type}")
            done
        fi
    fi
}