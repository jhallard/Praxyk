echo "Beginning Praxyk Build Process"

cp -R .praxyk/ ~/.praxyk_travis # move the fake config files to the home directory
ln -s ~/.praxyk_travis ~/.praxyk

declare -a arr=("api" "pod") # "models" "queue" "website" "pod" "devops" "docs")

sudo apt-get install -y git python-pip build-essential

for i in "${arr[@]}"
do
    echo Starting "$i" Build Process
    RETVAL=$(./"$i"/"$i"_build.sh)
    [ $RETVAL -eq 0 ] && echo "$i" Build Success && rm "$i"/.build.log
    [ $RETVAL -ne 0 ] && echo "$i" Build Failure && echo 1 && cat "$i"/.build.log
done
