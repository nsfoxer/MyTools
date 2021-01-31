# cnblog

[toc]

## 简介

​		这是一个cnblog的本地博客自动上传工具。使用python编写，相比其他的博客上传，依赖简单。这个工具参考[cnblogs_automatic_blog_uploading](https://github.com/nickchen121/cnblogs_automatic_blog_uploading)。程序没有使用参考所用的githook，而是建立本地数据，追踪新博客和已修改的博客。

## 功能

- 批量化上传
- 根据文件路径生成相应的标签
- 能够追踪到未上传的本地博客，已更新的本地博客

## 安装

```shell
pip3 install --user pypi-xmlrpc datetime json time argparse
wget "https://raw.githubusercontent.com/muwuren/MyTools/main/cnblog_upload/cnblog.py"
```

## 使用

```shell
$ python cnblog.py -h
usage: cnblogs [-h] [-d DEPTH] location

本地博客同步

positional arguments:
  location

optional arguments:
  -h, --help            show this help message and exit
  -d DEPTH, --depth DEPTH
                        category start serial

程序将扫描指定的路径，指定路径位置深度0，忽略深度不足的文件，选择所有非隐藏文件夹下的md(markdown)文档上传。
程序从足够深度的位置开始，将文件的文件夹路径视为标签上传。具有相同文件名和相同标签的文件被视为同一文件。具体请看README.md。
```

### 具体说明

1. -d：指定从location位置开始，忽略的文件深度。
2. location： 指定搜索的文件位置
3. 文件依赖depth和location决定其属性(标签)，相同文件名，但不同属性被视为不同文件
4. **文件属性不依赖路径的具体顺序。**

### 例

假设有如下的目录：

![image-20210130140200215](https://nsfoxer-oss.oss-cn-beijing.aliyuncs.com/img/a0d0f480d51d15b712bd4e77ab707122.png)

1. 所有md文件均有内容

   在当前`hello`路径下执行`python cnblog.py -d 0 ./`时，将上传`hello`路径下，所有`md`和`markdown`后缀文件。

2. `hello`路径下的`[1-2].md`文件,属性为空。

   `hello/Two/Three`路径下`[1-2].md`文件，属性为`Two`和`Three`，与`hello`路径下的md文件被视为不同文件。**但是**，`hello/Three/Two`路径下的`[1-2].md`被看作相同文件，属性相同，均为`Two`和`Three`。具体上传哪个位置的文件，依赖python中`os.path.listdir()`具体实现。

## 已知问题

1. 如果运行时，出现任何错误，请下次运行前需要删除`$HOME/.config/cnblog/bloginfo.conf`文件。造成此的原因是异常退出，不会保存更新的信息，导致旧信息使用，会造成重复上传。
2. 每天最多更新（上传）100个博客，程序并未对此进行检测。可能会在未来更新中进行修复。