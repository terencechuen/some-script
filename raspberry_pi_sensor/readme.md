## 前言
该脚本主要用于读取树莓派与arduino上传感器的数据。

## 使用方法
脚本需要在树莓派上运行。脚本分两部分。
其中根目录下的``main.py``使用python3运行，主要读取连接在树莓派上的温湿度传感器与火焰传感器的数值，具体功能如下：    
``
python3 main.py [tem|hum|flame] [pin_id]
``    

``voltage``目录下的``main.py``使用python2运行，主要读取arduino上电压传感器的数据:    
``
python2 ./voltage/main.py [pin_id]
``    

## 相关链接：
1. [通过arduino让树莓派读取传感器的模拟信号](https://ngx.hk/2018/07/08/%E9%80%9A%E8%BF%87arduino%E8%AE%A9%E6%A0%91%E8%8E%93%E6%B4%BE%E8%AF%BB%E5%8F%96%E4%BC%A0%E6%84%9F%E5%99%A8%E7%9A%84%E6%A8%A1%E6%8B%9F%E4%BF%A1%E5%8F%B7.html)