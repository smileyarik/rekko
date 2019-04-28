import implicit
import csv
import sys
from collections import defaultdict
import numpy as np
from scipy.sparse import csr_matrix
import pickle

if __name__ == '__main__':
    model = implicit.als.AlternatingLeastSquares(factors=14) # best 14

    user_items = defaultdict(set)
    items = set()
    users = set()
    count = 0
    print "Read transactions"
    with open(sys.argv[1]) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            item = int(row[0])
            user = int(row[1])
            #print item,user
            user_items[user].add(item)
            items.add(item)
            users.add(user)
            if count % 100000 == 0:
                print count
            count += 1

    items = sorted(list(items))
    users = sorted(list(users))

    item_index = {items[i]:i for i in xrange(0, len(items))}
    user_index = {users[i]:i for i in xrange(0, len(users))}
    #print items
    #print users

    print "Build matrix"
    indptr = [0]
    indices = []
    data = []
    count = 0
    for user in users:
        if count % 1000 == 0:
            print count
        count += 1
        #print user_items[user]
        #for index in xrange(0,len(items)):
        for item in sorted(list(user_items[user])):
            #if items[index] in user_items[user]:
            index = item_index[item]
            indices.append(index)
            data.append(1)
        indptr.append(len(indices))

    matrix = csr_matrix((data, indices, indptr), dtype=int).transpose()

    print "Fit als"
    model.fit(matrix)

    user_factors = {}
    for user in users:
        user_factors[user] = model.user_factors[user_index[user]]
    item_factors = {}
    for item in items:
        item_factors[item] = model.item_factors[item_index[item]]

    print "Dumping user profiles"
    with open(sys.argv[2], 'w') as user_pickle:
        pickle.dump(user_factors, user_pickle)

    print "Dumping item profiles"
    with open(sys.argv[3], 'w') as item_pickle:
        pickle.dump(item_factors, item_pickle)




    print model.item_factors
    print model.user_factors

    for item in [8888, 8436, 2252]:
        for user in [50431, 458827, 180823]:
            user_f = model.user_factors[user_index[user]]
            item_f = model.item_factors[item_index[item]]
            print user, item, np.dot(user_f, item_f)

    print "user-user"
    for user in list(users)[0:10]:
        for user2 in list(users)[0:10]:
            user_f = model.user_factors[user_index[user]]
            user2_f = model.user_factors[user_index[user2]]
            print user, user2, np.dot(user_f, user2_f)

    for item in model.item_factors[0:10]:
        print "---"
        for user in model.user_factors[0:10]:
            print np.dot(item, user)


#for other, score in model.similar_items(, 11):
