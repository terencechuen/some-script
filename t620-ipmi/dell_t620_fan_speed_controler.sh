#!/bin/sh
ipmi_host=""
ipmi_user="root"
ipmi_passwd=""
temp_threshold="65"

get_value=`ipmitool -I lanplus -H $ipmi_host -U $ipmi_user -P $ipmi_passwd sensor reading "Temp" | cut -d "|" -f 2 | cut -d " " -f 2`

if [[ $get_value > $temp_threshold ]]
  then
    ipmitool -I lanplus -H $ipmi_host -U $ipmi_user -P $ipmi_passwd raw 0x30 0x30 0x01 0x01
  else
    ipmitool -I lanplus -H $ipmi_host -U $ipmi_user -P $ipmi_passwd raw 0x30 0x30 0x01 0x00
    ipmitool -I lanplus -H $ipmi_host -U $ipmi_user -P $ipmi_passwd raw 0x30 0x30 0x02 0xff 0x1e
fi