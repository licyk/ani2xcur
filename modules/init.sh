#1/bin/bash

# 加载模块
ani_echo "加载 Ani2xcur 模块"
for i in ./modules/*
do
    [ ! "$i" = "./modules/init.sh" ] && . ./$i
done

# 安装win2xcur
case $install_win2xcur in
    1)
        ani_echo "安装 wi2n2xcur 中"
        if which win2xcur > /dev/null 2>&1; then
            ani_pip install numpy wand win2xcur --upgrade --force-reinstall
        else
            ani_pip install numpy wand win2xcur --upgrade
        fi
        if [ $? = 0 ];then
            ani_echo "win2xcur 核心安装成功"
        else
            ani_echo "win2xcur 核心安装成功"
        fi
        ;;
    2)
        ani_echo "卸载 wi2n2xcur 中"
        ani_pip uninstall win2xcur -y
        if [ $? = 0 ];then
            ani_echo "win2xcur 核心卸载成功"
        else
            ani_echo "win2xcur 核心卸载成功"
        fi
        ;;
esac

# 启动
if [ $cli_mode = 0 ];then
    ani_echo "启动转换"
    ani_win2xcur "$inf_file_path"
    ani_echo "转换完成"
    ani_echo "退出 Ani2xcur"
else
    mainmenu
    ani_echo "退出 Ani2xcur"
fi
