#!/bin/bash

# 转换功能
# 使用:
# ani_win2xcur <鼠标指针的inf配置文件>
ani_win2xcur_start()
{
    local cur_name # 鼠标指针名字
    local cur_pointer
    local cur_help
    local cur_work
    local cur_busy
    local cur_cross
    local cur_text
    local cur_hand
    local cur_unavailiable
    local cur_vert
    local cur_horz
    local cur_dgn1
    local cur_dgn2
    local cur_move
    local cur_alternate
    local cur_link
    local cur_pin
    local cur_person
    local cur_name_n # 鼠标指针名字所在行号
    local cur_pointer_n
    local cur_help_n
    local cur_work_n
    local cur_busy_n
    local cur_cross_n
    local cur_text_n
    local cur_hand_n
    local cur_unavailiable_n
    local cur_vert_n
    local cur_horz_n
    local cur_dgn1_n
    local cur_dgn2_n
    local cur_move_n
    local cur_alternate_n
    local cur_link_n
    local cur_pin_n
    local cur_person_n
    local inf_file=$1 # 鼠标指针配置文件
    local inf_parent_path=$(dirname "${inf_file}")
    EXEC_TIME=$(date "+%Y-%m-%d-%H-%M-%S") # 执行结束时间

    # 检测win2xcur核心是否安装
    if ! which "${WIN2XCUR_PATH}" &> /dev/null ;then
        ani_echo "win2xcur 核心未安装"
        return 1
    fi

    # 获取配置文件
    ani_echo "读取配置文件: $inf_file"
    cat "$inf_file" | awk '/\[Strings\]/ { print; flag = 1; next } /=/ { if (flag == 1){ print } }' > "${START_PATH}"/task/ani_info_origin.conf # 读取inf配置
    iconv -f GBK -t UTF-8 "${START_PATH}"/task/ani_info_origin.conf > "${START_PATH}"/task/ani_info.conf # 编码转换
    rm -rf "${START_PATH}"/task/ani_info_origin.conf

    #读取各个鼠标指针参数(文件名称)
    # 获取参数所在行数
    cur_name_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "SCHEME_NAME" | awk -F ':' '{print $NR}')
    cur_pointer_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "pointer" | awk -F ':' '{print $NR}')
    cur_help_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "help" | awk -F ':' '{print $NR}')
    cur_work_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "work" | awk -F ':' '{print $NR}')
    cur_busy_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "busy" | awk -F ':' '{print $NR}')
    cur_cross_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "cross" | awk -F ':' '{print $NR}')
    cur_text_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "text" | awk -F ':' '{print $NR}')
    cur_hand_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "hand" | awk -F ':' '{print $NR}')
    cur_unavailiable_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "unavailiable" | awk -F ':' '{print $NR}')
    cur_vert_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "vert" | awk -F ':' '{print $NR}')
    cur_horz_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "horz" | awk -F ':' '{print $NR}')
    cur_dgn1_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "dgn1" | awk -F ':' '{print $NR}')
    cur_dgn2_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "dgn2" | awk -F ':' '{print $NR}')
    cur_move_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "move" | awk -F ':' '{print $NR}')
    cur_alternate_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "alternate" | awk -F ':' '{print $NR}')
    cur_link_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "link" | awk -F ':' '{print $NR}')
    cur_pin_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "pin" | awk -F ':' '{print $NR}')
    cur_person_n=$(cat "${START_PATH}"/task/ani_info.conf | awk '{print $1}' | grep -nE "person" | awk -F ':' '{print $NR}')

    # 获取对应文件名称
    if [[ ! -z "${cur_name_n}" ]]; then
        cur_name=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_name_n}'' | grep -E "SCHEME_NAME" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_pointer_n}" ]]; then
        cur_pointer=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_pointer_n}'' | grep -E "pointer" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_help_n}" ]]; then
        cur_help=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_help_n}'' | grep -E "help" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_work_n}" ]]; then
        cur_work=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_work_n}'' | grep -E "work" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_busy_n}" ]]; then
        cur_busy=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_busy_n}'' | grep -E "busy" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_cross_n}" ]]; then
        cur_cross=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_cross_n}'' | grep -E "cross" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_text_n}" ]]; then
        cur_text=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_text_n}'' | grep -E "text" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_hand_n}" ]]; then
        cur_hand=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_hand_n}'' | grep -E "hand" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_unavailiable_n}" ]]; then
        cur_unavailiable=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_unavailiable_n}'' | grep -E "unavailiable" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_vert_n}" ]]; then
        cur_vert=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_vert_n}'' | grep -E "vert" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_horz_n}" ]]; then
        cur_horz=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_horz_n}'' | grep -E "horz" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_dgn1_n}" ]]; then
        cur_dgn1=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_dgn1_n}'' | grep -E "dgn1" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_dgn2_n}" ]]; then
        cur_dgn2=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_dgn2_n}'' | grep -E "dgn2" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_move_n}" ]]; then
        cur_move=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_move_n}'' | grep -E "move" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_alternate_n}" ]]; then
        cur_alternate=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_alternate_n}'' | grep -E "alternate" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_link_n}" ]]; then
        cur_link=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_link_n}'' | grep -E "link" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_pin_n}" ]]; then
        cur_pin=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_pin_n}'' | grep -E "pin" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    if [[ ! -z "${cur_person_n}" ]]; then
        cur_person=$(cat "${START_PATH}"/task/ani_info.conf | awk 'NR=='${cur_person_n}'' | grep -E "person" | awk -F '"' '{print $2}' | tr 'A-Z' 'a-z')
    fi

    rm -f "${START_PATH}"/task/ani_info.conf # 清理配置缓存文件

    #创建鼠标指针文件夹
    mkdir -p "${START_PATH}"/task/cursors_tmp # 缓存文件夹
    mkdir -p "${START_PATH}/task/${EXEC_TIME}/cursors" # 鼠标指针文件夹

    # 鼠标指针格式转换
    ani_echo "开始鼠标指针文件转换"
    if [[ -z "${cur_pointer}" ]]; then # 不存在时从指针库复制
        cp -f "${START_PATH}"/source/left_ptr "${START_PATH}/task/${EXEC_TIME}/cursors"
    else
        cp -f "${inf_parent_path}/$(ls -a "${inf_parent_path}" | grep -iw "${cur_pointer}" | awk 'NR==1 {print}')" "${START_PATH}"/task/cursors_tmp/left_ptr.ani # 复制鼠标指针到缓存文件夹
        ani_win2xcur "${START_PATH}"/task/cursors_tmp/left_ptr.ani -o "${START_PATH}/task/${EXEC_TIME}/cursors" # 转换后存到鼠标指针文件夹
    fi

    if [[ -z "${cur_help}" ]]; then
        cp -f "${START_PATH}"/source/question_arrow "${START_PATH}/task/${EXEC_TIME}/cursors"
    else
        cp -f "${inf_parent_path}/$(ls -a "${inf_parent_path}" | grep -iw "${cur_help}" | awk 'NR==1 {print}')" "${START_PATH}"/task/cursors_tmp/question_arrow.ani
        ani_win2xcur "${START_PATH}"/task/cursors_tmp/question_arrow.ani -o "${START_PATH}/task/${EXEC_TIME}/cursors"
    fi

    if [[ -z "${cur_work}" ]]; then
        cp -f "${START_PATH}"/source/left_ptr_watch "${START_PATH}/task/${EXEC_TIME}/cursors"
    else
        cp -f "${inf_parent_path}/$(ls -a "${inf_parent_path}" | grep -iw "${cur_work}" | awk 'NR==1 {print}')" "${START_PATH}"/task/cursors_tmp/left_ptr_watch.ani
        ani_win2xcur "${START_PATH}"/task/cursors_tmp/left_ptr_watch.ani -o "${START_PATH}/task/${EXEC_TIME}/cursors"
    fi

    if [[ -z "${cur_busy}" ]]; then
        cp -f "${START_PATH}"/source/wait "${START_PATH}/task/${EXEC_TIME}/cursors"
    else
        cp -f "${inf_parent_path}/$(ls -a "${inf_parent_path}" | grep -iw "${cur_busy}" | awk 'NR==1 {print}')" "${START_PATH}"/task/cursors_tmp/wait.ani
        ani_win2xcur "${START_PATH}"/task/cursors_tmp/wait.ani -o "${START_PATH}/task/${EXEC_TIME}/cursors"
    fi

    if [[ -z "${cur_cross}" ]]; then
        cp -f "${START_PATH}"/source/cross "${START_PATH}/task/${EXEC_TIME}/cursors"
    else
        cp -f "${inf_parent_path}/$(ls -a "${inf_parent_path}" | grep -iw "${cur_cross}" | awk 'NR==1 {print}')" "${START_PATH}"/task/cursors_tmp/cross.ani
        ani_win2xcur "${START_PATH}"/task/cursors_tmp/cross.ani -o "${START_PATH}/task/${EXEC_TIME}/cursors"
    fi

    if [[ -z "${cur_text}" ]]; then
        cp -f "${START_PATH}"/source/xterm "${START_PATH}/task/${EXEC_TIME}/cursors"
    else
        cp -f "${inf_parent_path}/$(ls -a "${inf_parent_path}" | grep -iw "${cur_text}" | awk 'NR==1 {print}')" "${START_PATH}"/task/cursors_tmp/xterm.ani
        ani_win2xcur "${START_PATH}"/task/cursors_tmp/xterm.ani -o "${START_PATH}/task/${EXEC_TIME}/cursors"
    fi

    if [[ -z "${cur_hand}" ]]; then
        cp -f "${START_PATH}"/source/pencil "${START_PATH}/task/${EXEC_TIME}/cursors"
    else
        cp -f "${inf_parent_path}/$(ls -a "${inf_parent_path}" | grep -iw "${cur_hand}" | awk 'NR==1 {print}')" "${START_PATH}"/task/cursors_tmp/pencil.ani
        ani_win2xcur "${START_PATH}"/task/cursors_tmp/pencil.ani -o "${START_PATH}/task/${EXEC_TIME}/cursors"
    fi

    if [[ -z "${cur_unavailiable}" ]]; then
        cp -f "${START_PATH}"/source/circle "${START_PATH}/task/${EXEC_TIME}/cursors"
    else
        cp -f "${inf_parent_path}/$(ls -a "${inf_parent_path}" | grep -iw "${cur_unavailiable}" | awk 'NR==1 {print}')" "${START_PATH}"/task/cursors_tmp/circle.ani
        ani_win2xcur "${START_PATH}"/task/cursors_tmp/circle.ani -o "${START_PATH}/task/${EXEC_TIME}/cursors"
    fi

    if [[ -z "${cur_vert}" ]]; then
        cp -f "${START_PATH}"/source/bottom_side "${START_PATH}/task/${EXEC_TIME}/cursors"
    else
        cp -f "${inf_parent_path}/$(ls -a "${inf_parent_path}" | grep -iw "${cur_vert}" | awk 'NR==1 {print}')" "${START_PATH}"/task/cursors_tmp/bottom_side.ani
        ani_win2xcur "${START_PATH}"/task/cursors_tmp/bottom_side.ani -o "${START_PATH}/task/${EXEC_TIME}/cursors"
    fi

    if [[ -z "${cur_horz}" ]]; then
        cp -f "${START_PATH}"/source/left_side "${START_PATH}/task/${EXEC_TIME}/cursors"
    else
        cp -f "${inf_parent_path}/$(ls -a "${inf_parent_path}" | grep -iw "${cur_horz}" | awk 'NR==1 {print}')" "${START_PATH}"/task/cursors_tmp/left_side.ani
        ani_win2xcur "${START_PATH}"/task/cursors_tmp/left_side.ani -o "${START_PATH}/task/${EXEC_TIME}/cursors"
    fi

    if [[ -z "${cur_dgn1}" ]]; then
        cp -f "${START_PATH}"/source/bottom_right_corner "${START_PATH}/task/${EXEC_TIME}/cursors"
    else
        cp -f "${inf_parent_path}/$(ls -a "${inf_parent_path}" | grep -iw "${cur_dgn1}" | awk 'NR==1 {print}')" "${START_PATH}"/task/cursors_tmp/bottom_right_corner.ani
        ani_win2xcur "${START_PATH}"/task/cursors_tmp/bottom_right_corner.ani -o "${START_PATH}/task/${EXEC_TIME}/cursors"
    fi

    if [[ -z "${cur_dgn2}" ]]; then
        cp -f "${START_PATH}"/source/bottom_left_corner "${START_PATH}/task/${EXEC_TIME}/cursors"
    else
        cp -f "${inf_parent_path}/$(ls -a "${inf_parent_path}" | grep -iw "${cur_dgn2}" | awk 'NR==1 {print}')" "${START_PATH}"/task/cursors_tmp/bottom_left_corner.ani
        ani_win2xcur "${START_PATH}"/task/cursors_tmp/bottom_left_corner.ani -o "${START_PATH}/task/${EXEC_TIME}/cursors"
    fi

    if [[ -z "${cur_move}" ]]; then
        cp -f "${START_PATH}"/source/move "${START_PATH}/task/${EXEC_TIME}/cursors"
    else
        cp -f "${inf_parent_path}/$(ls -a "${inf_parent_path}" | grep -iw "${cur_move}" | awk 'NR==1 {print}')" "${START_PATH}"/task/cursors_tmp/move.ani
        ani_win2xcur "${START_PATH}"/task/cursors_tmp/move.ani -o "${START_PATH}/task/${EXEC_TIME}/cursors"
    fi

    if [[ -z "${cur_alternate}" ]]; then
        cp -f "${START_PATH}"/source/dotbox "${START_PATH}/task/${EXEC_TIME}/cursors"
    else
        cp -f "${inf_parent_path}/$(ls -a "${inf_parent_path}" | grep -iw "${cur_alternate}" | awk 'NR==1 {print}')" "${START_PATH}"/task/cursors_tmp/dotbox.ani
        ani_win2xcur "${START_PATH}"/task/cursors_tmp/dotbox.ani -o "${START_PATH}/task/${EXEC_TIME}/cursors"
    fi

    if [[ -z "${cur_link}" ]]; then
        cp -f "${START_PATH}"/source/hand2 "${START_PATH}/task/${EXEC_TIME}/cursors"
    else
        cp -f "${inf_parent_path}/$(ls -a "${inf_parent_path}" | grep -iw "${cur_link}" | awk 'NR==1 {print}')" "${START_PATH}"/task/cursors_tmp/hand2.ani
        ani_win2xcur "${START_PATH}"/task/cursors_tmp/hand2.ani -o "${START_PATH}/task/${EXEC_TIME}/cursors"
    fi

    # 删除临时文件夹
    rm -rf "${START_PATH}"/task/cursors_tmp

    # 这两种鼠标指针很少人会去做，所以就不转换了
    # if [ -z "$cur_pin" ]; then
    #     cp -f "${START_PATH}"/win2xcur-source/
    # else
    #     cp -f "$cur_pin" "${START_PATH}"/task/cursors_tmp/pin.ani
    #     win2xcur "${START_PATH}"/task/cursors_tmp/pin.ani -o "${START_PATH}"/task/"$cur_name"/cursors
    # fi

    # if [ -z "$cur_person" ]; then
    #     cp -f "${START_PATH}"/win2xcur-source/
    # else
    #     cp -f "$cur_person" "${START_PATH}"/task/cursors_tmp/person.ani
    #     win2xcur "${START_PATH}"/task/cursors_tmp/person.ani -o "${START_PATH}"/task/"$cur_name"/cursors
    # fi

    # 补全剩下的鼠标文件夹
    ani_echo "补全剩余鼠标指针文件"
    cp "${START_PATH}"/source/right_ptr "${START_PATH}/task/${EXEC_TIME}/cursors"
    cp "${START_PATH}"/source/vertical-text "${START_PATH}/task/${EXEC_TIME}/cursors"
    cp "${START_PATH}"/source/wayland-cursor "${START_PATH}/task/${EXEC_TIME}/cursors"
    cp "${START_PATH}"/source/zoom-out "${START_PATH}/task/${EXEC_TIME}/cursors"
    cp "${START_PATH}"/source/zoom-in "${START_PATH}/task/${EXEC_TIME}/cursors"
    cp "${START_PATH}"/source/center_ptr "${START_PATH}/task/${EXEC_TIME}/cursors"

    # 进入鼠标指针文件夹
    cd "${START_PATH}/task/${EXEC_TIME}/cursors"

    # 为其他鼠标指针别名创建链接
    ani_echo "创建鼠标指针文件链接"
    ln -s left_ptr context-menu
    ln -s left_ptr grabbing
    ln -s left_ptr hand1
    ln -s left_ptr arrow
    ln -s left_ptr closedhand
    ln -s left_ptr default
    ln -s left_ptr dnd-none
    ln -s left_ptr grab
    ln -s left_ptr openhand
    ln -s left_ptr top_left_arrow
    ln -s left_ptr fcf21c00b30f7e3f83fe0dfd12e71cff

    ln -s left_ptr_watch progress
    ln -s left_ptr_watch 00000000000000020006000e7e9ffc3f
    ln -s left_ptr_watch 08e8e1c95fe2fc01f976f1e063a24ccd
    ln -s left_ptr_watch 3ecb610c1bf2410f44200f48c40d3599

    ln -s right_ptr draft_large
    ln -s right_ptr draft_small
    ln -s right_ptr e-resize

    ln -s move all-scroll
    ln -s move fleur
    ln -s move size_all
    ln -s move 4498f0e0c1937ffe01fd06f973665830
    ln -s move 9081237383d90e509aa00f00170e968f

    ln -s question_arrow dnd-ask
    ln -s question_arrow help
    ln -s question_arrow left_ptr_help
    ln -s question_arrow whats_this
    ln -s question_arrow 5c6cd98b3f3ebcb1f9c7f1c204630408
    ln -s question_arrow d9ce0ab605698f320427677b458ad60b

    ln -s xterm ibeam
    ln -s xterm text

    ln -s wait watch

    ln -s hand2 pointer
    ln -s hand2 pointing_hand
    ln -s hand2 9d800788f1b08800ae810202380a0822
    ln -s hand2 e29285e634086352946a0e7090d73106

    ln -s pencil copy
    ln -s pencil dnd-copy
    ln -s pencil dnd-move
    ln -s pencil dnd-link
    ln -s pencil link
    ln -s pencil pointer-move
    ln -s pencil alias
    ln -s pencil draft
    ln -s pencil 1081e37283d90000800003c07f3ef6bf
    ln -s pencil 3085a0e285430894940527032f8b26df
    ln -s pencil 6407b0e94181790501fd1e167b474872
    ln -s pencil 640fb0e74195791501fd1ed57b41487f
    ln -s pencil a2a266d0498c3104214a47bd64ab0fc8
    ln -s pencil b66166c04f8c3109214a4fbd64a50fc8

    ln -s circle crossed_circle
    ln -s circle dnd_no_drop
    ln -s circle X_cursor
    ln -s circle x-cursor
    ln -s circle forbidden
    ln -s circle no-drop
    ln -s circle not-allowed
    ln -s circle pirate
    ln -s circle 03b6e0fcb3499374a867c041f52298f0

    ln -s cross crosshair
    ln -s cross tcross
    ln -s cross color-picker
    ln -s cross cross_reverse
    ln -s cross diamond_cross

    ln -s bottom_left_corner fd_double_arrow
    ln -s bottom_left_corner ll_angle
    ln -s bottom_left_corner top_right_corner
    ln -s bottom_left_corner ur_angle
    ln -s bottom_left_corner ne-resize
    ln -s bottom_left_corner nesw-resize
    ln -s bottom_left_corner size_bdiag
    ln -s bottom_left_corner sw-resize
    ln -s bottom_left_corner fcf1c3c7cd4491d801f1e1c78f100000

    ln -s bottom_right_corner bd_double_arrow
    ln -s bottom_right_corner lr_angle
    ln -s bottom_right_corner top_left_corner
    ln -s bottom_right_corner ul_angle
    ln -s bottom_right_corner nw-resize
    ln -s bottom_right_corner nwse-resize
    ln -s bottom_right_corner se-resize
    ln -s bottom_right_corner size_fdiag
    ln -s bottom_right_corner c7088f0f3e6c8088236ef8e1e3e70000

    ln -s bottom_side bottom_tee
    ln -s bottom_side plus
    ln -s bottom_side sb_down_arrow
    ln -s bottom_side sb_up_arrow
    ln -s bottom_side sb_v_double_arrow
    ln -s bottom_side top_side
    ln -s bottom_side top_tee
    ln -s bottom_side cell
    ln -s bottom_side double_arrow
    ln -s bottom_side down-arrow
    ln -s bottom_side n-resize
    ln -s bottom_side ns-resize
    ln -s bottom_side row-resize
    ln -s bottom_side s-resize
    ln -s bottom_side up-arrow
    ln -s bottom_side v_double_arrow
    ln -s bottom_side size_ver
    ln -s bottom_side 00008160000006810000408080010102
    ln -s bottom_side 2870a09082c31050810ffdffffe0204

    ln -s left_side left_tee
    ln -s left_side right_side
    ln -s left_side right_tee
    ln -s left_side sb_h_double_arrow
    ln -s left_side sb_left_arrow
    ln -s left_side sb_right_arrow
    ln -s left_side col-resize
    ln -s left_side ew-resize
    ln -s left_side h_double_arrow
    ln -s left_side left-arrow
    ln -s left_side right-arrow
    ln -s left_side size-hor
    ln -s left_side size-ver
    ln -s left_side split_h
    ln -s left_side split_v
    ln -s left_side w-resize
    ln -s left_side size_hor
    ln -s left_side 028006030e0e7ebffc7f7070c0600140
    ln -s left_side 14fef782d02440884392942c1120523 

    ln -s dotbox dot_box_mask
    ln -s dotbox draped_box
    ln -s dotbox icon
    ln -s dotbox target

    # 返回原来的目录
    cd - > /dev/null

    # 为鼠标指针生成配置文件
    ani_echo "生成配置文件中"
    generate_config "${cur_name}"

    # 移动鼠标文件夹到最终输出文件夹
    mkdir -p "${START_PATH}/output/${EXEC_TIME}"
    mv -f "${START_PATH}/task/${EXEC_TIME}" "${START_PATH}/output/${EXEC_TIME}"
    mv -f "${START_PATH}/output/${EXEC_TIME}/${EXEC_TIME}" "${START_PATH}/output/${EXEC_TIME}/${cur_name}"

    # 生成鼠标指针安装脚本到鼠标指针文件夹所在目录
    generate_install_script "${cur_name}"

    ani_echo "转换结束, 鼠标指针文件保存路径: ${START_PATH}/output/${EXEC_TIME}"
}

# 生成配置文件
generate_config() {
    local cur_name=$@

    # cursor.theme
    cat<<EOF > "${START_PATH}/task/${EXEC_TIME}/cursor.theme"
[Icon Theme]
Name=${cur_name}
Inherits=${cur_name}
EOF

    # index.tmeme
    cat<<EOF > "${START_PATH}/task/${EXEC_TIME}/index.theme"
[Icon Theme]
Name=${cur_name}
Comment=${cur_name} cursors for Linux
Inherits=hicolor
EOF
}

# 生成安装脚本
generate_install_script() {
    local cur_name=$@

    cat<<EOF > "${START_PATH}/output/${EXEC_TIME}/install.sh"
#!/bin/bash

echo "将鼠标指针安装至 \$HOME/.icons"
cp -r "./${cur_name}" "\$HOME/.icons"
echo "${cur_name} 鼠标指针安装完成, 可使用运行下面的命令启用该鼠标指针"
echo "\$ gsettings set org.gnome.desktop.interface cursor-theme \"${cur_name}\""
EOF
    chmod +x "${START_PATH}/output/${EXEC_TIME}/install.sh"
}
