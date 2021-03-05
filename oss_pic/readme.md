# README

[toc]

## 介绍

​	typora图片上传功能配合+ picgo + 阿里云oss存储虽然很方便，但是picgo体积太大（Emm，由于npm下载速度太慢）。这里使用轻量级的阿里云官方提供的ossutil程序，配合shell脚本实现图片上传。

## 功能

- 上传本地图片
- 上传其他http图片
- 给图片增加阴影效果

## 安装

找到一个合适的地方

```bash
git clone https://github.com/muwuren/ossutil_picture
```

初始化运行（用来初始化ossutil的，以及上传error.png）

```bash
$ ./init.sh
```

## 配置

在typora配置中，自定义命令选择程序oss_upload.sh（例：~/mbin/oss_pic/oss_upload.sh）

![image-20200727234008660](https://nsfoxer-oss.oss-cn-beijing.aliyuncs.com/img/1595864408777727142.png)

