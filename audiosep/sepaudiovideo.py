import os, sys
import multiprocessing as mp

""" This code extract audio files from mp4 files."""
def main(sourcedir, savedir, filelistdir, dset, ifmulticore):
    """Args:
            sourcedir (str): LRS2 dataset dir.
            savedir (str): The dir, which save the extracted audio signal.
            filelistdir (str): The dir, which save LRS2 dataset filelist information.
            dset (str): Which set. There are pretrain, Train, Val, Test set.
            ifmulticore: If use multi processes.
        """
    ifmulticore = bool(ifmulticore)
    exist=os.path.exists(savedir)
    if exist == 1:
        pass
    else:
        os.mkdir(savedir)

    filelistdir = filelistdir + "/Filelist_" +dset
    with open(filelistdir) as filelists:
        filelist = filelists.readlines()
    for i in range(len(filelist)):
        filelist[i]=filelist[i].strip('\n')

    audiodir=savedir+'/audio'
    existaudio=os.path.exists(audiodir)
    if existaudio ==1:
        pass
    else:
        os.mkdir(audiodir)
    filelist.sort()

    if dset == 'pretrain':
        subfiledir = 'pretrain'
    else:
        subfiledir = 'main'


    if ifmulticore is True:
        pool = mp.Pool()
        job_args = [(dset, audiodir, j, sourcedir, subfiledir) for j in filelist]
        pool.map(product_helper, job_args)
    else:
        for j in filelist:
            process(dset, audiodir, j, sourcedir, subfiledir)



def product_helper(args):
    return process(*args)

def process(s,audiodir,name, sourcedir, subfiledir):
    """Extract the audio signal from each mp4 file.

       Args:
           s (str): Which set. There are pretrain, Train, Val, Test set.
           audiodir (str):The dir, which save the extracted audio signal.
           name (str): The name of the mp4 file.
           sourcedir (str):  LRS2 dataset dir.
           subfiledir (str): where the mp4 files saved.
    """
    inputFile = sourcedir + '/' + subfiledir + '/' + name + '.mp4'
    savecheckdir = audiodir + '/' + s + '/' + name + '.wav'
    check = os.path.exists(savecheckdir)
    if check is True:
        pass
    else:
        namesplit = name.split('/')
        savedir = audiodir + '/' + s + '/' + namesplit[0]
        outputname = namesplit[1] + ".wav"
        existdir = os.path.exists(audiodir + '/' + s)
        if existdir == 1:
            pass
        else:
            os.mkdir(audiodir + '/' + s)
        existdir = os.path.exists(audiodir + '/' + s + '/' + namesplit[0])
        if existdir == 1:
            pass
        else:
            os.mkdir(audiodir + '/' + s + '/' + namesplit[0])
        outFile = savedir + '/' + outputname
        try:
            cmd = "ffmpeg -i {} -vn -ac 2 -ar 16000 -ab 320k -f wav {}".format(inputFile, outFile)
            os.popen(cmd)
        except:
            print('error')
            with open(savedir + '/Filelist_' + s + '.txt', 'a+') as af:
                af.writelines(name + '\n')
            af.close()




main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4], sys.argv[5])



