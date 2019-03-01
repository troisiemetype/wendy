#!/bin/bash

#parameters
stopState=1
rebootState=1
stopPinNumber=0
rebootPinNumber=2
refresh=1

gpio mode $stopPinNumber in
gpio mode $stopPinNumber up
gpio mode $rebootPinNumber in
gpio mode $rebootPinNumber up

while (true); do
	stopState=$(gpio read $stopPinNumber)
	rebootState=$(gpio read $rebootPinNumber)

	if [ $stopState -eq 0 ] ; then
		sleep $refresh
		sleep $refresh
		stopState=$(gpio read $stopPinNumber)

		if [ $stopState -eq 0 ] ; then
			echo `sudo halt`
		fi
	fi

	if [ $rebootState -eq 0 ] ; then
		sleep $refresh
		sleep $refresh
		rebootState=$(gpio read $rebootPinNumber)

		if [ $rebootState -eq 0 ] ; then
			echo `sudo reboot`
		fi
	fi
	sleep $refresh

done
