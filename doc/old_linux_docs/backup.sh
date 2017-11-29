while [ "$1" != "" ]; do
    case $1 in
        -d | --destination )    shift
                                dest=$1
                                ;;
        * )                     echo "Unknown argument $1."
                                exit 1
    esac
    shift
done

# set and create backup folder
folder="$dest/`date +%Y%m%d%H%M%S`"
mkdir -p $folder

# backup postgres database
echo "Got input folder: "
echo $folder
pg_dump mokstatsdb -h localhost -U mokstats -F c > $folder/cdump
pg_dump mokstatsdb -h localhost -U mokstats -F c -O > $folder/cdump_o

# delete old backups keeping 5
echo "Deleting old backups..."
cd $dest
ls -t | sed 1,5d | while read folder; do rm -r $folder; done

# done
echo "Done."