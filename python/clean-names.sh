#! /bin/sh
#
[ -z $1 ] && echo "USAGE: $0 CSV_FILE > babynames.txt " 1>&2 && exit 1

sed "1d" "$1" | awk -F, '{print $2}' | sed 's/"//g'
