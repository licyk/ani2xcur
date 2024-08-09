#!/bin.bash

# 更新 Ani2xcur
update_ani2xcur() {
    local commit_hash
    local ref
    local branch

    if fix_ani2xcur_git_file; then
        fix_git_point_offset
        ani_echo "更新 Ani2xcur 中"
        ani_echo "拉取 Ani2xcur 远端内容中"
        git fetch
        if [[ "$?" == 0 ]]; then
            ani_echo "应用 Ani2xcur 更新中"
            ref=$(git symbolic-ref --quiet HEAD 2> /dev/null)
            branch="origin/${ref#refs/heads/}"
            commit_hash=$(git log "${branch}" --max-count 1 --format="%h")
            git reset --hard "${commit_hash}"
            return 0
        else
            ani_echo "拉取 Ani2xcur 远端内容失败, 无法进行更新"
            return 1
        fi
    else
        return 1
    fi
}

# 修复 Anixcur 的 Git 信息
fix_ani2xcur_git_file() {
    if [[ -d ".git" ]]; then
        return 0
    else
        ani_echo "检测到 Ani2xcur 缺失 Git 文件信息, 尝试修复中"
        git init
        git remote add origin https://github.com/licyk/ani2xcur.git
        if git fetch; then
            git reset --hard origin/main
            git checkout main
            ani_echo "Ani2xcur Git 信息修复完成"
            return 0
        else
            rm -rf "${START_PATH}/.git"
            ani_echo "Ani2xcur Git 信息修复失败, 无法进行更新"
            return 1
        fi
    fi
}

# 修复 Git 仓库分支游离
fix_git_point_offset() {
    local branch

    if ! git symbolic-ref HEAD &> /dev/null; then
        ani_echo "检测到 Ani2xcur 出现分支游离, 尝试修复中"
        git remote prune origin # 删除无用分支
        git submodule init # 初始化 Git 子模块
        branch=$(git branch -a | grep "/HEAD" | awk -F '/' '{print $NF}') # 查询 HEAD 所指分支
        git checkout ${branch} # 切换到主分支
        git reset --recurse-submodules --hard origin/${branch} # 回退到远程分支的版本
        term_sd_echo "修复 Ani2xcur 完成"
    fi
}