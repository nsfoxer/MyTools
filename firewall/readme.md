# Deny_Scan

[toc]



## 介绍

服务器经常被扫描，查看日志会发现大量的扫描记录。Deny_scan会对失败次数过多的ip进行拦截。

## 功能

- 拦截潜在的扫描ip地址

## 安装

### 依赖安装

程序依赖`ufw`的拦截记录

```bash
# pacman -S ufw
```

### 要求

1. 要求`ufw`的日志输出在`journalctl`的`kernel`中，且拦截以`[UFW BLOCK]`开头。

   如下所示：`sudo journalctl -rk`中：

   ![image-20211112155002256](https://nsfoxer-oss.oss-cn-beijing.aliyuncs.com/img/2134d35b5f277e2266290bf28b48ca4d.png)

   此输出定义于`/etc/ufw/user.rules`中：

   ```ini
   ......
   
   ### LOGGING ###
   -A ufw-after-logging-input -j LOG --log-prefix "[UFW BLOCK] " -m limit --limit 3/min --limit-burst 10
   -A ufw-after-logging-forward -j LOG --log-prefix "[UFW BLOCK] " -m limit --limit 3/min --limit-burst 10
   -I ufw-logging-deny -m conntrack --ctstate INVALID -j RETURN -m limit --limit 3/min --limit-burst 10
   -A ufw-logging-deny -j LOG --log-prefix "[UFW BLOCK] " -m limit --limit 3/min --limit-burst 10
   -A ufw-logging-allow -j LOG --log-prefix "[UFW ALLOW] " -m limit --limit 3/min --limit-burst 10
   ### END LOGGING ###
   
   ......
   ```

## 使用

```shell
$ sudo python deny_scan.py
```

## 说明

- Deny_scan会生成ip.db，来对ip信息进行持久化保存
- 退出程序时，Ctrl+c