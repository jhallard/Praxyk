function log_dump {
    echo "$1 Build Log : \n\n"
    cat $1/.build.log
}


echo "Beginning Praxyk Build Process"
echo "______________________________"

cp -R .praxyk/ ~/.praxyk_travis # move the fake config files to the home directory
ln -s ~/.praxyk_travis ~/.praxyk

declare -a arr=("api" "pod" ) # "models" "queue" "website" "pod" "devops" "docs")

sudo apt-get install -y git python-dev python-pip build-essential

for i in "${arr[@]}"
do
    echo "\t Starting $i Build Process"
    cd "$i"
    ./"$i"_build.sh
    cd ..
    RETVAL=$?
    [ $RETVAL -eq 0 ] && echo "\t Module $i Build Success"
    [ $RETVAL -ne 0 ] && echo "\t Module $i Build Failure" && log_dump "$i" && exit 1
done

echo "Praxyk Server Build Success"
echo "______________________________"
exit 0

