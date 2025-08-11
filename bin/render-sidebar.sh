#!/bin/sh

cat _sidebar.conf | xargs yq ea '. as $i ireduce ({}; . *+ $i)' > _sidebar.yml
