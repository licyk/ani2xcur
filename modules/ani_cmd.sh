#!/bin/bash

# Python 命令
ani_pyhton() {
    # 检测是否在虚拟环境中
    if [[ ! -z "${VIRTUAL_ENV}" ]]; then # 当处在虚拟环境时
        # 检测使用哪种命令调用 Python
        # 调用虚拟环境的python
        if [[ ! -z "$(python --version 2> /dev/null)" ]]; then
            python "$@" # 加双引号防止运行报错
        elif [[ ! -z "$(python3 --version 2> /dev/null)" ]]; then
            python3 "$@"
        fi
    else # 不在虚拟环境时
        #调用系统中存在的 Python
        "${ANI_PYTHON_PATH}" "$@"
    fi
}

# Pip 命令
ani_pip() {
    # 检测是否在虚拟环境中
    if [[ ! -z "${VIRTUAL_ENV}" ]]; then
        # 调用虚拟环境的 Pip
        if [ ! -z "$(python --version 2> /dev/null)" ]; then
            python -m pip "$@"
        elif [ ! -z "$(python3 --version 2> /dev/null)" ]; then
            python3 -m pip "$@"
        fi
    else
        # 调用系统中存在的 Pip
        "${ANI_PYTHON_PATH}" -m pip "$@"
    fi
}

# win2xcur 命令
ani_win2xcur() {
    "${WIN2XCUR_PATH}" "$@"
}