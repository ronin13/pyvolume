#!/bin/bash 

set -ue
vpid=$$

echo "For sshfs, make sure ssh keys exist in this session"

ssh-add -l | grep 'id_'

[[ -z $SSH_CONFIG  || -z $REMOTE_PATH ]] && {
    echp "Need to set both SSH_CONFIG and REMOTE_PATH"
    exit 1
}
[[ ! -x `which jq` ||  ! -x `which sshfs`  || ! -x `which curl` ]] && {
    echo "Need the runtime deps"
    exit 1
}
export PS1='>>'

[[ ! -d venv ]] && virtualenv2 venv
source venv/bin/activate

finish() {
    set +e
    kill -INT $vpid
    sleep 2
    deactivate
    #rm -rf venv
    cat /tmp/flask.log
    set -e
}

trap finish EXIT 

python2 setup.py install 

rm /tmp/flask.log || true
python2 ./venv/bin/pyvolume 2>&1 &>/tmp/flask.log &
vpid=$!

volname='TESTVOL'
volname2='NEXTVOL'
volname3='AFTERVOL'

sleep 5

set -x

curl -X GET -s http://0.0.0.0:1331 | grep 1331


curl -X POST -s -d '{"Name": "'$volname'", "Opts": {"ssh_config": "'$SSH_CONFIG'", "remote_path": "'$REMOTE_PATH'"} }' http://0.0.0.0:1331/VolumeDriver.Create |  jq '.Err' | grep -v '[a-z]'

curl -X POST -s http://0.0.0.0:1331/Plugin.Activate  | grep  VolumeDriver

curl -X POST -s -d '{"Name": "'$volname'"}' http://0.0.0.0:1331/VolumeDriver.Mount |  jq '.Err' | grep -v '[a-z]'

curl -X POST -s  http://0.0.0.0:1331/VolumeDriver.List |  jq '.Err' | grep -v '[a-z]'

curl -X POST -s -d '{"Name": "'$volname'"}' http://0.0.0.0:1331/VolumeDriver.Path |  jq '.Err' | grep -v '[a-z]'

curl -X POST -s -d '{"Name": "'$volname'"}' http://0.0.0.0:1331/VolumeDriver.Path |  jq '.Mountpoint' | grep  "/mnt/$volname"

curl -X POST -s -d '{"Name": "'$volname'"}' http://0.0.0.0:1331/VolumeDriver.Get |  jq '.Err' | grep -v '[a-z]'

curl -X POST -s -d '{"Name": "'$volname'"}' http://0.0.0.0:1331/VolumeDriver.Get |  jq '.Volume .Mountpoint' | grep  "/mnt/$volname"

curl -X POST -s -d '{"Name": "'$volname'"}' http://0.0.0.0:1331/VolumeDriver.Mount |  jq '.Err' | grep -v '[a-z]'

curl -X POST -s -d '{"Name": "'$volname'"}' http://0.0.0.0:1331/VolumeDriver.UnMount |  jq '.Err' | grep -v '[a-z]'

curl -X POST -s -d '{"Name": "'$volname'"}' http://0.0.0.0:1331/VolumeDriver.Path |  jq '.Mountpoint' | grep  "/mnt/$volname"

curl -X POST -s -d '{"Name": "'$volname'"}' http://0.0.0.0:1331/VolumeDriver.UnMount |  jq '.Err' | grep -v '[a-z]'


curl -X POST -s -d '{"Name": "'$volname'"}' http://0.0.0.0:1331/VolumeDriver.Path |  jq '.Err' | grep  'is not mounted'


curl -X POST -s -d '{"Name": "'$volname2'", "Opts": {"ssh_config": "'$SSH_CONFIG'", "remote_path": "'$REMOTE_PATH'"} }' http://0.0.0.0:1331/VolumeDriver.Create |  jq '.Err' | grep -v '[a-z]'

curl -X POST -s -d '{"Name": "'$volname2'"}' http://0.0.0.0:1331/VolumeDriver.Mount |  jq '.Err' | grep -v '[a-z]'

curl -X POST -s -d '{"Name": "'$volname2'"}' http://0.0.0.0:1331/VolumeDriver.Remove |  jq '.Err' | grep -v '[a-z]'

curl -X POST -s -d '{"Name": "'$volname3'", "Opts": {"ssh_config": "'$SSH_CONFIG'", "remote_path": "'$REMOTE_PATH'"} }' http://0.0.0.0:1331/VolumeDriver.Create |  jq '.Err' | grep -v '[a-z]'

curl -X POST -s -d '{"Name": "'$volname3'"}' http://0.0.0.0:1331/VolumeDriver.Mount |  jq '.Err' | grep -v '[a-z]'


curl -s -X POST http://0.0.0.0:1331/VolumeDriver.Capabilities | jq '.Capabilities .Scope' | grep  global

curl -s -X POST http://0.0.0.0:1331/shutdown | grep 'Server shutting down'
set +x
sleep 5

#kill $vpid

set -x
for vols in $volname $volname2 $volname3; do
    [[ -d /mnt/$vols ]] && {
        echo "Cleanup failed"
        exit 3
    }
done
set +x
