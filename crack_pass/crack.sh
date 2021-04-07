#!/bin/bash

if [[ $# -ne 2 ]]; then
	echo "usage: $0 FILE PASSFILE"
	exit 1
fi

filename=$1
passfile=$2
if [[ ! -f "$filename" || ! -f "$passfile" ]]; then
	echo "${filename} or ${passfile} is not existed!"
	exit 2
fi
while read password
do
	echo "$password"
	7z e -p"$password" "${filename}" > /dev/null 2>&1
	if [[ $? -eq 0 ]]; then
		echo "password: $password"
		exit 0
	fi
done < "$passfile"
echo "NO PASSWORD"
exit 3
