#!/bin/bash

PATH_TO_NARRATOR_SCRIPT="/data/cvit/pipeline-20111215/scripts/create_distribute/dtb/Narrator-DtbookToDaisy.taskScript"
INPUT_FILE=$1
OUTPUT_DIR=$2
OUTPUT_PATH="/data/django_u/django_projects/code_along/ttsdaisy/ttsdaisy_v4/media/archive/$OUTPUT_DIR"

/bin/bash /data/cvit/pipeline-20111215/pipeline.sh $PATH_TO_NARRATOR_SCRIPT --input=$INPUT_FILE --outputPath=$OUTPUT_PATH
