#!/bin/bash

# python命令
ani_pyhton()
{
    "$ani_python_path" "$@"
}

# pip命令
ani_pip()
{
    ani_pyhton -m pip "$@"
}