#!/bin/bash

src_path=`cd "$1"; pwd`
dest_path=`cd "$2"; pwd`
# echo "$src_path --> $dest_path"

for filepath in $src_path/watcher_dashboard/local/enabled/*.py; do
    filename=$(basename $filepath)
    if [ $filename != "__init__.py" ]; then
        echo $filepath
        src_filepath="`cd "$(dirname $filepath)"; pwd`/$filename"
        dest_filepath="$dest_path/openstack_dashboard/local/enabled/$filename"
        echo "$src_filepath --> $dest_filepath"
        ln -s $src_filepath $dest_filepath
    fi
done

policy_file_name='watcher_policy.json'
src_policy_filepath=$src_path'/watcher_dashboard/conf/'$policy_file_name
dest_policy_file=$dest_path'/openstack_dashboard/conf/'$policy_file_name
echo "$src_policy_filepath --> $dest_policy_file"
ln -s $src_policy_filepath $dest_policy_file
