#!/bin/env bash
# 上传图片至阿里云oss，markdown图床
oss_url="oss://nsfoxer-oss/img"
url="nsfoxer-oss.oss-cn-beijing.aliyuncs.com/img"
err_img="${url}/error.png"

# 获得当前脚本执行路径
if [[ ${0} =~ "/" ]]; then
	location="${0%/*}" 
else
	location="$(pwd)"
fi

# http检测：如果是http(s)的话，应该先下载，再上传
http_check(){
	if [[ ${file%%:*} == "http" || ${file%%:*} == "https" ]]; then
		# 判断该地址是否已经是oss阿里云的
		if [[ "${file}" =~ "${url}" ]]; then
			echo ${file}
			exit 0
		fi
		# 否则下载该图片
		file_loc="${dir}/${pre_pic}.png"
		if command -v wget > /dev/null 2>&1; then
			echo "wget"
			echo "$file_loc"
			wget ${file} -O ${file_loc} > /dev/null 2>&1
		elif command -v curl > /dev/null 2>&1; then
			echo "curl"
			curl ${file} -o ${file_loc} > /dev/null 2>&1
		else
			echo "could not find a http(s) downloader" >&2
			exit 1
		fi
		file=${file_loc}
	fi
}

# 本地图片上传
pic_upload() {
	# 查询是否已存在该图片
	pic_md5=$(md5sum ${file} | awk '{print $1}')
	pic_status=$("${location}/ossutil" ls "${oss_url}/${pic_md5}.png" | grep "Object Number is:" | awk '{print $4}')
	if [[ ${pic_status} -eq 0 ]]; then
	# 不存在图片
		# 不对gif图片使用imagemagic给图片添加阴影
		filetype=${file##*.}
		if [[ ${filetype} == "png" || ${filetype} == "jpg" ]]; then
			convert "${file}" \( +clone -background black -shadow 60x6+5+5 \) +swap -background white -layers merge +repage "${file}"
			# png图片体积较大，此处将其转为webp格式
			if [[ ${filetype} == "png" ]]; then
				temp_file=${file}
				file="${file%.*}.webp"
				filetype="webp"
				convert ${temp_file} "${file}"
			fi
		fi
		"${location}/ossutil" cp ${file} "${oss_url}/${pic_md5}.${filetype}" > /dev/null
	else
		echo "${file} is existed"
	fi

	if [[ $? == 0 ]]; then
		echo "https://${url}/${pic_md5}.${filetype}"
	else
		echo "https://${err_img}"
	fi
}

# main
dir=$(mktemp -d)
for file in "$@"
do
	pre_pic=$(date +%s%N) # 纳秒级时间戳
	http_check
	pic_upload
done
rm -rf "${dir}"
