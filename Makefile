test:
	#cat short_file.txt | ./kanten.py
	./kanten.py -c 10 short_file.txt
	#./kanten.py -w 30 short_file.txt
	#./kanten.py -w 30 short_file.txt
	#cat kanten.py | ./kanten.py
	./kanten.py kanten.py
	./kanten.py -w 30 kanten.py
	./kanten.py -c 10 -w 30 kanten.py
	nosetests

mem:
	while [ true ] ; do ps -o 'rss pmem' -p `ps ax | grep kanten | grep Python | grep -v grep | cut -f 1 -d\ ` ; sleep  1; done

big bigfile:
	kanten /var/log/wifi.log
