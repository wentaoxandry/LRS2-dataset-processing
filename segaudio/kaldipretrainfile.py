import os, sys, wave, contextlib
import re, string
import itertools
import multiprocessing as mp

def main(audiodir, savedir, dset, ifmulticore):
    """Prepare the Kaldi files.

        Args:
            audiodir (str): The audio dir.
            savedir (str): The dir save the Kaldi files.
            dset (str): Which set. For this code dset is pretrain set.
            ifmulticore: If use multi processes.
    """
    ifmulticore = bool(ifmulticore)
    exist=os.path.exists(savedir)
    if exist == 1:
        pass
    else:
        os.mkdir(savedir)
    filelistdir = savedir + '/' + dset + '_text'
    with open(filelistdir) as filelists:
        filelist = filelists.readlines()
    for i in range(len(filelist)):
        filelist[i] = filelist[i].strip('\n')
        if dset=='Test':
            filelist[i] = filelist[i].split(' ')
            filelist[i] = filelist[i][0]
        else:
            pass
    filelist.sort()
    if ifmulticore is True:
        pool = mp.Pool()
        job_args = [(i, dset, audiodir, savedir) for i in filelist]
        pool.map(product_helper, job_args)
    else:
        for i in filelist:
            set(i,dset,audiodir, savedir)

def product_helper(args):
    return set(*args)

def set(file,s,audiodir, savedir):
    """Make the Kaldi files.

        Args:
            file (str): The file name.
            s (str): Which set. For this code dset is pretrain set.
            audiodir: The audio dir.
            savedir (str): The dir save the Kaldi files.
    """
    segdir = savedir +  '/segments'
    textdir= savedir +  '/text'
    utt2spkdir=savedir + '/utt2spk'
    wavdir=savedir +  '/wav.scp'
    notexist = savedir + '/notexist'

    splittext = file.split(' ')
    filedir = splittext[0]
    if '_' in filedir[-2:]:
        filedir = filedir + '0'
    else:
        pass
    text = ' '.join(splittext[1:])
    mp3dir = audiodir + '/' + filedir + 'p.wav'
    exist = os.path.exists(mp3dir)
    if exist == 1:
        splitname = filedir.split('/')
        try:
            with contextlib.closing(wave.open(mp3dir, 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)
            starttime = round(0.00, 2)
            endtime = round(duration, 2)
            if endtime < 1.0:
                with open(notexist, "a") as wav:
                    wav.writelines(mp3dir + '\n')
                    wav.close()
            else:
                startint = int(float(starttime) * 100)
                endint = int(float(endtime) * 100)
                startstr = str(startint).zfill(7)
                endstr = str(endint).zfill(7)
                title = 'LRS2_' + splitname[0] + '_' + splitname[1] + 'p_' + startstr + '_' + endstr
                recoid = 'LRS2_' + splitname[0] + '_' + splitname[1] + 'p'

                with open(textdir, "a") as textprocess:
                    textprocess.writelines(title + ' ' + text + '\n')
                    textprocess.close()
                with open(segdir, "a") as seg:
                    seg.writelines(title + ' ' + recoid + ' 0 ' + str(endtime) + '\n')
                    seg.close()
                with open(utt2spkdir, "a") as utt:
                    utt.writelines(title + ' ' + recoid + '\n')
                    utt.close()

                with open(wavdir, "a") as wav:
                    wav.writelines(
                        title + ' ' + mp3dir + '\n')
                    wav.close()

        except:
            with open(notexist, "a") as wav:
                wav.writelines(mp3dir + '\n')
                wav.close()

    else:
        with open(notexist, "a") as wav:
            wav.writelines(mp3dir + '\n')
            wav.close()






def remove(sub,s):
    return s.replace(sub, "", -1)



main(sys.argv[1],sys.argv[2],sys.argv[3], sys.argv[4])
