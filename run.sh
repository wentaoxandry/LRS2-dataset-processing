#!/bin/sh -u

ifmulticore=1 
ifsegpretrain=true #if we segment pretrain set
videodir=/home/wentao/mnt/ds/database/LipReadingInTheWild/LRS2 #path of LRS2
sourcedir=$videodir/data/lrs2_v1/mvlrs_v1
tmpdir=$(mktemp -d tmp-XXXXX)
trap 'rm -rf ${tmpdir}' EXIT



mkdir  -p ${tmpdir}/filelists

rm -rf filelists
mkdir filelists

for dset in pretrain Test Train Val; do
	cp $videodir/Filelist_${dset} filelists
done
mv filelists/Filelist_Test ${tmpdir}/filelists/Filelist_Test
cat ${tmpdir}/filelists/Filelist_Test | cut -d " " -f1 > filelists/Filelist_Test


datadir=LRS2data
<<'COMMEN'
rm -rf $datadir
mkdir $datadir


audiodir=$datadir/audio
rm -rf $audiodir
mkdir $audiodir

for dset in pretrain Test Train Val; do
    python3 audiosep/sepaudiovideo.py $sourcedir $datadir filelists $dset $ifmulticore
    dsetdir=$audiodir/dset
    find "dsetdir" -size 0 > $audiodir/Filelist_${dset}.txt #check if there are zero size audio file
done
###you should check if there are some thing in $audiodir/Filelist_${dset}.txt, 
###if yes, you should run audiosep/sepaudiovideo.py again, 
###'filelists' is replaced by $audiodir 

if [ "$ifsegpretrain" = true ] ; then
    python3 segaudio/segmentinfo.py $sourcedir $datadir filelists pretrain $ifmulticore #we only segment pretrain set, here we get the segment information
    sort $audiodir/pretrain_segmentinfo/pretrainlist -o  $audiodir/pretrain_segmentinfo/pretrainlist
    sort $audiodir/pretrain_segmentinfo/pretrain_text -o  $audiodir/pretrain_segmentinfo/pretrain_text

    python3 segaudio/segaudio.py $audiodir $audiodir/pretrain_segmentinfo pretrain $ifmulticore #segment the pretrain set
fi


kaldidir=kaldi
rm -rf $kaldidir
mkdir $kaldidir
if [ "$ifsegpretrain" = true ] ; then
    dset=pretrain
    kaldipretraindir=$kaldidir/$dset
    rm -rf $kaldipretraindir
    mkdir $kaldipretraindir
    cp $audiodir/${dset}_segmentinfo/* $kaldipretraindir
    python3 segaudio/kaldipretrainfile.py $audiodir/pretrainsegment $kaldipretraindir pretrain $ifmulticore #prepare kaldi files for segment pretrain set
    for file in segments text utt2spk wav.scp; do
        sort $kaldipretraindir/$file -o $kaldipretraindir/$file
    done

    for dset in Train Val Test; do
        kaldidsetdir=$kaldidir/$dset
	rm -rf $kaldidsetdir
	mkdir $kaldidsetdir
	python3 segaudio/kaldifile.py $sourcedir $audiodir filelists $kaldidsetdir $dset $ifmulticore || exit 1
        for file in segments text utt2spk wav.scp; do
            sort $kaldidsetdir/$file -o $kaldidsetdir/$file
        done
    done

else
    for dset in pretrain Train Val Test; do
        kaldidsetdir=$kaldidir/$dset
	rm -rf $kaldidsetdir
	mkdir $kaldidsetdir
	python3 segaudio/kaldifile.py $sourcedir $audiodir filelists $kaldidsetdir $dset $ifmulticore || exit 1
        for file in segments text utt2spk wav.scp; do
            sort $kaldidsetdir/$file -o $kaldidsetdir/$file
        done
    done
fi

COMMEN

##############################from here is video processing###############################################
videodir=$datadir/video
rm -rf $videodir
mkdir $videodir

if [ "$ifsegpretrain" = true ] ; then
    dset=pretrain
    videopretraindir=$videodir/${dset}_segment
    rm -rf $videopretraindir
    mkdir $videopretraindir
    python3 segvideo/segvideopretrain.py $sourcedir $datadir pretrain $ifmulticore #segment video pretrain set
    for dset in Train Val Test; do
        videodsetdir=$videodir/$dset
	rm -rf $videodsetdir
	mkdir $videodsetdir
	python3 segvideo/segvideo.py $sourcedir $datadir filelists $dset $ifmulticore || exit 1
    done


else
    for dset in pretrain Train Val Test; do
        videodsetdir=$videodir/$dset
	rm -rf $videodsetdir
	mkdir $videodsetdir
	python3 segvideo/segvideo.py $sourcedir $datadir filelists $dset $ifmulticore || exit 1
    done
fi



rm -fr ${tmpdir}


exit 0


