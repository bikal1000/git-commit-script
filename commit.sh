#!/usr/bin/env bash

commit_message="$1"
read -p "Enter the type of type: " type

type="$(tr '[:lower:]' '[:upper:]' <<< ${type:0:1})${type:1}"

task_id=$(git rev-parse --abbrev-ref HEAD | grep -o "^[A-Z]*-[0-9]*")
if [ -z "$task_id" ]
then
    git commit -m "$type: $commit_message"
else
    git commit -m "$type: $commit_message #$task_id"
fi