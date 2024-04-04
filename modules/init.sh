#1/bin/bash

# 加载模块
ani_echo "加载 Ani2xcur 模块"
for i in ./modules/*
do
    [ ! "$i" = "./modules/init.sh" ] && . ./$i
done

# 启动
if [ $cli_mode = 0 ];then
    ani_echo "启动转换"
    ani_win2xcur "$inf_file_path"
    ani_echo "转换完成"
    ani_echo "退出 Ani2xcur"
else
    mainmenu
fi
