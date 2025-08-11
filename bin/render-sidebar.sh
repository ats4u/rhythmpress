#!/bin/sh

cat _sidebar.conf | xargs yq ea '. as $i ireduce ({}; . *+ $i)' > _sidebar.generated.yml
echo "**目次**\n\n" > _sidebar.generated.md
bin/render-toc2 _sidebar.conf >> _sidebar.generated.md

