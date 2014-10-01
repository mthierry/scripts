#!/bin/sh
# fetch an 'mbox' patch from patchwork (optionally, git am it)
# usage: fetch-patch.sh <number(s)>
# example: 'fetch-patch.sh 32310' will get the patch from http://patchwork.freedesktop.org/patch/32310/
# optional: To also apply the patch, use fetch-patch.sh am <patch-number(s)>
am=0
for patchnumber in $@;
do
	if [ $patchnumber = "am" ]
	then
		am=1
		continue
	fi

	wget -nv http://patchwork.freedesktop.org/patch/$patchnumber/mbox/ -O fetchedpatch-$patchnumber.patch

	if [ $am = "1" ]
	then
		git am -s fetchedpatch-$patchnumber.patch
		rm fetchedpatch-$patchnumber.patch
	fi
done
