#/bin/sh

######## hostname ########
PTR_ANSWER=`dig +short -x 10.1.1.141`

if [ -z $PTR_ANSWER ] ; then
	hostnamectl set-hostname $(cat /sys/class/net/ens192/address | sed 's/://g' | cut -c 7-12)
else
	hostnamectl set-hostname $(cat $PTR_ANSWER | cut -d '.' -f 1)
fi

sed -i '/.*ngx-pxe-setting-script\.sh.*/d' /etc/rc.local

