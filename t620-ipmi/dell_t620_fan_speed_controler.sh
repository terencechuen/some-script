#!/bin/sh
ipmi_host=""
ipmi_user=""
ipmi_passwd=""

snmp_host=""
snmp_ver="2c"
snmp_com="public"

# 三个温度值将转速划分为四个区间
temp_threshold="56,60,65"
fan_speed="30,50,70,100"

#日志文件路径
log_path='t620_ipmi_fan_speed_controller.log'

# 检查是否已安装bc
if [ ! `rpm -qa | grep -e ^bc -e net-snmp-utils | wc -l` -eq 2 ]; then
	echo "You need to install bc and net-snmp-utils."
	echo "You can try \"yum install bc net-snmp-utils -y\""
	exit 2
fi

# 获取当前的CPU温度
get_cpu1_temp=`snmpwalk -v $snmp_ver -c $snmp_com $snmp_host SNMPv2-SMI::enterprises.674.10892.5.4.700.20.1.6.1.2 | cut -d " " -f 4`
get_cpu2_temp=`snmpwalk -v $snmp_ver -c $snmp_com $snmp_host SNMPv2-SMI::enterprises.674.10892.5.4.700.20.1.6.1.3 | cut -d " " -f 4`

# 获取当前进气温度，用于写入日志
inlet_temp=`snmpwalk -v $snmp_ver -c $snmp_com $snmp_host SNMPv2-SMI::enterprises.674.10892.5.4.700.20.1.6.1.1 | cut -d " " -f 4`

# 计算CPU温度均值
calc_avg_temp=`echo "($get_cpu1_temp + $get_cpu2_temp)/20" | bc`

# 确定温度区间
temp_arr=(${temp_threshold//,/ })
if [ `echo "$calc_avg_temp > ${temp_arr[2]}" | bc` -eq 1 ]; then
	speed_range=3
elif [ `echo "$calc_avg_temp > ${temp_arr[1]}" | bc` -eq 1 ]; then
	speed_range=2
elif [ `echo "$calc_avg_temp > ${temp_arr[0]}" | bc` -eq 1 ]; then
	speed_range=1
else
	speed_range=0
fi

fan_speed_arr=(${fan_speed//,/ })
speed_hex="0x"$(echo "obase=16; ${fan_speed_arr[$speed_range]}" | bc)
inlet_temp=$(expr $inlet_temp / 10)
fan_speed=${fan_speed_arr[$speed_range]}%

# 判断日志文件是否存在
if [ -f $log_path ]; then
	# 获取最后一条日志中的转速区间值
	fan_speed_now=$(echo `tail -n 1 $log_path` | cut -d '=' -f 4 | cut -d ' ' -f 1)

	# 若目标区间值大于最后一条日志中的区间值，则立即上调转速，然后写入日志并退出程序
	if [ "$speed_range" -gt "$fan_speed_now" ]; then
		ipmitool -I lanplus -H $ipmi_host -U $ipmi_user -P $ipmi_passwd raw 0x30 0x30 0x02 0xff $speed_hex
		echo "`date '+%Y-%m-%d %H:%M:%S'` cpu_temp=$calc_avg_temp inlet_temp=$inlet_temp fan_speed_range=$speed_range fan_speed=$fan_speed msg=\"Cooling fan increases speed\"" >> $log_path
		exit 0
	elif [ "$speed_range" -eq "$fan_speed_now" ]; then
		echo "`date '+%Y-%m-%d %H:%M:%S'` cpu_temp=$calc_avg_temp inlet_temp=$inlet_temp fan_speed_range=$fan_speed_now fan_speed=$fan_speed msg=\"Cooling fan maintains speed\"" >> $log_path
		exit 0
	else
		# 获取最后5条日志中的CPU温度值并计算均值
		for i in $(tail -n 5 $log_path);
		do
			i_tmp=`echo $i | sed -e 's/^cpu_temp=\(.*\)/\1/g;t;d'`
			if [ $i_tmp ]; then
				if [ $last_few_min_cpu_temp_avg ]; then
					last_few_min_cpu_temp_avg=`echo "($last_few_min_cpu_temp_avg + $i_tmp)/2" | bc`
				else
					last_few_min_cpu_temp_avg=$i_tmp
				fi
			fi
		done
	fi
else
	# 若日志文件不存在，则立即调整转速并写入日志
	ipmitool -I lanplus -H $ipmi_host -U $ipmi_user -P $ipmi_passwd raw 0x30 0x30 0x02 0xff $speed_hex
	echo "`date '+%Y-%m-%d %H:%M:%S'` cpu_temp=$calc_avg_temp inlet_temp=$inlet_temp fan_speed_range=$speed_range fan_speed=$fan_speed msg=\"The log file does not exist, adjust the speed immediately\"" >> $log_path
	exit 0
fi

# 若日志文件存在，但需要降低转速，则需要进行判断温度是否在合适的范围
# 当 “(最近10分钟的温度均值-最新CPU温度均值)/最新CPU温度均值” 小于或等于0.05，方可降低转速
temp_calc=`echo "scale=2; ($last_few_min_cpu_temp_avg - $calc_avg_temp)/$calc_avg_temp" | bc`

if [ `echo "$temp_calc > 0.05" | bc` -eq 1 ]; then
	ipmitool -I lanplus -H $ipmi_host -U $ipmi_user -P $ipmi_passwd raw 0x30 0x30 0x02 0xff $speed_hex
	echo "`date '+%Y-%m-%d %H:%M:%S'` cpu_temp=$calc_avg_temp inlet_temp=$inlet_temp fan_speed_range=$speed_range fan_speed=$fan_speed msg=\"Cooling fan reduces speed, $temp_calc\"" >> $log_path
	exit 0
else
	echo "`date '+%Y-%m-%d %H:%M:%S'` cpu_temp=$calc_avg_temp inlet_temp=$inlet_temp fan_speed_range=$fan_speed_now fan_speed=$fan_speed msg=\"Waiting for the temperature drop, $temp_calc\"" >> $log_path
	exit 0
fi
