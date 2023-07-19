inf_file=$(ls -a | grep \.inf$)
start_path_=$(pwd)
function mainmenu()
{
    if which win2xcur > /dev/null ;then
        echo "已安装win2xcur"
    else
        echo "未安装win2xcur"
        install_win2xcur
    fi
    declare -g test_source_num_="0"
    test_source
    if [ $test_source_num_ = 1 ];then
        install_source
    else
        echo "资源文件完整"
    fi
    echo "环境准备完成，开始转换"
    start_win2xcur
    echo "输入以下任意一条指令可将鼠标指针安装进系统\n\"sudo cp $start_path_/"$cur_name" /usr/share/icons\"\n\"mkdir ~/.icons && cp $start_path_/"$cur_name" ~/.icons\""
    exit
}

#win2xcur安装
function install_win2xcur()
{
    echo "请选择pip安装源,如果没有科学上网的话建议使用镜像源"
    echo "1、官方源"
    echo "2、镜像源"
    read -p "输入数字后回车==>" pip_pak_image
    if [ $pip_pak_image = 1 ];then
        pip install win2xcur -i https://pypi.python.org/simple
    elif [ $pip_pak_image = 2 ];then
        pip install win2xcur-i https://mirrors.bfsu.edu.cn/pypi/web/simple
    else
        echo "输入有误，请重试"
        test_win2xcur
    fi
    mainmenu
}

function install_source()
{
    echo "请选择下载资源方式"
    echo "1、不使用代理站"
    echo "2、使用代理站"
    read -p "输入数字后回车==>" github_proxy_select
    if [ $github_proxy_select = 1 ];then
        declare -g dl_source_methon="1"
        dl_source
        mainmenu
    elif [ $github_proxy_select = 2 ];then
        declare -g dl_source_methon="proxy"
        dl_source
        mainmenu
    else
        echo "输入有误，请重试"
        install_source
    fi
}

function test_source()
{
    #检测文件是否完整
    test_source_num=0

    if [ ! -e $start_path_/win2xcur-source/left_ptr ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! -e $start_path_/win2xcur-source/question_arrow ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi
    
    if [ ! -e $start_path_/win2xcur-source/left_ptr_watch ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! -e $start_path_/win2xcur-source/wait ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! -e $start_path_/win2xcur-source/cross ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! -e $start_path_/win2xcur-source/xterm ];then

        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! -e $start_path_/win2xcur-source/pencil ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! -e $start_path_/win2xcur-source/circle ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi
    
    if [ ! -e $start_path_/win2xcur-source/bottom_side ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! -e $start_path_/win2xcur-source/left_side ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! -e $start_path_/win2xcur-source/bottom_right_corner ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! -e $start_path_/win2xcur-source/bottom_left_corner ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! -e $start_path_/win2xcur-source/move ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! -e $start_path_/win2xcur-source/dotbox ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! -e $start_path_/win2xcur-source/hand2 ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! -e $start_path_/win2xcur-source/right_ptr ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi
    
    if [ ! -e $start_path_/win2xcur-source/vertical-text ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! -e $start_path_/win2xcur-source/wayland-cursor ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! -e $start_path_/win2xcur-source/center_ptr ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! -e $start_path_/win2xcur-source/zoom-in ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi
    
    if [ ! -e $start_path_/win2xcur-source/zoom-out ];then
        test_source_num=$(( $test_source_num + 1 ))
    fi

    if [ ! $test_source_num -gt 0 ];then
        echo "资源完整"
    else
        echo "资源不完整，请重新下载"
        declare -g test_source_num_="1"
    fi
}

function dl_source()
{
    echo "下载资源文件"
    #创建资源文件夹
    if [ ! -e $start_path_/win2xcur-source ];then
        mkdir $start_path_/win2xcur-source
    fi
    cd $start_path_
    #下载资源文件
    if [ $dl_source_methon = proxy ];then
        echo "使用代理站"

        if [ ! -e $start_path_/win2xcur-source/left_ptr ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/left_ptr -o ./win2xcur-source/left_ptr
        fi

        if [ ! -e $start_path_/win2xcur-source/question_arrow ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/question_arrow -o ./win2xcur-source/question_arrow
        fi

        if [ ! -e $start_path_/win2xcur-source/left_ptr_watch ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/left_ptr_watch -o ./win2xcur-source/left_ptr_watch
        fi

        if [ ! -e $start_path_/win2xcur-source/wait ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/wait -o ./win2xcur-source/wait
        fi

        if [ ! -e $start_path_/win2xcur-source/cross ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/cross -o ./win2xcur-source/cross
        fi

        if [ ! -e $start_path_/win2xcur-source/xterm ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/xterm -o ./win2xcur-source/xterm
        fi

        if [ ! -e $start_path_/win2xcur-source/pencil ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/pencil -o ./win2xcur-source/pencil
        fi

        if [ ! -e $start_path_/win2xcur-source/circle ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/circle -o ./win2xcur-source/circle
        fi

        if [ ! -e $start_path_/win2xcur-source/bottom_side ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/bottom_side -o ./win2xcur-source/bottom_side
        fi

        if [ ! -e $start_path_/win2xcur-source/left_side ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/left_side -o ./win2xcur-source/left_side
        fi

        if [ ! -e $start_path_/win2xcur-source/bottom_right_corner ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/bottom_right_corner -o ./win2xcur-source/bottom_right_corner
        fi

        if [ ! -e $start_path_/win2xcur-source/bottom_left_corner ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/bottom_left_corner -o ./win2xcur-source/bottom_left_corner
        fi

        if [ ! -e $start_path_/win2xcur-source/move ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/move -o ./win2xcur-source/move
        fi

        if [ ! -e $start_path_/win2xcur-source/dotbox ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/dotbox -o ./win2xcur-source/dotbox
        fi

        if [ ! -e $start_path_/win2xcur-source/hand2 ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/hand2 -o ./win2xcur-source/hand2
        fi

        if [ ! -e $start_path_/win2xcur-source/right_ptr ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/right_ptr -o ./win2xcur-source/right_ptr
        fi

        if [ ! -e $start_path_/win2xcur-source/vertical-text ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/vertical-text -o ./win2xcur-source/vertical-text
        fi

        if [ ! -e $start_path_/win2xcur-source/wayland-cursor ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/wayland-cursor -o ./win2xcur-source/wayland-cursor
        fi

        if [ ! -e $start_path_/win2xcur-source/center_ptr ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/center_ptr -o ./win2xcur-source/center_ptr
        fi

        if [ ! -e $start_path_/win2xcur-source/zoom-in ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/zoom-in -o ./win2xcur-source/zoom-in
        fi

        if [ ! -e $start_path_/win2xcur-source/zoom-out ];then
            aria2c https://ghproxy.com/https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/zoom-out -o ./win2xcur-source/zoom-out
        fi

    else

        if [ ! -e $start_path_/win2xcur-source/left_ptr ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/left_ptr -o ./win2xcur-source/left_ptr
        fi

        if [ ! -e $start_path_/win2xcur-source/question_arrow ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/question_arrow -o ./win2xcur-source/question_arrow
        fi

        if [ ! -e $start_path_/win2xcur-source/left_ptr_watch ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/left_ptr_watch -o ./win2xcur-source/left_ptr_watch
        fi

        if [ ! -e $start_path_/win2xcur-source/wait ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/wait -o ./win2xcur-source/wait
        fi

        if [ ! -e $start_path_/win2xcur-source/cross ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/cross -o ./win2xcur-source/cross
        fi

        if [ ! -e $start_path_/win2xcur-source/xterm ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/xterm -o ./win2xcur-source/xterm
        fi

        if [ ! -e $start_path_/win2xcur-source/pencil ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/pencil -o ./win2xcur-source/pencil
        fi

        if [ ! -e $start_path_/win2xcur-source/circle ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/circle -o ./win2xcur-source/circle
        fi

        if [ ! -e $start_path_/win2xcur-source/bottom_side ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/bottom_side -o ./win2xcur-source/bottom_side
        fi

        if [ ! -e $start_path_/win2xcur-source/left_side ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/left_side -o ./win2xcur-source/left_side
        fi

        if [ ! -e $start_path_/win2xcur-source/bottom_right_corner ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/bottom_right_corner -o ./win2xcur-source/bottom_right_corner
        fi

        if [ ! -e $start_path_/win2xcur-source/bottom_left_corner ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/bottom_left_corner -o ./win2xcur-source/bottom_left_corner
        fi

        if [ ! -e $start_path_/win2xcur-source/move ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/move -o ./win2xcur-source/move
        fi

        if [ ! -e $start_path_/win2xcur-source/dotbox ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/dotbox -o ./win2xcur-source/dotbox
        fi

        if [ ! -e $start_path_/win2xcur-source/hand2 ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/hand2 -o ./win2xcur-source/hand2
        fi

        if [ ! -e $start_path_/win2xcur-source/right_ptr ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/right_ptr -o ./win2xcur-source/right_ptr
        fi

        if [ ! -e $start_path_/win2xcur-source/vertical-text ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/vertical-text -o ./win2xcur-source/vertical-text
        fi

        if [ ! -e $start_path_/win2xcur-source/wayland-cursor ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/wayland-cursor -o ./win2xcur-source/wayland-cursor
        fi

        if [ ! -e $start_path_/win2xcur-source/center_ptr ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/center_ptr -o ./win2xcur-source/center_ptr
        fi

        if [ ! -e $start_path_/win2xcur-source/zoom-in ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/zoom-in -o ./win2xcur-source/zoom-in
        fi

        if [ ! -e $start_path_/win2xcur-source/zoom-out ];then
            aria2c https://raw.githubusercontent.com/licyk/ani2xcur/main/win2xcur-source/zoom-out -o ./win2xcur-source/zoom-out
        fi
    fi

}

function start_win2xcur()
{
    cat "$inf_file" | awk '/\[Strings\]/{print;flag=1;next}/=/{if(flag==1)print}' > .win2xcur-pre_.conf #读取inf配置
    iconv -f GBK -t UTF-8 .win2xcur-pre_.conf >.win2xcur-pre.conf
    rm -rfv ./.win2xcur-pre_.conf
    cur_name=""
    cur_pointer=""
    cur_help=""
    cur_work=""
    cur_busy=""
    cur_cross=""
    cur_text=""
    cur_hand=""
    cur_unavailiable=""
    cur_vert=""
    cur_horz=""
    cur_dgn1=""
    cur_dgn2=""
    cur_move=""
    cur_alternate=""
    cur_link=""
    cur_pin=""
    cur_person=""

    #读取各个鼠标指针参数
    cur_name=$(grep -IE "SCHEME_NAME" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_pointer=$(grep -E "pointer" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_help=$(grep -E "help" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_work=$(grep -E "work" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_busy=$(grep -E "busy" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_cross=$(grep -E "cross" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_text=$(grep -E "text" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_hand=$(grep -E "hand" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_unavailiable=$(grep -E "unavailiable" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_vert=$(grep -E "vert" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_horz=$(grep -E "horz" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_dgn1=$(grep -E "dgn1" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_dgn2=$(grep -E "dgn2" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_move=$(grep -E "move" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_alternate=$(grep -E "alternate" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_link=$(grep -E "link" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_pin=$(grep -E "pin" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')
    cur_person=$(grep -E "person" ./.win2xcur-pre.conf | awk -F'"' '{print $2}' |tr 'A-Z' 'a-z')

    echo "----------配置文件----------"
    echo "鼠标名:"
    echo $cur_name
    echo "鼠标文件:"
    echo $cur_pointer
    echo $cur_help
    echo $cur_work
    echo $cur_busy
    echo $cur_cross
    echo $cur_text
    echo $cur_hand
    echo $cur_unavailiable
    echo $cur_vert
    echo $cur_horz
    echo $cur_dgn1
    echo $cur_dgn2
    echo $cur_move
    echo $cur_alternate
    echo $cur_link
    echo $cur_pin
    echo $cur_person
    echo "----------------------------"

    rm -fv ./.win2xcur-pre.conf #清理配置缓存文件
    start_path=$(pwd)

    #创建鼠标指针文件夹
    mkdir $start_path/win2xcur-tmp
    mkdir $start_path/win2xcur-tmp/cursors-tmp
    mkdir $start_path/win2xcur-tmp/"$cur_name"
    mkdir $start_path/win2xcur-tmp/"$cur_name"/cursors

    #开始转换
    if [ -z "$cur_pointer" ];then
        echo "cur_pointer不存在,补全中"
        cp $start_path_/win2xcur-source/left_ptr $start_path/win2xcur-tmp/"$cur_name"/cursors
    else
        echo "cur_pointer存在,进行转换中"
        cp -ifv "$(ls -a |grep -iw "$cur_pointer")" $start_path/win2xcur-tmp/cursors-tmp/left_ptr.ani
        win2xcur $start_path/win2xcur-tmp/cursors-tmp/left_ptr.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    fi

    if [ -z "$cur_help" ];then
        echo "cur_help不存在,补全中"
        cp $start_path_/win2xcur-source/question_arrow $start_path/win2xcur-tmp/"$cur_name"/cursors
    else
        echo "cur_help存在,进行转换中"
        cp -ifv "$(ls -a |grep -iw "$cur_help")" $start_path/win2xcur-tmp/cursors-tmp/question_arrow.ani
        win2xcur $start_path/win2xcur-tmp/cursors-tmp/question_arrow.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    fi

    if [ -z "$cur_work" ];then
        echo "cur_work不存在,补全中"
        cp $start_path_/win2xcur-source/left_ptr_watch $start_path/win2xcur-tmp/"$cur_name"/cursors
    else
        echo "cur_work存在,进行转换中"
        cp -ifv "$(ls -a |grep -iw "$cur_work")" $start_path/win2xcur-tmp/cursors-tmp/left_ptr_watch.ani
        win2xcur $start_path/win2xcur-tmp/cursors-tmp/left_ptr_watch.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    fi

    if [ -z "$cur_busy" ];then
        echo "cur_busy不存在,补全中"
        cp $start_path_/win2xcur-source/wait $start_path/win2xcur-tmp/"$cur_name"/cursors
    else
        echo "cur_busy存在,进行转换中"
        cp -ifv "$(ls -a |grep -iw "$cur_busy")" $start_path/win2xcur-tmp/cursors-tmp/wait.ani
        win2xcur $start_path/win2xcur-tmp/cursors-tmp/wait.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    fi

    if [ -z "$cur_cross" ];then
        echo "cur_cross不存在,补全中"
        cp $start_path_/win2xcur-source/cross $start_path/win2xcur-tmp/"$cur_name"/cursors
    else
        echo "cur_cross存在,进行转换中"
        cp -ifv "$(ls -a |grep -iw "$cur_cross")" $start_path/win2xcur-tmp/cursors-tmp/cross.ani
        win2xcur $start_path/win2xcur-tmp/cursors-tmp/cross.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    fi

    if [ -z "$cur_text" ];then
        echo "cur_text不存在,补全中"
        cp $start_path_/win2xcur-source/xterm $start_path/win2xcur-tmp/"$cur_name"/cursors
    else
        echo "cur_text存在,进行转换中"
        cp -ifv "$(ls -a |grep -iw "$cur_text")" $start_path/win2xcur-tmp/cursors-tmp/xterm.ani
        win2xcur $start_path/win2xcur-tmp/cursors-tmp/xterm.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    fi

    if [ -z "$cur_hand" ];then
        echo "cur_hand不存在,补全中"
        cp $start_path_/win2xcur-source/pencil $start_path/win2xcur-tmp/"$cur_name"/cursors
    else    
        echo "cur_hand存在,进行转换中"
        cp -ifv "$(ls -a |grep -iw "$cur_hand")" $start_path/win2xcur-tmp/cursors-tmp/pencil.ani
        win2xcur $start_path/win2xcur-tmp/cursors-tmp/pencil.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    fi

    if [ -z "$cur_unavailiable" ];then
        echo "cur_unavailiable不存在,补全中"
        cp $start_path_/win2xcur-source/circle $start_path/win2xcur-tmp/"$cur_name"/cursors
    else
        echo "cur_unavailiable存在,进行转换中"
        cp -ifv "$(ls -a |grep -iw "$cur_unavailiable")" $start_path/win2xcur-tmp/cursors-tmp/circle.ani
        win2xcur $start_path/win2xcur-tmp/cursors-tmp/circle.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    fi

    if [ -z "$cur_vert" ];then
        echo "cur_vert不存在,补全中"
        cp $start_path_/win2xcur-source/bottom_side $start_path/win2xcur-tmp/"$cur_name"/cursors
    else
        echo "cur_vert存在,进行转换中"
        cp -ifv "$(ls -a |grep -iw "$cur_vert")" $start_path/win2xcur-tmp/cursors-tmp/bottom_side.ani
        win2xcur $start_path/win2xcur-tmp/cursors-tmp/bottom_side.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    fi

    if [ -z "$cur_horz" ];then
        echo "cur_horz不存在,补全中"
        cp $start_path_/win2xcur-source/left_side $start_path/win2xcur-tmp/"$cur_name"/cursors
    else
        echo "cur_horz存在,进行转换中"
        cp -ifv "$(ls -a |grep -iw "$cur_horz")" $start_path/win2xcur-tmp/cursors-tmp/left_side.ani
        win2xcur $start_path/win2xcur-tmp/cursors-tmp/left_side.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    fi

    if [ -z "$cur_dgn1" ];then
        echo "cur_dgn1不存在,补全中"
        cp $start_path_/win2xcur-source/bottom_right_corner $start_path/win2xcur-tmp/"$cur_name"/cursors
    else
        echo "cur_dgn1存在,进行转换中"
        cp -ifv "$(ls -a |grep -iw "$cur_dgn1")" $start_path/win2xcur-tmp/cursors-tmp/bottom_right_corner.ani
        win2xcur $start_path/win2xcur-tmp/cursors-tmp/bottom_right_corner.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    fi

    if [ -z "$cur_dgn2" ];then
        echo "cur_dgn2不存在,补全中"
        cp $start_path_/win2xcur-source/bottom_left_corner $start_path/win2xcur-tmp/"$cur_name"/cursors
    else
        echo "cur_dgn2存在,进行转换中"
        cp -ifv "$(ls -a |grep -iw "$cur_dgn2")" $start_path/win2xcur-tmp/cursors-tmp/bottom_left_corner.ani
        win2xcur $start_path/win2xcur-tmp/cursors-tmp/bottom_left_corner.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    fi

    if [ -z "$cur_move" ];then
        echo "cur_move不存在,补全中"
        cp $start_path_/win2xcur-source/move $start_path/win2xcur-tmp/"$cur_name"/cursors
    else
        echo "cur_move存在,进行转换中"
        cp -ifv "$(ls -a |grep -iw "$cur_move")" $start_path/win2xcur-tmp/cursors-tmp/move.ani
        win2xcur $start_path/win2xcur-tmp/cursors-tmp/move.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    fi

    if [ -z "$cur_alternate" ];then
        echo "cur_alternate不存在,补全中"
        cp $start_path_/win2xcur-source/dotbox $start_path/win2xcur-tmp/"$cur_name"/cursors
    else
        echo "cur_alternate存在,进行转换中"
        cp -ifv "$(ls -a |grep -iw "$cur_alternate")" $start_path/win2xcur-tmp/cursors-tmp/dotbox.ani
        win2xcur $start_path/win2xcur-tmp/cursors-tmp/dotbox.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    fi

    if [ -z "$cur_link" ];then
        echo "cur_link不存在,补全中"
        cp $start_path_/win2xcur-source/hand2 $start_path/win2xcur-tmp/"$cur_name"/cursors
    else
        echo "cur_link存在,进行转换中"
        cp -ifv "$(ls -a |grep -iw "$cur_link")" $start_path/win2xcur-tmp/cursors-tmp/hand2.ani
        win2xcur $start_path/win2xcur-tmp/cursors-tmp/hand2.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    fi

    echo "补全鼠标指针中"
    cp -fv $start_path_/win2xcur-source/right_ptr $start_path/win2xcur-tmp/"$cur_name"/cursors
    cp -fv $start_path_/win2xcur-source/vertical-text $start_path/win2xcur-tmp/"$cur_name"/cursors
    cp -fv $start_path_/win2xcur-source/wayland-cursor $start_path/win2xcur-tmp/"$cur_name"/cursors
    cp -fv $start_path_/win2xcur-source/zoom-out $start_path/win2xcur-tmp/"$cur_name"/cursors
    cp -fv $start_path_/win2xcur-source/zoom-in $start_path/win2xcur-tmp/"$cur_name"/cursors
    cp -fv $start_path_/win2xcur-source/center_ptr $start_path/win2xcur-tmp/"$cur_name"/cursors
    
    #为其他鼠标指针别名创建链接
    echo "创建鼠标指针链接"
    cd $start_path/win2xcur-tmp/"$cur_name"/cursors
    ln -sv left_ptr context-menu
    ln -sv left_ptr grabbing
    ln -sv left_ptr hand1
    ln -sv left_ptr arrow
    ln -sv left_ptr closedhand
    ln -sv left_ptr default
    ln -sv left_ptr dnd-none
    ln -sv left_ptr grab
    ln -sv left_ptr openhand
    ln -sv left_ptr top_left_arrow
    ln -sv left_ptr fcf21c00b30f7e3f83fe0dfd12e71cff

    ln -sv left_ptr_watch progress
    ln -sv left_ptr_watch 00000000000000020006000e7e9ffc3f
    ln -sv left_ptr_watch 08e8e1c95fe2fc01f976f1e063a24ccd
    ln -sv left_ptr_watch 3ecb610c1bf2410f44200f48c40d3599

    ln -sv right_ptr draft_large
    ln -sv right_ptr draft_small
    ln -sv right_ptr e-resize

    ln -sv move all-scroll
    ln -sv move fleur
    ln -sv move size_all
    ln -sv move 4498f0e0c1937ffe01fd06f973665830
    ln -sv move 9081237383d90e509aa00f00170e968f

    ln -sv question_arrow dnd-ask
    ln -sv question_arrow help
    ln -sv question_arrow left_ptr_help
    ln -sv question_arrow whats_this
    ln -sv question_arrow 5c6cd98b3f3ebcb1f9c7f1c204630408
    ln -sv question_arrow d9ce0ab605698f320427677b458ad60b

    ln -sv xterm ibeam
    ln -sv xterm text

    ln -sv wait watch

    ln -sv hand2 pointer
    ln -sv hand2 pointing_hand
    ln -sv hand2 9d800788f1b08800ae810202380a0822
    ln -sv hand2 e29285e634086352946a0e7090d73106

    ln -sv pencil copy
    ln -sv pencil dnd-copy
    ln -sv pencil dnd-move
    ln -sv pencil dnd-link
    ln -sv pencil link
    ln -sv pencil pointer-move
    ln -sv pencil alias
    ln -sv pencil draft
    ln -sv pencil 1081e37283d90000800003c07f3ef6bf
    ln -sv pencil 3085a0e285430894940527032f8b26df
    ln -sv pencil 6407b0e94181790501fd1e167b474872
    ln -sv pencil 640fb0e74195791501fd1ed57b41487f
    ln -sv pencil a2a266d0498c3104214a47bd64ab0fc8
    ln -sv pencil b66166c04f8c3109214a4fbd64a50fc8


    ln -sv circle crossed_circle
    ln -sv circle dnd_no_drop
    ln -sv circle X_cursor
    ln -sv circle x-cursor
    ln -sv circle forbidden
    ln -sv circle no-drop
    ln -sv circle not-allowed
    ln -sv circle pirate
    ln -sv circle 03b6e0fcb3499374a867c041f52298f0

    ln -sv cross crosshair
    ln -sv cross tcross
    ln -sv cross color-picker
    ln -sv cross cross_reverse
    ln -sv cross diamond_cross

    ln -sv bottom_left_corner fd_double_arrow
    ln -sv bottom_left_corner ll_angle
    ln -sv bottom_left_corner top_right_corner
    ln -sv bottom_left_corner ur_angle
    ln -sv bottom_left_corner ne-resize
    ln -sv bottom_left_corner nesw-resize
    ln -sv bottom_left_corner size_bdiag
    ln -sv bottom_left_corner sw-resize
    ln -sv bottom_left_corner fcf1c3c7cd4491d801f1e1c78f100000

    ln -sv bottom_right_corner bd_double_arrow
    ln -sv bottom_right_corner lr_angle
    ln -sv bottom_right_corner top_left_corner
    ln -sv bottom_right_corner ul_angle
    ln -sv bottom_right_corner nw-resize
    ln -sv bottom_right_corner nwse-resize
    ln -sv bottom_right_corner se-resize
    ln -sv bottom_right_corner size_fdiag
    ln -sv bottom_right_corner c7088f0f3e6c8088236ef8e1e3e70000

    ln -sv bottom_side bottom_tee
    ln -sv bottom_side plus
    ln -sv bottom_side sb_down_arrow
    ln -sv bottom_side sb_up_arrow
    ln -sv bottom_side sb_v_double_arrow
    ln -sv bottom_side top_side
    ln -sv bottom_side top_tee
    ln -sv bottom_side cell
    ln -sv bottom_side double_arrow
    ln -sv bottom_side down-arrow
    ln -sv bottom_side n-resize
    ln -sv bottom_side ns-resize
    ln -sv bottom_side row-resize
    ln -sv bottom_side s-resize
    ln -sv bottom_side up-arrow
    ln -sv bottom_side v_double_arrow
    ln -sv bottom_side size_ver
    ln -sv bottom_side 00008160000006810000408080010102
    ln -sv bottom_side 2870a09082c31050810ffdffffe0204

    ln -sv left_side left_tee
    ln -sv left_side right_side
    ln -sv left_side right_tee
    ln -sv left_side sb_h_double_arrow
    ln -sv left_side sb_left_arrow
    ln -sv left_side sb_right_arrow
    ln -sv left_side col-resize
    ln -sv left_side ew-resize
    ln -sv left_side h_double_arrow
    ln -sv left_side left-arrow
    ln -sv left_side right-arrow
    ln -sv left_side size-hor
    ln -sv left_side size-ver
    ln -sv left_side split_h
    ln -sv left_side split_v
    ln -sv left_side w-resize
    ln -sv left_side size_hor
    ln -sv left_side 028006030e0e7ebffc7f7070c0600140
    ln -sv left_side 14fef782d02440884392942c1120523 

    ln -sv dotbox dot_box_mask
    ln -sv dotbox draped_box
    ln -sv dotbox icon
    ln -sv dotbox target

    cd $start_path
    #这两种鼠标指针很少人会去做，所以就不转换了
    #if [ -z "$cur_pin" ];then
    #    echo cur_pin不存在,补全中
    #    cp $start_path/win2xcur-source/
    #else
    #    echo cur_pin存在
    #    cp -ifv "$cur_pin" $start_path/win2xcur-tmp/cursors-tmp/pin.ani
    #    win2xcur $start_path/win2xcur-tmp/cursors-tmp/pin.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    #fi

    #if [ -z "$cur_person" ];then
    #    echo cur_person不存在,补全中
    #    cp $start_path/win2xcur-source/
    #else
    #    echo cur_person存在
    #    cp -ifv "$cur_person" $start_path/win2xcur-tmp/cursors-tmp/person.ani
    #    win2xcur $start_path/win2xcur-tmp/cursors-tmp/person.ani -o $start_path/win2xcur-tmp/"$cur_name"/cursors
    #fi

    echo "为鼠标指针生成配置文件"
    echo "[Icon Theme]" > cursor.theme
    echo "Name="$cur_name"" >>cursor.theme
    echo "Inherits="$cur_name"" >>cursor.theme
    echo "[Icon Theme]" > index.theme
    echo "Name="$cur_name"" >> index.theme
    echo "Comment="$cur_name" cursors for linux" >> index.theme
    echo "Inherits=hicolor" >> index.theme
    mv -fv cursor.theme $start_path/win2xcur-tmp/"$cur_name"
    mv -fv index.theme $start_path/win2xcur-tmp/"$cur_name"

    echo "清理缓存文件中"
    mv -fv $start_path/win2xcur-tmp/"$cur_name" $start_path_/
    rm -rfv $start_path/win2xcur-tmp
    echo "转换完成"
}

###############################################################################
if [ $(uname -o) = "Msys" ];then #为了兼容windows系统
    test_python="python"
else
    test_python="python3"
fi

if which "$test_python" > /dev/null ;then
    mainmenu
else
    echo "未安装python,请安装后重试"
    echo "正在退出"
    exit
fi