import os, sys, wave, contextlib
import re, string
import itertools
import multiprocessing as mp

def main(sourcedir, audiodir, filelistdir, savedir, dset, ifmulticore):
    """Prepare the Kaldi files.

        Args:
            sourcedir (str): LRS2 dataset dir.
            audiodir (str): The audio dir.
            filelist (str): The dir of the mp4 file, it should be like '5535415699068794046/00001'
            savedir (str): The dir save the Kaldi files.
            dset (str): Which set. For this code dset is pretrain set.
            ifmulticore: If use multi processes.
    """
    ifmulticore = bool(ifmulticore)
    exist = os.path.exists(savedir)
    if exist == 1:
        pass
    else:
        os.mkdir(savedir)
    filelistdir = filelistdir + '/' +  'Filelist_' +dset
    with open(filelistdir) as filelists:
        filelist = filelists.readlines()
    for i in range(len(filelist)):
        filelist[i] = filelist[i].strip('\n')
    audiodir = audiodir + '/' + dset
    if dset =='pretrain':
        sourcedir = sourcedir + '/pretrain/'
    else:
        sourcedir = sourcedir + '/main/'
    if ifmulticore is True:
        pool = mp.Pool()
        job_args = [(i,dset,audiodir,savedir, sourcedir) for i in filelist]
        pool.map(product_helper, job_args)
    else:
        for i in filelist:
            set(i,dset,audiodir,savedir, sourcedir)

def product_helper(args):
    return set(*args)


def set(info,s,audiodir,savedir, sourcedir):
    """Make the Kaldi files.

        Args:
            info (str): The file name.
            s (str): Which set. For this code dset is pretrain set.
            audiodir: The audio dir.
            savedir (str): The dir save the Kaldi files.
            sourcedir (str): LRS2 dataset dir.
    """
    segdir = savedir + '/segments'
    textdir= savedir + '/text'
    utt2spkdir=savedir + '/utt2spk'
    wavdir=savedir + '/wav.scp'
    files=[]

    info=info.split()
    info[0]=info[0].split('/')
    if s == 'pretrain':
        info[0] = 'LRS2_' + info[0][0] + '_' + info[0][1] + 'p'
    else:
        info[0]='LRS2_' + info[0][0] + '_' + info[0][1] + 'm'
    name = info[0]
    name = name.split('_')
    f = name[1] + '/' + name[2][:-1]

    textfile = sourcedir + f + '.txt'
    mp3dir = audiodir + '/' + f + '.wav'
    exist = os.path.exists(mp3dir)
    if exist == 1:
        with open(textfile) as filelists:
            text = filelists.readlines()
        text = text[0].split(':')[1]
        splitname = f.split('/')
        with contextlib.closing(wave.open(mp3dir, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
        starttime = round(0.00, 2)
        endtime = round(duration, 2)
        startint = int(starttime * 100)
        endint = int(endtime * 100)
        startstr = str(startint).zfill(7)
        endstr = str(endint).zfill(7)
        if s == 'pretrain':
            title = 'LRS2_' + splitname[0] + '_' + splitname[1] + 'p_' + startstr + '_' + endstr
            recoid = 'LRS2_' + splitname[0] + '_' + splitname[1] + 'p'
        else:
            title = 'LRS2_' + splitname[0] + '_' + splitname[1] + 'm_' + startstr + '_' + endstr
            recoid = 'LRS2_' + splitname[0] + '_' + splitname[1] + 'm'

        if duration < 100:
            with open(textdir, "a") as textprocess:
                textprocess.writelines(title + '' + text)
                textprocess.close()

            with open(segdir, "a") as seg:
                seg.writelines(title + ' ' + recoid + ' ' + str('0') + ' ' + str(endtime) + '\n')
                seg.close()
            with open(utt2spkdir, "a") as utt:
                if s == 'pretrain':
                    utt.writelines(title + ' LRS2_' + splitname[0] + '_' + splitname[1] + 'p\n')
                else:
                    utt.writelines(title + ' LRS2_' + splitname[0] + '_' + splitname[1] + 'm\n')
                utt.close()

            with open(wavdir, "a") as wav:
                wav.writelines(title + ' ' + mp3dir + '\n')
                wav.close()



        else:
            pass

    else:
        pass




main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4], sys.argv[5], sys.argv[6])
