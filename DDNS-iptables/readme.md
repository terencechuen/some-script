# 0x01 前言  
因DDNS服务的关系，VPS上需要自动放行相关端口，DDNS服务相关文章参考以下链接：  
* [使用python脚本调用阿里DNS解析API以提供DDNS服务-v2](https://ngx.hk/2018/04/21/%E4%BD%BF%E7%94%A8python%E8%84%9A%E6%9C%AC%E8%B0%83%E7%94%A8%E9%98%BF%E9%87%8Cdns%E8%A7%A3%E6%9E%90api%E4%BB%A5%E6%8F%90%E4%BE%9Bddns%E6%9C%8D%E5%8A%A1-v2.html)  
  
关于该脚本的相关说明，请参考以下文章：  
* [通过python调用iptables放行DDNS的IP](https://ngx.hk/2018/08/11/%E9%80%9A%E8%BF%87python%E8%B0%83%E7%94%A8iptables%E6%94%BE%E8%A1%8Cddns%E7%9A%84ip.html)  
  
# 0x02 功能  
该脚本通过解析DDNS域名，获取指定记录类型下的IP地址，并调用iptables根据需要开放端口。目前可实现以下功能：  
1. 支持向特定的IP开放全部端口与协议；  
2. 支持向特定的IP开放多端口；  
3. 支持向特定的IP开放单一端口。  
  
iptables的命令如下：  
* 对1.1.1.1开放全部协议与端口：  
``iptables -A INPUT  -s 1.1.1.1 -j ACCEPT -m comment --comment "DDNS iptables rule"``  

* 对1.1.1.1开放TCP 80,8080,443端口：  
``iptables -A INPUT -p tcp -m multiport --dport 80,8080,443 -s 1.1.1.1 -j ACCEPT -m comment --comment "DDNS iptables rule"``  

* 对1.1.1.1开放TCP 80端口：  
``iptables -A INPUT -p tcp --dport 80 -s 1.1.1.1 -j ACCEPT -m comment --comment "DDNS iptables rule"``  
  
# 0x03 配置  
目前只支持单一域名，只需要修改 ``config.json`` 文件即可：  

```  
{  
  "domain": "ngx.hk",  
  "port": "10050,80,443,222",  
  "record": "a",  
  "proto": "udp"  
}  
```  
* domain：填写DDNS的域名；  
* port：支持单一或多端口，请使用英文字符的逗号 ``,`` 最为分隔符，请勿包含空格或其他字符；  
* record：填写需要解析的域名解析类型，默认为A记录，若设为其他类型，请确认解析出来的值为IP地址。  
* proto：支持TCP或UDP，若该变量设为 ``-1`` ，将对解析出来的IP开放全部端口。  
  
  