import os,sys
import multiprocessing as mp

""" This code get pretrain set segment information."""
def remove(sub, s):
    return s.replace(sub, "", -1)

def seg(seginfodir, filelist, savedir,dset):
    """Make segment information, in this code, the segment interval is set to 5s.

        Args:
            seginfodir (str): The LRS2 segment information dir, it can be find in LRS2 dataset.
            filelist (str): The dir of the mp4 file, it should be like '5535415699068794046/00001'
            savedir (str): The dir save the segmented information.
            dset (str): Which set. There are pretrain, Train, Val, Test set.
    """
    datadir = seginfodir + '/' + filelist + '.txt'
    with open(datadir) as filediscr:
        info = filediscr.readlines()
    info[0] = remove('Text:  ', info[0])
    starttime = info[4].split(' ')[1]
    endtime = float(info[-1].split(' ')[2])
    if endtime > 6:
        cutpoint = []
        timer = 5
        for j in range(4, len(info)):
            wordendtime = float(info[j].split(' ')[2])
            if wordendtime / timer > 1:
                cutpoint.append(j)
                timer = timer + 5
        cuttime = []
        for k in range(len(cutpoint)):
            cuttime.append(info[cutpoint[k]].split(' ')[2])

        if cuttime == []:
            ifseg = False
        else:
            ifseg = True
        cuttime = [starttime] + cuttime + [str(endtime)]
        cuttime = ' '.join(cuttime)

        text = []
        for m in range(4, len(info)):
            text.append(info[m].split(' ')[0])
        cuttext = [x - 4 for x in cutpoint]
        cuttext.append(len(text))
        textlen = []
        for n in range(1, len(cuttext)):
            textlen.append(cuttext[n] - cuttext[n - 1])
        textlen = [cuttext[0] + 1] + textlen
        textlen[-1] = textlen[-1] - 1
        textseg = []
        for p in range(len(textlen)):
            temp = []
            for q in range(textlen[p]):
                temp.append(text[q])
            textseg.append(' '.join(temp))
            text[0:textlen[p]] = []

        if ifseg == True:
            for s in range(len(textseg)):
                if textseg[-1] == '':
                    w=1
                else:
                    with open(savedir + '/' + dset + '_text', "a") as text:
                        text.writelines(filelist + '_' + str(s + 1).zfill(2) + ' ' + textseg[s] + '\n')
                        text.close()
            if textseg[-1] == '':
                splitcut = cuttime.split(' ')
                del splitcut[-1]
                cuttime = ' '.join(splitcut)

            with open(savedir + '/' + dset + 'list', "a") as seg:
                seg.writelines(filelist + ' ' + cuttime + '\n')
                seg.close()
        else:
            with open(savedir + '/' + dset + '_text', "a") as text:
                text.writelines(filelist + '_' + str(0).zfill(2) + ' ' + info[0])
                text.close()
            with open(savedir + '/' + dset + 'list', "a") as seg:
                seg.writelines(filelist + ' ' + cuttime + '\n')
                seg.close()




    else:
        with open(savedir + '/' + dset + '_text', "a") as text:
            text.writelines(filelist + '_' + str(0).zfill(2) + ' ' + info[0])
            text.close()
        with open(savedir + '/' + dset + 'list', "a") as seg:
            seg.writelines(filelist + '\n')
            seg.close()
def product_helper(args):
    return seg(*args)
def main(sourcedir, savedir, filelistdir, dset, ifmulticore):
    """Args:
            sourcedir (str): LRS2 dataset dir.
            savedir (str): The dir, which save the extracted audio signal.
            filelistdir (str): The dir, which save LRS2 dataset filelist information.
            dset (str): Which set. There are pretrain, Train, Val, Test set.
            ifmulticore: If use multi processes.
    """
    ifmulticore = bool(ifmulticore)
    seginfodir = sourcedir + '/' + dset
    filelist = filelistdir + "/Filelist_" +dset
    savedir = savedir + '/audio/' + dset + '_segmentinfo'
    exist = os.path.exists(savedir)
    if exist == 1:
        pass
    else:
        os.mkdir(savedir)

    with open(filelist) as filelists:
        filelist = filelists.readlines()
    for i in range(len(filelist)):
        filelist[i] = filelist[i].strip('\n')

    if ifmulticore is True:
        pool = mp.Pool()
        job_args = [(seginfodir, i, savedir,dset) for i in filelist]
        pool.map(product_helper, job_args)
    else:
        for j in filelist:
            seg(seginfodir, j, savedir,dset)





main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4], sys.argv[5])

