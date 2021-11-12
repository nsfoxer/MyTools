#!/bin/env bash
# 多显示器设置
arg=$1
case "${arg}" in
	-n | --normal )
	xrandr --output HDMI-A-0 --mode 2560x1440  --scale 1x1 --pos 0x0 --output eDP --mode 2560x1600 --pos 2560x0 --scale 1x1
		;;
	-b | --big )
	xrandr --output HDMI-A-0 --mode 2560x1440  --scale 0.5x0.5 --pos 0x0 --output eDP --mode 2560x1600 --pos 1280x0 --scale 1x1
		;;
	-s | --small )
	xrandr --output HDMI-A-0 --mode 2560x1440  --scale 1.5x1.5 --pos 0x0 --output eDP --mode 2560x1600 --pos 3840x0 --scale 1x1
		;;
	-d | --dpi )
	xrandr --output HDMI-A-0 --mode 2560x1440  --scale 1.2x1.2 --pos 0x0 --output eDP --mode 2560x1600 --pos 3072x0 --scale 1x1
		;;
	-f | --off )
		xrandr --output HDMI-A-0 --off
		;;
	* )
		echo "need argument"
		exit 1
		;;
esac

feh --bg-fill --no-fehbg --randomize ~/Pictures/wallpapers/anime/

