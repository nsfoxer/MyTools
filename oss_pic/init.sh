#!/bin/env bash

if [[ ! -f ~/.ossutilconfig ]]; then
	# 初始化ossutil
	./ossutil config
fi

# 初始化配置
read -p "请输入oss的地址（如：oss://nsfoxer-oss/img）: " oss_url
read -p "请输入url的地址（如：nsfoxer-oss.oss-cn-beijing.aliyuncs.com/img）: " url
sed -i "3s/^$/oss_url=${oss_url//\//\\\/}/g" ./oss_upload.sh
sed -i "4s/^$/oss_url=${url//\//\\\/}/g" ./oss_upload.sh

# 初始化error图片
./ossutil cp ./error.png ${oss_url}/error.png
