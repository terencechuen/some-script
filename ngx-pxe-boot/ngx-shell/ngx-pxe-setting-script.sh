#/bin/sh

######## hostname ########
LOCAL_IPADDR=`hostname -I | cut -d ' ' -f 1`
PTR_ANSWER=`dig +short -x $LOCAL_IPADDR`

if [ -z $PTR_ANSWER ] ; then
	hostnamectl set-hostname $(cat /sys/class/net/ens192/address | sed 's/://g' | cut -c 7-12)
else
	hostnamectl set-hostname $(cat $PTR_ANSWER | cut -d '.' -f 1)
fi

sed -i '/.*ngx-pxe-setting-script\.sh.*/d' /etc/rc.local

rm -f /etc/yum.repos.d/Centos*.repo
yum clean all
yum install -y iftop htop python-pip python34-pip python34-devel python34 bash-completion bash-completion-extras vim

