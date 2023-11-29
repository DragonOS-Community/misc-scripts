# info-spider

一个用于调用github官方api以获取社区仓库信息的脚本

	##  使用方式

本脚本可以直接运行，也可以作为模块被导入

### Requirements

需要有python运行环境并安装依赖库

```shell
pip3 install -r requirements.txt
```

### **配置说明**

* 若需更改文件输出及配置文件路径，可通过更改脚本中PATH变量的值，若为空则默认为脚本同一目录下

```python
PATH = " 这里填写文件输出以及配置文件路径 "
```

* 使用者需要在config.json中填写如下选项以更好的使用脚本
  * **user** : 社区用户名，默认为DragonOS-Community
  * **token** : 使用者的[github token](https://github.com/settings/tokens)，用以增加访问访问次数(若不使用token则有每小时60次的访问限制，[查看详情](https://docs.github.com/zh/rest/overview/rate-limits-for-the-rest-api))
  * **parallel_threads** : 最大并行线程数
  * **black_list** : 仓库获取黑名单，列表中填写仓库的名称用于忽略该仓库中的contributor信息
  * **white_list** : 黑名单中的白名单，列表中填写用户名，黑名单中的仓库会忽略除了白名单中的contributor

### 直接运行

使用命令行执行脚本生成.json文件以及.xls文件

```shell
python main.py
```

### 作为模块导入

可以调用模块中的get_json()和get_dict()

* **get_dict()** : 返回带有社区信息的python字典
* **get_json()** : 返回带有社区信息的json文本

## 添加统计条目

如果后期需要添加社区仓库的统计条目，需要做以下改动

1. 编写统计函数，参数为仓库信息字典，返回值字典{"条目名称":条目数据}，并在脚本头部的**function_list**中填写函数名
2. 将上述条目名称在脚本头部的head1中，作为最终输出在excel中的表头

## TODO

如果后期需要可以考虑进一步封装脚本