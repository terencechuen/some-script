## 0x01 使用场景
该脚本主要用于更新Cachet的图表。    
该脚本分为两个主要的功能:  
1. 作为zabbix的告警脚本，当发生zabbix告警时会被zabbix server调用，脚本会更新cachet相关组件的状态；  
2. 最为主动式的脚本从elasticsearch中获取指定索引的日志数量并更新cachet的图表。  

展示页面请浏览：[NGX Services Status](https://status.ngx.hk)

## 0x02 依赖
本脚本使用python3编写，需要安装以下依赖包
* requests    

可通过以下命令安装：    
    
    pip3 install requests

## 0x03 elasticsearch_script 配置文件
* config_main：请填写cachethq的API地址与API Key
* config：以列表的形式记录数据源的信息，支持多个数据源，脚本会自动遍历该列表，根据配置信息逐一更新Cachet的图表
  * es6_api_url：请填写elasticsearch的API地址；  
  * metric_id：cachet图表的id；  
  * es6_index：请填写elasticsearch index的名称。  
  
## 0x04 zabbix_script 配置文件  
* config_main：请填写cachethq的API地址与API Key  
* host：该字段为字典，key为zabbix host配置中的hostname；value为cachet中对应组件的id；  
* alarm_level：zabbix告警等级的数字化表示，关系如下：  
  * 0：zabbix告警等级为Not classified 或 Information，cachet组件的状态会根据alarm_level值的不同而有不同动作；  
  * 1：zabbix无告警，cachet组件显示为"运行正常"；  
  * 2：zabbix告警等级为Warning，cachet组件显示为"负载较高"；  
  * 3：zabbix告警等级为Average，cachet组件显示为"Partial Outage"； 
  * 4：zabbix告警等级为High 或 Disaster，cachet组件显示为"Major Outage"。  
  
如果alarm_level的值设置为-1，那么告警等级0会加2，zabbix的Not classified 或 Information告警会在cachet中显示为"负载较高"，如果alarm_level的值设置为0，则告警等级为0的告警会被忽略，cachet不会有任何改变。  
  
我们可以将常见但低危的告警设置为Not classified 或 Information，这样就不会在cachet中显示，避免不必要的麻烦。  

## 0x05 elasticsearch_script 运行
该脚本直接执行即可：    
    
    /usr/bin/python3 ./main.py    
    
建议将其加入crontab，实现自动更新，如：    
    
    */1 * * * * root /usr/bin/python3 /usr/local/services_data/shell/cachethq/main_temp.py  
  
## 0x06 zabbix_script 运行  
该脚本不可直接执行，需配合zabbix使用，具体请参考以下链接：  
* [通过python脚本与zabbix互动并更新Cachet的设备状态与添加事件记录](https://ngx.hk/2018/11/08/%E9%80%9A%E8%BF%87python%E8%84%9A%E6%9C%AC%E4%B8%8Ezabbix%E4%BA%92%E5%8A%A8%E5%B9%B6%E6%9B%B4%E6%96%B0cachet%E7%9A%84%E8%AE%BE%E5%A4%87%E7%8A%B6%E6%80%81%E4%B8%8E%E6%B7%BB%E5%8A%A0%E4%BA%8B%E4%BB%B6.html)
  
## 0x07 其他
脚本中elasticsearch的query payload仅在ES6中测试过，仅能统计指定索引在最近一分钟内的请求数。    
我的应用场景是为了统计nginx的请求数，因为每次访问都会产生一条日志，而在elasticsearch里则是一个条目，所以计算出的数量即为请求数。
