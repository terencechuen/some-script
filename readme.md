## 自用的多个小脚本，以下是各个目录的用途  
* **DDNS-iptables**：定时解析设定的域名以获取IP地址，然后调用iptables在INPUT链中追加规则。主要用于DDNS的域名，在云服务器上放行DDNS域名所指向的IP。  
以下是相关文章的链接：  
[通过python调用iptables放行DDNS的IP](https://ngx.hk/2018/08/11/%E9%80%9A%E8%BF%87python%E8%B0%83%E7%94%A8iptables%E6%94%BE%E8%A1%8Cddns%E7%9A%84ip.html)    
  
* **cachethq**：用于对接zabbix、elasticsearch与cachethq的脚本。可以被zabbix调用，实现在cachethq中添加事件记录与更新组建状态；可以主动统计elasticsearch中的日志数量，并将数据写入cachethq，从而形成图表。  
以下是相关文章的链接：  
[通过python脚本与zabbix互动并更新Cachet的设备状态与添加事件记录](https://ngx.hk/2018/11/08/%E9%80%9A%E8%BF%87python%E8%84%9A%E6%9C%AC%E4%B8%8Ezabbix%E4%BA%92%E5%8A%A8%E5%B9%B6%E6%9B%B4%E6%96%B0cachet%E7%9A%84%E8%AE%BE%E5%A4%87%E7%8A%B6%E6%80%81%E4%B8%8E%E6%B7%BB%E5%8A%A0%E4%BA%8B%E4%BB%B6.html)  
[通过python调用elasticsearch与Cachet的API实时更新Cachet图表](https://ngx.hk/2018/06/25/%E9%80%9A%E8%BF%87python%E8%B0%83%E7%94%A8elasticsearch%E4%B8%8Ecachet%E7%9A%84api%E5%AE%9E%E6%97%B6%E6%9B%B4%E6%96%B0cachet%E5%9B%BE%E8%A1%A8.html)  
  
* **email_handler**：读取指定邮箱中指定文件夹下的所有文件，并生成xml文件，用于统计参与抽奖报名人员的情况。  
以下是相关文章的链接：  
[使用python脚本从邮箱中拉取邮件、处理并生成csv文件](https://ngx.hk/2018/11/10/%E4%BD%BF%E7%94%A8python%E8%84%9A%E6%9C%AC%E4%BB%8E%E9%82%AE%E7%AE%B1%E4%B8%AD%E6%8B%89%E5%8F%96%E9%82%AE%E4%BB%B6%E3%80%81%E5%A4%84%E7%90%86%E5%B9%B6%E7%94%9F%E6%88%90csv%E6%96%87%E4%BB%B6.html)  
  
* **jumpserver**：简单的jumpserver安装脚本，用于jumpserver的安装部署。因测试需要，需要不断重装，因过于繁琐才有这个脚本的产生。因只是测试之用，尚未有文章。  
  
* **nginx-status**：用于zabbix-agent获取nginx状态的一个脚本，尚未有文章。  
  
* **ngx-pxe-boot**：我家虚拟化环境的centos7的pxe引导文件与部署脚本。  
以下是相关文章的链接：  
[使用kickstart与tftp并通过网络启动centos7安装程序实现自动部署](https://ngx.hk/2018/11/18/%E4%BD%BF%E7%94%A8kickstart%E4%B8%8Etftp%E5%B9%B6%E9%80%9A%E8%BF%87%E7%BD%91%E7%BB%9C%E5%90%AF%E5%8A%A8centos7%E5%AE%89%E8%A3%85%E7%A8%8B%E5%BA%8F%E5%AE%9E%E7%8E%B0%E8%87%AA%E5%8A%A8%E9%83%A8%E7%BD%B2.html)  
  
* **random_draw**：用于抽奖的脚本，需要使用**email_handler**脚本生成的csv文件最为数据源。  
以下是相关文章的链接：  
[一个超级简单无尿点的python抽奖脚本](https://ngx.hk/2018/11/12/%E4%B8%80%E4%B8%AA%E8%B6%85%E7%BA%A7%E7%AE%80%E5%8D%95%E6%97%A0%E5%B0%BF%E7%82%B9%E7%9A%84python%E6%8A%BD%E5%A5%96%E8%84%9A%E6%9C%AC.html)  
  
* **raspberry_pi_sensor**：该脚本主要用于读取树莓派与arduino上传感器的数据。  
以下是相关文章的链接：  
[通过arduino让树莓派读取传感器的模拟信号](https://ngx.hk/2018/07/08/%E9%80%9A%E8%BF%87arduino%E8%AE%A9%E6%A0%91%E8%8E%93%E6%B4%BE%E8%AF%BB%E5%8F%96%E4%BC%A0%E6%84%9F%E5%99%A8%E7%9A%84%E6%A8%A1%E6%8B%9F%E4%BF%A1%E5%8F%B7.html)  
  
* **t620-ipmi**：使用该脚本可以通过IPMI调整Dell T620的散热风扇转速。脚本同样适用于Dell 12G的其他型号服务器，但可能需要修改某些参数。  
以下是相关文章的链接:  
[静音！通过IPMI调整Dell T620（12G）服务器散热风扇的转速](https://ngx.hk/2018/10/02/%E9%9D%99%E9%9F%B3%EF%BC%81%E9%80%9A%E8%BF%87ipmi%E8%B0%83%E6%95%B4dell-t620%EF%BC%8812g%EF%BC%89%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%95%A3%E7%83%AD%E9%A3%8E%E6%89%87%E7%9A%84%E8%BD%AC%E9%80%9F.html)  
