#!/bin/bash

# --------------------
# default values
# --------------------
SLIDEFILE=/boot/slide.pdf
SLIDESTORE=/home/pi/pdfslideshow-images
# image resolution. 72->hd, 192->fullhd(but very slow)
RESOLUTION=96
SLIDESECOND=10
# --------------------

# if config file exists, load it.
ENVFILE=/home/pi/pdfslideshow.env
if [ -e $ENVFILE ] ; then
  source $ENVFILE
fi

# if slide exists then culculation md5sum.
if [ -e $SLIDEFILE ] ; then
  SLIDEHASH=`md5sum $SLIDEFILE | awk -F' ' '{print $1}'`
fi

# if slideimage directory does not exists then create it.
if [ ! -e $SLIDESTORE ] ; then
  mkdir -p $SLIDESTORE
fi

SLIDEIMG=$SLIDESTORE/$SLIDEHASH

DO_CONVERT=0
if [ ! -e $SLIDEIMG ] ; then
  # if slide image does not exists then do convert.
  mkdir -p $SLIDEIMG
  DO_CONVERT=1
else
  # https://qiita.com/stc1988/items/e3a1d7dccafe4ab573fa
  IMGCOUNT=`ls -F $SLIDEIMG | grep -v / | wc -l`
  # if $SLIDEIMG does not have image then do convert.
  if [ $IMGCOUNT == 0 ] ; then
    DO_CONVERT=1
  fi
fi

if [ $DO_CONVERT == 1 ] ; then
  /usr/bin/convert \
    -density $RESOLUTION -units PixelsPerInch \
    -limit memory 100MB \
    $SLIDEFILE $SLIDEIMG/slide-%03d.jpg
fi

/usr/bin/feh -F -D $SLIDESECOND --zoom max $SLIDEIMG

