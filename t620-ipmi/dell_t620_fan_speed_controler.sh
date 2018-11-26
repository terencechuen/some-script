#!/bin/sh
ipmi_host=""
ipmi_user=""
ipmi_passwd=""

snmp_host=""
snmp_ver="2c"
snmp_com="public"

# 值为温度乘以10，如60摄氏度的值为600
# 温度警戒线，当超过该温度则启动自动温度控制，否则强制风扇转速在30%
temp_threshold="600"

# 检查是否已安装依赖包
if [ `rpm -qa | grep ^bc | wc -l` == 0 ]
then
	echo "You need to install bc to perform arithmetic calculations."
	echo "You can try \"yum install bc -y\""
	exit 2
fi

get_cpu1_temp=`snmpwalk -v $snmp_ver -c $snmp_com $snmp_host SNMPv2-SMI::enterprises.674.10892.5.4.700.20.1.6.1.2 | cut -d " " -f 4`
get_cpu2_temp=`snmpwalk -v $snmp_ver -c $snmp_com $snmp_host SNMPv2-SMI::enterprises.674.10892.5.4.700.20.1.6.1.3 | cut -d " " -f 4`

calc_avg_temp=`echo "($get_cpu1_temp + $get_cpu2_temp)/2" | bc`

if [ `echo "$calc_avg_temp > $temp_threshold" | bc ` == 1 ]
then
  ipmitool -I lanplus -H $ipmi_host -U $ipmi_user -P $ipmi_passwd raw 0x30 0x30 0x01 0x01
else
  ipmitool -I lanplus -H $ipmi_host -U $ipmi_user -P $ipmi_passwd raw 0x30 0x30 0x01 0x00
  ipmitool -I lanplus -H $ipmi_host -U $ipmi_user -P $ipmi_passwd raw 0x30 0x30 0x02 0xff 0x1e
fi
