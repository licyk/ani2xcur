#1/bin/bash

# 初始化模块
# 通过 INSTALL_WIN2XCUR 全局变量确认是否进行安装 / 卸载 win2xcur
# 通过 CLI_MODE 全局变量确认启用命令模式 / 图形化模式
init_ani2xcur() {
    local i
    # 加载模块
    ani_echo "加载 Ani2xcur 模块"
    for i in "${START_PATH}"/modules/*; do
        [[ ! "${i}" == "${START_PATH}/modules/init.sh" ]] && . "${i}"
    done
}

init_ani2xcur
