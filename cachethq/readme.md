## 使用场景
该脚本主要用于更新Cachet的图表。    
支持从zabbix中取某个item最新的数值与统计elasticsearch近一分钟内的日志数量，然后调用Cachet的API将数值插入图表中。

展示页面请浏览：[NGX Services Status](https://status.ngx.hk)

## 依赖
本脚本使用python3编写，需要安装以下依赖包
* requests    

可通过以下命令安装：    
    
    pip3 install requests

## 配置文件
* config_main：请填写cachethq的API地址与API Key
* config：以列表的形式记录数据源的信息，支持多个数据源，脚本会自动遍历该列表，根据配置信息逐一更新Cachet的图表
 * services：zabbix请使用zbx，elasticsearch请使用es6
 * api_url：请根据实际情况修改api的地址，只需要修改域名或IP即可

## 其他
脚本中elasticsearch的query payload仅在ES6中测试过，仅能统计指定索引在最近一分钟内的请求数。    
我的应用场景是为了统计nginx的请求数，因为每次访问都会产生一条日志，而在elasticsearch里则是一个条目，所以计算出的数量即为请求数。

## 运行
该脚本直接执行即可：    
    
    /usr/bin/python3 ./main_temp.py    
    
建议将其加入crontab，实现自动更新：    
    
    */1 * * * * root /usr/bin/python3 /usr/local/services_data/shell/cachethq/main_temp.py