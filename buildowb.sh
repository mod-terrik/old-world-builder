#!/bin/bash

yarn build
mv build/ owb/
tar -czvf owb.tgz owb/
scp owb.tgz cvadmin@proxy-dmz.tech.lab:/docker/nginx/html/warhammer

