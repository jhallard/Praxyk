function log_dump {
    echo "$1 Build Log :"
    cat .build.log
}

function setup_databases {
    mysql -e "create database IF NOT EXISTS test;" -uroot
}


echo "Beginning Praxyk Build Process"
echo "______________________________"

cp -R .praxyk/ ~/.praxyk_travis # move the fake config files to the home directory
ln -s ~/.praxyk_travis ~/.praxyk

declare -a arr=("api" "pod" "models") # "queue" "website" "pod" "devops" "docs")

sudo apt-get install -y git python-dev python-pip build-essential
git submodule update --init --recursive

for i in "${arr[@]}"
do
    echo "  Starting $i Build Process"
    cd "$i"
    ./build.sh
    RETVAL=$?
    [ $RETVAL -eq 0 ] && echo "  Module $i Build Success"
    [ $RETVAL -ne 0 ] && echo "  Module $i Build Failure" && exit 1
    cd ..
done


echo "Praxyk Server Build Success"
echo "______________________________"
exit 0

