#!/bin/sh
ipmi_host=""
ipmi_user=""
ipmi_passwd=""

snmp_host=""
snmp_ver="2c"
snmp_com="public"

temp_threshold="60"

get_cpu1_temp=`snmpwalk -v $snmp_ver -c $snmp_com $snmp_host SNMPv2-SMI::enterprises.674.10892.5.4.700.20.1.6.1.2 | cut -d " " -f 4`
get_cpu2_temp=`snmpwalk -v $snmp_ver -c $snmp_com $snmp_host SNMPv2-SMI::enterprises.674.10892.5.4.700.20.1.6.1.3 | cut -d " " -f 4`

calc_avg_temp=`expr \( $get_cpu1_temp + $get_cpu2_temp \) \/ 2`

# get_value=`ipmitool -I lanplus -H $ipmi_host -U $ipmi_user -P $ipmi_passwd sensor reading "Temp" | cut -d "|" -f 2 | cut -d " " -f 2`

if [[ $calc_avg_temp > $temp_threshold ]]
then
  ipmitool -I lanplus -H $ipmi_host -U $ipmi_user -P $ipmi_passwd raw 0x30 0x30 0x01 0x01
else
  ipmitool -I lanplus -H $ipmi_host -U $ipmi_user -P $ipmi_passwd raw 0x30 0x30 0x01 0x00
  ipmitool -I lanplus -H $ipmi_host -U $ipmi_user -P $ipmi_passwd raw 0x30 0x30 0x02 0xff 0x1e
fi