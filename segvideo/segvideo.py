import os, sys, math
from shutil import copyfile
import cv2
import numpy as np
import torch
import itertools
import multiprocessing as mp
def extract_opencv(filename):
    """Using cv2 extract video frames.

        Args:
            filename (str): The video file name.
    """
    video = []
    cap = cv2.VideoCapture(filename)
    while(cap.isOpened()):
        ret, frame = cap.read() # BGR
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            video.append(frame)
        else:
            break
    cap.release()

    video = np.array(video)
    return video #[...,::-1]
def segvideo(sourcedir, filelist, savedir,dset):
    """Segment video files, save data in pt files.

        Args:
            sourcedir (str): The LRS2 dataset dir.
            filelist (str): The dir of the mp4 file, it should be like '5535415699068794046/00001'
            savedir (str): Save the segmented video files.
            dset (str): Which set. There are pretrain, Train, Val, Test set.
    """
    #print(filelist)
    mp4filedir = sourcedir + '/' + filelist + '.mp4'
    pics = extract_opencv(mp4filedir)[:, 55: 125, 45: 115]
    pics = pics / 255.
    pics = [cv2.resize(pics[i,:,:], (96, 96)) for i in range(len(pics))]
    pics = np.array(pics)
    mean = 0.4161
    std = 0.1688
    pics = (pics - mean) / std
    filelist = filelist.split('/')

    savedir1 = savedir
    exist = os.path.exists(savedir1)
    if exist == 1:
        pass
    else:
        os.mkdir(savedir1)
    savedir2 = savedir1 + '/' + filelist[0]
    exist = os.path.exists(savedir2)
    if exist == 1:
        pass
    else:
        os.mkdir(savedir2)

    savedir3 = savedir2 + '/' + filelist[1]
    exist = os.path.exists(savedir3 + '.pt')
    if exist is True:
        pass
    else:
        torch.save(pics, savedir3 + '.pt')
        print(savedir3)








def product_helper(args):
    return segvideo(*args)
def main(sourcedir, savedir, filelistdir, dset, ifmulticore):
    """Segment video files, save data in pt files.

        Args:
            sourcedir (str): The LRS2 dataset dir.
            savedir (str): Save the segmented video files.
            filelistdir (str): The dir, which save LRS2 dataset filelist information.
            dset (str): Which set. There are pretrain, Train, Val, Test set.
            ifmulticore: If use multi processes.
    """
    ifmulticore = bool(ifmulticore)
    if dset == 'pretrain':
        sourcedir = sourcedir + '/pretrain'
    else:
        sourcedir = sourcedir + '/main'
    filelistdir = filelistdir + "/Filelist_" +dset
    savedir = savedir + '/video/' + dset
    exist = os.path.exists(savedir)
    if exist == 1:
        pass
    else:
        os.mkdir(savedir)



    with open(filelistdir) as filelists:
        filelist = filelists.readlines()


    for i in range(len(filelist)):
        filelist[i] = filelist[i].strip('\n')
    if ifmulticore is True:
        pool = mp.Pool()
        job_args = [(sourcedir, i, savedir, dset) for i in filelist]
        pool.map(product_helper, job_args)
    else:
        for i in filelist:
            segvideo(sourcedir, i, savedir, dset)




main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4], sys.argv[5])
