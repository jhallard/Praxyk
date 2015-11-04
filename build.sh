echo "Beginning Praxyk Build Process"

cp -R .praxyk/ ~/.praxyk_travis # move the fake config files to the home directory
ln -s ~/.praxyk_travis ~/.praxyk

declare -a arr=("api" ) # "models" "queue" "website" "pod" "devops" "docs")

sudo apt-get install -y git python-pip build-essential

for i in "${arr[@]}"
do
    echo Starting "$i" Build Process
    ./"$i"/"$i"_build.sh
    RETVAL=$?
    [ $RETVAL -eq 0 ] && echo "$i" Build Success
    [ $RETVAL -ne 0 ] && echo "$i" Build Failure && exit 1
done

echo "Build Success"
exit 0

