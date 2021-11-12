# README

[toc]

## 介绍

​	typora图片上传功能配合+ picgo + 阿里云oss存储虽然很方便，但是picgo体积太大（Emm，由于npm下载速度太慢）。这里使用轻量级的阿里云官方提供的ossutil程序，配合shell脚本实现图片上传。

## 功能

- 上传本地图片
- 上传其他http图片
- 给图片增加阴影效果,使其看起来有立体感（☺）
- 将png转为webp，降低文件体积

## 依赖

- imagemagick

## 安装

1. 安装依赖：

   ```shell
   # archlinux 系列发行版
   sudo pacman -S imagemagick
   ```

2. 找到一个合适的地方
   

    ```bash
    git clone https://github.com/muwuren/ossutil_picture
    ```
    
3. 初始化运行（用来初始化ossutil的，以及上传error.png）

    ```bash
    $ ./init.sh
    ```

## 配置

在typora配置中，自定义命令选择程序oss_upload.sh（例：~/mbin/oss_pic/oss_upload.sh）

![image-20210705110124977](https://nsfoxer-oss.oss-cn-beijing.aliyuncs.com/img/20c7de0247fdf86fc1d5263f4bd69f0f.png)

## 问题

2021年 08月 24日 发现，当上传的图片路径带空格时，无法正确处理。需修复。

