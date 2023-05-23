#!/bin/bash

PROJECTPATH="$PWD/experiments"

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --project-path)
      PROJECTPATH="$2"
      shift
      shift
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

sed "s+REPOPATH+$PWD+g" templates/sourceme_template.sh > sourceme.sh
sed -i "s+PROJECTPATH+$PROJECTPATH+g" sourceme.sh
