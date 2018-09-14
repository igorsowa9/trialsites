/usr/sbin/service ntp stop
/usr/sbin/ntpdate ntp1.rwth-aachen.de >>/home/iso/trialsites/ntplog.txt 2>&1
/usr/sbin/service ntp start

