#!/bin/bash

sed "s+REPOPATH+$PWD+g" templates/sourceme_template.sh > sourceme.sh
