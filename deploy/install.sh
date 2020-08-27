#!/bin/bash
DIR=`dirname $0`
. "$DIR/config.sh"
SOURCE_DIR=`readlink -f $DIR/../`

echo "Install $SOURCE_DIR..."
if [ ! -d $ROOT_DIR ]
then
	mkdir -p $ROOT_DIR
fi
if [ ! -d $FCGI_DIR ]
then
	mkdir $FCGI_DIR
fi
if [ ! -d $ROOT_DIR/$LOG_DIR ]
then
	mkdir $ROOT_DIR/$LOG_DIR
fi
if [ ! -d $ROOT_DIR/$STATIC_DIR ]
then
	mkdir $ROOT_DIR/$STATIC_DIR
fi
ln -sfT $SOURCE_DIR $CURRENT_DIR
ln -sfT $SOURCE_DIR/$DEPLOY_DIR $ROOT_DIR/$DEPLOY_DIR

rm -rf $SOURCE_DIR/$STATIC_DIR/school_assets
yes | cp -rf $SOURCE_DIR/$STATIC_DIR/* $ROOT_DIR/$STATIC_DIR
rm -rf $SOURCE_DIR/$STATIC_DIR
ln -sfT $ROOT_DIR/$STATIC_DIR $SOURCE_DIR/$STATIC_DIR
#if [ -d $SOURCE_DIR/$STATIC_DIR ]
#then
#	ln -sfT $ROOT_DIR/$STATIC_DIR $SOURCE_DIR/$STATIC_DIR
#fi

for d in `cd $DIR;ls -d */`;
do
	project=${d%%/}
	if [ -f "$DIR/$project/config.sh" ]
	then
		. "$DIR/$project/config.sh"
		if [ ! -d $ROOT_DIR/$LOG_DIR/$MODULE ]
		then
			mkdir $ROOT_DIR/$LOG_DIR/$MODULE
		fi
		ln -sfT $ROOT_DIR/$LOG_DIR/$MODULE $SOURCE_DIR/$MODULE/log
	fi
done
find $SOURCE_DIR -name "requirements.txt" -exec pip install -r {} \;
/bin/bash $DIR/patch_python.sh
echo "Installed"
