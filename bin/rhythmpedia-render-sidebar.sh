#!/bin/sh

cat _sidebar.conf | xargs yq ea '. as $i ireduce ({}; . *+ $i)' > _sidebar.generated.yml
echo "**目次**\n\n" > _sidebar.generated.md
bin/rhythmpedia-render-toc.py _sidebar.conf >> _sidebar.generated.md

