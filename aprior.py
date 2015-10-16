from collections import deque
import itertools
import time
import sys
import os.path

##return value: head: the name of each transaction
##              data: the data from file
from builtins import print

# usage: read datafile in
def readfile(path):
    head = []
    data = []
    with open(path) as fp:
        for line in fp:
            count = 0
            # split the transaction name with transaction context
            entry = line[:-1].split(':')

            head.append(entry[0])

            items = entry[1][1:].split(',')
            data.append(items)
            #print(items)
        fp.close()
    return head, data


## usage scan the database, pruning the itemsets with small support
def prun(keys, Sup, D):
    afterprun = []
    support = []
    n = len(D)
    count = 0
    for key in keys:
        count += 1
        #print('prun', count, 'in', len(keys))
        appear = 0
        for line in D:
            # if it appears in one transaction
            if set(key) <= set(line):
                appear += 1


        if appear >= Sup:
            #print(key,"appear", appear, 'in', n, 'times', appear/n)
            afterprun.append(key)
            support.append(appear)
           # print('prun: key', key)
    #print('prun: afterPrun', afterprun)
    #print('prun: appear', support)
    return afterprun, support





## usage self join the itemsets to form k+1 level
#keys should have order

def self_join(keys):
    jointset = []
    count = 0
    for i in keys[:len(keys)-1]:
        count += 1

        index_j = keys.index(i) + 1


        while index_j < len(keys):
            j = keys[index_j]
            # tmp = listor(i, keys[j])
            if len(i) != len(j):
                print('self-join:try to join two sets of different element num')
                exit()
            # if the two frequent item sets only have the last item different
            if i[:len(i)-1] == j[:len(j)-1]:
                #join this two itemsets
                tmp = i + j[len(j)-1:]
                if jointset.count(tmp) == 0:
                    jointset.append(tmp)
                    # print('joint before', i, j)
                    # print('joint generated:', tmp)
            index_j += 1
    return jointset




## usage show  itemset and its support
def showfreq(Itemsets, Support, filehandle):
    i = 0
    while i < len(Itemsets):

        #print('freq itemset found! {', Itemsets[i], '},Sup=', Support[i])
        buffer = '{' + ','.join(Itemsets[i]) + '};Sup=' + str(Support[i]) + '\n'
        i += 1
        filehandle.write(buffer)

    ## usage show  itemset and its support
def ShowMaxItems(Itemset, mSupport, filehandle):
    i = 0

    if len(Itemset) != len(mSupport):
        print('len of MaxItems:,',len(Itemset),'len of MaxSup:', len(mSupport))
        print('alert, maxitems ')
    while i < len(Itemset):
      #  print('{', Itemset[i], '},Sup=', Support[i])
        buffer = '{' + ','.join(Itemset[i]) + '};Sup=' + str(mSupport[i]) + '\n'
        i += 1
        # print('find the support of No.',i,'Maxitems')
        filehandle.write(buffer)

## generate association rules using frequent itemsets
def generate_ass(Itemsets, data, Conf , filehandle):
    for itemset in Itemsets:
        i = 1
        if len(itemset) < 2:
            return -1
            print('itemset must have more than 2 elements')
        while i < len(itemset):
            gen = itertools.combinations(itemset, i)# get the subset which have i items
            for j in gen:
                # split the set into two parts
                right = j
                left = set(itemset) - set(right)

                occur1, occur2 = 0, 0
                for line in data:
                    if left <= set(line):
                        occur1 += 1
                        if set(right) <= set(line):
                            occur2 += 1
                conf = occur2/occur1
                if conf > Conf:
                    sorted_left = list(left)
                    sorted_right = list(right)
                    sorted_left.sort( key = lambda item_name: int(item_name[1:]))
                    sorted_right.sort( key = lambda item_name: int(item_name[1:]))
                    # print('{', left, '->', list(right), '};Confidence:', occur1, occur2, "{0:.1f}%".format(conf*100))
                    buffer = '{' + ','.join(sorted_left) + '->' + ','.join(sorted_right) + '};Confidence:' + "{0:.1f}%".format(conf*100) +'\n'
                    h_ass.write(buffer)
            i += 1


if __name__ == "__main__":
    data = []
    head = []
    freq_items = []
    Support = []
    MaxItems = []
    MaxItemSup = []\

    '''
    Sup = 300
    datapath = 'data/dataset_full.txt'
    Conf = 0.5
    '''

    # do the input check
    if len(sys.argv) != 4:
        print('input error')
        print('please input in this format: python3 aprior.py fullfilepath Minsup Minconf')
        exit()
    if os.path.isfile(sys.argv[1]):
        datapath = sys.argv[1]
    else:
        print('datafile not found, try again')
        print('please input in this format: fullfilepath minsup minconf')
        exit()
    if int(sys.argv[2]) > 0:
            Sup = int(sys.argv[2])
    else:
        print('you have Sup = ', sys.argv[2])
        print('minsup must be a positive integer')
        print('please input in this format: fullfilepath minsup minconf')
        exit()
    if 0 <= float(sys.argv[3]) <= 1:
        Conf = float(sys.argv[3])
    else:
        print('you should input the min confidence as a decimal from 0 to 1')
        print('please input in this format: fullfilepath minsup minconf')
        exit()



    print('correct input', datapath, Sup, Conf)
    print('please wait')



    start_time=time.time()
    head, data = readfile(datapath)  # path = 'data/minor.txt'

    h_freqitems = open('outputs/FrequentItemsets.txt', 'w')
    h_ass = open('outputs/AssociationRules.txt', 'w')
    h_maxfreq = open('outputs/MaxFrequentItemsets.txt', 'w')

    # tick
    # prun the repeat items
    keys = []
    for T in data:
        for I in T:
            if keys.count([I]) == 0:
                keys.append([I])

    # sort using the item name
    keys.sort( key = lambda item_name: int(item_name[0][1:]))

    afterprun, appear = prun(keys, Sup, data)
    iter_time = 0
    # store the maxitemsets and their support
    MaxItems = []
    MaxItemsSup = []
    while afterprun != []:
        iter_time += 1
        #print('\nthe', iter_time,'iratation')
        # out put the current level frequent itemsets
        showfreq(afterprun, appear, h_freqitems)

        # generate associate rules
        generate_ass(afterprun, data, Conf, h_ass)

        freq_items += afterprun
        Support += appear

        # self join the elements to form next-level candidate
        Cand_k = self_join(afterprun)

        # save frequent itemset of this level
        prev_afterprun = afterprun

        # prun the candidate to form frequent itemset of next level
        afterprun, appear = prun(Cand_k, Sup, data)

        count1 = 0
        count2 = 0

        # calculate the Max ItemSet
        # should change iter order!
        for I1 in prev_afterprun:
            count1 += 1
            flag = 0
            for I2 in afterprun:
                if set(I1) < set(I2):
                    flag = 1
                    break
            if flag == 0:
                MaxItems.append(I1)
                freq_index = freq_items.index(I1)
                MaxItemsSup.append(Support[freq_index])
                # if len(MaxItems) != len(MaxItemsSup):
                #print('maxitemslenth', len(MaxItems), 'maxitemsupportlent', len(MaxItemsSup))
        #print('add max itemset', I1)


    ShowMaxItems(MaxItems, MaxItemsSup, h_maxfreq)
    #write_into_file()
    print('complete!')
    print("freq_items are saved in 'outputs/FrequentItemsets'")
    print("assocation rules are saved in 'outputs/AssociationRules'")
    print("freq_items is saved in 'outputs/maxFrequentItemsets'")


    #toc
    print('*******************************************')
    print("total used time is----%s seconds---"%round(time.time()-start_time, 5))

    h_freqitems.close()
    h_ass.close()
    h_maxfreq.close()



