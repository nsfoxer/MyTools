#!/bin/python
import xmlrpc.client as xmlrpclib
import json
import os
import sys
import time
import datetime
import argparse

class Config:
    blogid = ""
    username = ""
    passwd = ""
    appkey = ""
    url = ""

    server = ""
    blogsInfo = []
    categoriesInfo = []

    # 配置路径
    _cfg_path     = os.environ["HOME"] + "/.config/cnblogs/"
    _user_cfg     = _cfg_path + "user.config"
    _bloginfo_cfg = _cfg_path + "bloginfo.conf"
    _category_cfg = _cfg_path + "category.conf"
    # 配置是否需要更新
    _bloginfo_update = 0
    _category_update = 0
    # blogInfo重写
    _blogsInfo = {}

    def __init__(self):
        if not os.path.exists(self._cfg_path):
            os.makedirs(self._cfg_path)
        if not os.path.exists(self._user_cfg):
            self._init_user_cfg()
        self._get_user_cfg()
        metablog = MetaWeblog(self.username, self.passwd, self.blogid, self.url)
        if not os.path.exists(self._bloginfo_cfg):
            self._init_bloginfo_cfg(metablog.getRecentPosts())
        self._get_bloginfo_cfg()
        if not os.path.exists(self._category_cfg):
            self._init_category_cfg(metablog.getCategories())
        self._get_category_cfg()

    def saveData(self):
        """
            需要更新文件时，更新配置
        """
        if self._bloginfo_update:
            print("start update blog")
            self._init_bloginfo_cfg(self.blogsInfo)
        if self._category_update:
            print("start update cate")
            self._init_category_cfg(self.categoriesInfo)

    def _init_user_cfg(self):
        userInfo = {}
        print("初始化用户配置信息")
        print("注意开启metaWeblog，位于博客设置最下面")
        print("请输入用户名：")
        username = input()
        print("请输入密码：")
        passwd = input()
        self.url = "https://rpc.cnblogs.com/metaweblog/" + username
        appkey = username
        server = xmlrpclib.ServerProxy(self.url)

        # 获取配置
        userBlog = server.blogger.getUsersBlogs(appkey, username, passwd)[0]
        print(userBlog)
        blogid = userBlog["blogid"]

        userInfo["username"] = username
        userInfo["passwd"]   = passwd
        userInfo["blogid"]   = blogid

        # 写入配置文件
        with open(self._user_cfg, mode="w") as f:
            f.writelines(json.dumps(userInfo) + "\n")
    def _get_user_cfg(self):
        with open(self._user_cfg, "r") as f:
            userInfo = json.loads(f.readline())
            self.username = userInfo["username"]
            self.passwd   = userInfo["passwd"]
            self.blogid   = userInfo["blogid"]
            self.appkey   = self.username
            self.url = "https://rpc.cnblogs.com/metaweblog/" + self.username

    def _init_bloginfo_cfg(self, blogsInfo):
        """
            初始化blog的配置。从cnblog更新所有博客的属性。标题与分类不相同的博客，属于不同博客。
            博客创建时间将被视为最后修改时间
        """
        self._write_blog_cfg(blogsInfo)
    def _write_blog_cfg(self, blogsInfo:list):
        with open(self._bloginfo_cfg, "w") as f:
            for info in blogsInfo:
                f.writelines(json.dumps(info) + "\n")
        return
    def _get_bloginfo_cfg(self):
        with open(self._bloginfo_cfg, "r") as f:
            for line in f.readlines():
                info = json.loads(line)
                self.blogsInfo.append(info)

    def _init_category_cfg(self, categories):
        with open(self._category_cfg, "w") as f:
            f.write(json.dumps(categories))
    def _get_category_cfg(self):
        with open(self._category_cfg, "r") as f:
            self.categoriesInfo = json.loads(f.read())

    # 未完成
    def _speed_find(self):
        """
            加快bloginfo信息查找(实际就是设计失误，目前懒得改)
        """
        for blog in self.blogsInfo:
            key = {}
            key[blog["title"]] = blog["categories"]
            value = 0
            self._blogsInfo

    def find_blog(self, title:str, categories:list) -> dict:
        """
            查找一个博客
        """
        for blog in self.blogsInfo:
            if blog["title"] != title:
                continue
            # print(blog)
            if len(blog["categories"]) == len(categories):
                for cate in categories:
                    if cate not in blog["categories"]:
                        continue
                return blog
        return {}

    def is_new_blog(self, title:str, categories:list[str]) -> bool:
        """
            判断是否为新博客。
        """
        if self.find_blog(title, categories):
            return False
        return True

    def add_blog(self, title:str, categories:list, date:str, postid:str):
        """
            增加一个新博客。
        """
        blog = {}
        blog["title"]       = title
        blog["categories"]  = categories
        blog["dateCreated"] = date
        blog["postid"]      = postid
        self.blogsInfo.append(blog)
        # 需要更新blog配置
        self._bloginfo_update = 1

        return
    def change_blog(self, title:str, categories:list, date:str):
        """
            改变一个博客
        """
        blog = self.find_blog(title, categories)
        if not blog:
            print("没有相关的blog")
            raise ValueError
        blog["dateCreated"] = date
        # 需要更新blog配置
        self._bloginfo_update = 1

    def is_new_category(self, cate:str) -> bool:
        """
            判断是否为新的分类
        """
        if cate not in self.categoriesInfo:
            return True
        return False
    def add_category(self, cate:str):
        """
            增加一个新的标签
        """
        self.categoriesInfo.append(cate)
        # 需要更新cate配置
        self._category_update = 1

class MetaWeblog:
    appKey = ""
    username = ""
    passwd = ""
    blogid = ""
    server = ""

    def __init__(self, username:str, passwd:str, blogid:str, url:str):
        self.username = username
        self.passwd = passwd
        self.blogid = blogid
        self.server = xmlrpclib.ServerProxy(url)

    def delPost(self, postid):
        self.server.blogger.deletePost(self.appKey, postid, self.username, self.passwd, True)

    def _category_lstrip(self, cate:str) -> str:
        """
            去除前缀的所有[]
            如："[123][456]789"返回"789"
        """
        if len(cate) == 0:
            return ""
        if cate[0]=='[' and cate[-1] == ']':
            return ""
        i = 0
        while cate[i] == '[':
            for c in cate[i:]:
                i += 1
                if c == ']':
                    break
        return cate[i:]

    def getCategories(self) -> list:
        categoriesInfo = self.server.metaWeblog.getCategories(self.blogid, self.username, self.passwd)
        categories = []
        for cate in categoriesInfo:
            a = self._category_lstrip(cate["title"])
            if len(a) != 0:
                categories.append(a)
        return categories

    def getRecentPosts(self) -> list:
        blogsInfo = []
        recentPosts = self.server.metaWeblog.getRecentPosts(self.blogid, self.username, self.passwd, 9999)
        for blog in recentPosts:
            info = {}
            info["title"] = blog["title"]
            info["categories"] = []
            try:
                for c in blog["categories"]:
                    c = self._category_lstrip(c)
                    if c:
                        info["categories"].append(c)
            except KeyError:
                info["categories"] = []
            info["dateCreated"] = str(blog["dateCreated"])
            info["postid"] = blog["postid"]
            blogsInfo.append(info)
        return blogsInfo

    def editPost(self, postid:str, filename:str, title:str, categories:list):
        post = {}
        with open(filename) as f:
            post["title"] = title
            temp_cate = categories[:]
            temp_cate.append("[Markdown]")
            post["categories"] = temp_cate # 格式测试
            post["description"] = f.read()
        self.server.metaWeblog.editPost(postid, self.username, self.passwd, post, True)

    def newPost(self, filename:str, title:str, categories:list, date:str) -> str:
        """
        return: postid
        """
        post = {}
        with open(filename, "r") as f:
            post["description"] = f.read()
        post["dateCreated"] = datetime.datetime.strptime(date, "%Y%m%dT%H:%M:00")
        temp_cate = categories[:]
        temp_cate.append("[Markdown]")
        post["categories"] = temp_cate # 格式测试
        post["title"] = title
        postid = self.server.metaWeblog.newPost(self.blogid, self.username, self.passwd, post, True)
        return postid

    def newCategory(self, name:str, description:str="") -> int:
        wpCate = {}
        wpCate["name"] = name
        wpCate["description"] = description
        wpCate["parent_id"] = 6
        return self.server.wp.newCategory(self.blogid, self.username, self.passwd, wpCate)

def init_arg():
    """
        初始化参数解析
    """
    parser = argparse.ArgumentParser(prog="cnblogs", description="本地博客同步", 
            epilog="程序将扫描指定的路径，指定路径位置深度0，忽略深度不足的文件，选择所有非隐藏文件夹下的md(markdown)文档上传。\n程序从足够深度的位置开始，将文件的文件夹路径视为标签上传。具有相同文件名和相同标签的文件被视为同一文件。具体请看README.md。")
    parser.add_argument('-d', '--depth', type=int, help="category start serial", default=0, nargs=1)
    parser.add_argument("location", type=str, default="./", nargs=1)
    # args = parser.parse_args(["-d", "0", "/home/nsfoxer/Documents/articles"])
    args = parser.parse_args()
    return args

def get_md(path:str, categories:list[str], depth:int) -> list[dict]:
    """
        获取指定路径下的所有markdown文件名，属性与路径
        depth达不到时，仅忽略文件与文件名(属性)
        return: [{},{}...]
    """
    # 调用错误，退出
    if not os.path.exists(path):
        print(path + " is not exist")
        sys.exit(1)

    mds_info = [] # 记录所有的md文件
    # 深度搜索遍历文件夹
    for name in os.listdir(path):
        md_info = {} # 记录单个文件信息
        temp_name = name[:] # 对现有的name进行备份
        name = os.path.join(path, name) # 填充name为完整路径
        # 排除隐藏文件或文件夹
        if temp_name[0] == ".":
            continue
        # name为普通文件
        if os.path.isfile(name):
            if depth > 0:
                # 深度不够，不记录文件
                continue
            # 排除非markdown文件
            suffix = os.path.splitext(name)[-1]
            if suffix != ".md" and suffix != ".markdown":
                continue
            # 忽略空文件
            if os.path.getsize(name) == 0:
                print("file " + name + " is empty!")
                continue
            # 记录文件的 文件名，属性，具体位置
            md_info["title"] = temp_name
            md_info["categories"] = categories
            md_info["location"] = name
            # md_info = {'title': 'index', 'categories': [], 'location': '/tmp/nsfoxer/firefox/cache2/index'}
            # 保存到全部的md信息中
            mds_info.append(md_info)
        # name为文件夹
        elif os.path.isdir(name):
            if depth > 0:
                # 深度不够，进行下一层文件夹遍历
                mds_info.extend(get_md(name, categories, depth-1))
            else:
                # 保存下一层文件夹的所有信息
                temp_cate = categories[:] # 使用另一份信息进行存储
                temp_cate.append(temp_name)
                mds_info.extend(get_md(name, temp_cate, depth-1))
    return mds_info

if __name__ == "__main__":
    path_arg = init_arg()
    cfg = Config()
    weblog = MetaWeblog(cfg.username, cfg.passwd, cfg.blogid, cfg.url)
    # for bloginfo in cfg.blogsInfo:
    #     print("delete " + bloginfo["title"] + "!")
    #     weblog.delPost(bloginfo["postid"])
    # sys.exit(1)
    mds_info = get_md(path_arg.location[0],[], path_arg.depth[0])
    for md_info in mds_info:
        # 新博客
        if cfg.is_new_blog(md_info["title"], md_info["categories"]):
            print(md_info["title"] + " is new!")
            # print(md_info)
            input("wait")
            # category 更新
            for cate in md_info["categories"]:
                if cfg.is_new_category(cate):
                    # catecary为新时，增加一个新的标签
                    weblog.newCategory(cate)
                    # 更新配置
                    cfg.add_category(cate)
            # 上传博客
            date = time.strftime("%Y%m%dT%H:%M:00", time.localtime())
            postid = weblog.newPost(md_info["location"], md_info["title"], md_info["categories"], date)
            # 更新配置
            cfg.add_blog(md_info["title"], md_info["categories"], date, postid)
        # 已有的博客
        else:
            bloginfo = cfg.find_blog(md_info["title"], md_info["categories"])
            # 判断是否已更新
            now_date = time.strftime("%Y%m%dT%H:%M:00", time.localtime(os.path.getmtime(md_info["location"])))
            if now_date > bloginfo["dateCreated"]:
                # 更新博客
                print(md_info["title"] + " update")
                weblog.editPost(bloginfo["postid"], md_info["location"], md_info["title"], md_info["categories"])
                # 更新配置
                cfg.change_blog(md_info["title"], md_info["categories"], now_date)
    # 由于del中不能使用open，所有__del__改用显式
    cfg.saveData()
