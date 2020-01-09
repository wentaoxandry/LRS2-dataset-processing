import os, sys
from pydub import AudioSegment
import multiprocessing as mp

""" This code crop the audio file by using the segment information."""

def seg(filelist, sourcedir, savedir):
    """Crop the audio files into fest interval.

        Args:
            filelist (str): Segment information.
            sourcedir (str): Audio file dir.
            savedir (str): The dir save the segmented audio files.
    """
    filelist = filelist.strip('\n')
    filelist = filelist.split(' ')
    ifsegment = len(filelist)

    filedir = filelist[0]
    seginfo = filelist[1:]
    audiodir = sourcedir + '/pretrain/' + filedir + '.wav'
    splitname = filedir.split('/')
    savedir1 = savedir + '/' + splitname[0]
    exist = os.path.exists(savedir1)
    if exist == 1:
        pass
    else:
        os.mkdir(savedir1)

    Audio = AudioSegment.from_wav(audiodir)
    fs = Audio.frame_rate
    cutpoint = [int(float(x) * 1000) for x in seginfo]

    if cutpoint == []:
        finalsave = savedir1 + '/' + splitname[1] + '_00p' + '.wav'
        exist = os.path.isfile(finalsave)
        if exist is True:
            pass
        else:
            Audio.export(finalsave, format="wav")
            print(finalsave)


    for j in range(len(cutpoint) - 1):
        newAudio = Audio[cutpoint[j]: cutpoint[j + 1]]
        if ifsegment > 3:
            finalsave = savedir1 + '/' + splitname[1] + '_' + str(j + 1).zfill(2) + 'p' + '.wav'
            exist = os.path.isfile(finalsave)
            if exist is True:
                pass
            else:
                newAudio.export(finalsave, format="wav")
                print(finalsave)
        else:
            finalsave = savedir1 + '/' + splitname[1] + '_' + str(j).zfill(2) + 'p' + '.wav'
            exist = os.path.isfile(finalsave)
            if exist is True:
                pass
            else:
                newAudio.export(finalsave, format="wav")
                print(finalsave)


def product_helper(args):
    return seg(*args)
def main(sourcedir, filelist, dset, ifmulticore):
    """Args:
            sourcedir (str): The extracted audio dir.
            filelist (str): The file, which save LRS2 dataset filelist information.
            dset (str): Which set. There are pretrain, Train, Val, Test set.
            ifmulticore: If use multi processes.
    """
    ifmulticore = bool(ifmulticore)
    savedir = sourcedir
    filelistdir = filelist + '/' + dset + 'list'
    savedir = savedir + '/pretrainsegment'
    exist = os.path.exists(savedir)
    if exist == 1:
        pass
    else:
        os.mkdir(savedir)



    with open(filelistdir) as filelists:
        filelist = filelists.readlines()

    if ifmulticore is True:
        pool = mp.Pool()
        job_args = [(i, sourcedir, savedir) for i in filelist]
        pool.map(product_helper, job_args)
    else:
        for i in filelist:
            seg(i, sourcedir, savedir)











main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])

