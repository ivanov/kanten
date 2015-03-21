test:
	cat kanten.py | ./kanten.py
	nosetests

mem:
	while [ true ] ; do ps -o 'rss pmem' -p `ps ax | grep kanten | grep Python | grep -v grep | cut -f 1 -d\ ` ; sleep  1; done

big bigfile:
	kanten /var/log/wifi.log
