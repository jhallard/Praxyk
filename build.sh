echo "Beginning Praxyk Build Process"

declare -a arr=("api") # "models" "queue" "website" "pod" "devops" "docs")

for i in "${arr[@]}"
do
    echo Starting "$i" Build Process
    ./"$i"/"$i"_build.sh
    RETVAL=$?
    [ $RETVAL -eq 0 ] && echo "$i" Build Success
    [ $RETVAL -ne 0 ] && echo "$i" Build Failure && return 1
done
