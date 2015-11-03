#!/bin/sh
cp -r `ls | grep -v build | xargs` ./build && cd ./build && rm -rf logs && rm -rf config_base.py && rm -rf config_api.py && rm -rf config_wap.py && \cp -rf * ../../tubban_user_v1/