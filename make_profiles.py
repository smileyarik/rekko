import sys
import csv
import json
from profiles import *
from collections import defaultdict
import pickle

def make_counters():
    return Counters()

if __name__ == '__main__':
    item_counters = defaultdict(make_counters)
    user_counters = defaultdict(make_counters)

    print "Find target users"
    target_users = defaultdict(lambda:set())
    data = json.load(open(sys.argv[5]))
    for user in data['users']:
        target_users[int(user)] = set()


    # READ ITEM CATALOGUE #
    print "Reading catalogue"
    cat_data = json.load(open(sys.argv[1]))
    for item_id,value in cat_data.iteritems():
        item_id = int(item_id)
        counters = item_counters[item_id]
        for attr in  value['attributes']:
            counters.set(OT_ATTR, CT_HAS, RT_SUM, attr, 1, 0)
        for avail in value['availability']:
            counters.set(OT_AVAIL, CT_HAS, RT_SUM, avail, 1, 0)
        counters.set(OT_DURATION, CT_VALUE, RT_SUM, '', value['duration'], 0)
        for i in xrange(1,6):
            counters.set(OT_FEATURE, CT_VALUE, RT_SUM, i, value['feature_' + str(i)], 0)
        counters.set(OT_ITEMTYPE, CT_HAS, RT_SUM, value['type'], 1, 0)


    # PARSE TRANSACTIONS #
    print "Parsing transactions"
    with open(sys.argv[2]) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        count = 1
        for row in reader:
            if count % 100000 == 0:
                print count
            count += 1
            item_id = int(row[0])
            user_id = int(row[1])
            mode = row[2]
            ts = int(float(row[3]) * 6)
            watch_time = int(row[4])
            d_type = int(row[5])
            d_man = int(row[6])

            item = item_counters[item_id]

            item.add(OT_GLOBAL, CT_TRANSACTION, RT_SUM, '', 1, ts)
            item.add(OT_GLOBAL, CT_TRANSACTION, RT_7D, '', 1, ts)
            item.add(OT_GLOBAL, CT_TRANSACTION, RT_30D, '', 1, ts)

            if user_id in target_users:
                user = user_counters[user_id]

                user.add(OT_GLOBAL, CT_TRANSACTION, RT_SUM, '', 1, ts)
                user.add(OT_ITEM, CT_TRANSACTION, RT_SUM, item_id, 1, ts)

                user.update_from(item, OT_ATTR, CT_HAS, RT_SUM, CT_TRANSACTION, RT_SUM, ts)
                user.update_from(item, OT_AVAIL, CT_HAS, RT_SUM, CT_TRANSACTION, RT_SUM, ts)
                user.update_from(item, OT_DURATION, CT_VALUE, RT_SUM, CT_TRANSACTION, RT_SUM, ts)
                user.update_from(item, OT_FEATURE, CT_VALUE, RT_SUM, CT_TRANSACTION, RT_SUM, ts)
                user.update_from(item, OT_ITEMTYPE, CT_HAS, RT_SUM, CT_TRANSACTION, RT_SUM, ts)

                user.add(OT_WATCHTIME, CT_TRANSACTION, RT_SUM, '', watch_time, ts)
                user.add(OT_DEVICETYPE, CT_TRANSACTION, RT_SUM, d_type, 1, ts)
                user.add(OT_DEVICEMAN, CT_TRANSACTION, RT_SUM, d_man, 1, ts)
                user.add(OT_WATCHMODE, CT_TRANSACTION, RT_SUM, mode, 1, ts)

            item.add(OT_WATCHTIME, CT_TRANSACTION, RT_SUM, '', watch_time, ts)
            item.add(OT_DEVICETYPE, CT_TRANSACTION, RT_SUM, d_type, 1, ts)
            item.add(OT_DEVICEMAN, CT_TRANSACTION, RT_SUM, d_man, 1, ts)
            item.add(OT_WATCHMODE, CT_TRANSACTION, RT_SUM, mode, 1, ts)

    print "Parsing bookmarks"
    with open(sys.argv[3]) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        count = 1
        for row in reader:
            if count % 100000 == 0:
                print count
            count += 1
            user_id = int(row[0])
            item_id = int(row[1])
            ts = int(float(row[2]) * 6)

            item = item_counters[item_id]

            item.add(OT_GLOBAL, CT_BOOKMARK, RT_SUM, '', 1, ts)
            item.add(OT_GLOBAL, CT_BOOKMARK, RT_7D, '', 1, ts)
            item.add(OT_GLOBAL, CT_BOOKMARK, RT_30D, '', 1, ts)

            if user_id in target_users:
                user = user_counters[user_id]

                user.add(OT_GLOBAL, CT_BOOKMARK, RT_SUM, '', 1, ts)
                user.add(OT_ITEM, CT_BOOKMARK, RT_SUM, item_id, 1, ts)

                user.update_from(item, OT_ATTR, CT_HAS, RT_SUM, CT_BOOKMARK, RT_SUM, ts)
                user.update_from(item, OT_AVAIL, CT_HAS, RT_SUM, CT_BOOKMARK, RT_SUM, ts)
                user.update_from(item, OT_DURATION, CT_VALUE, RT_SUM, CT_BOOKMARK, RT_SUM, ts)
                user.update_from(item, OT_FEATURE, CT_VALUE, RT_SUM, CT_BOOKMARK, RT_SUM, ts)
                user.update_from(item, OT_ITEMTYPE, CT_HAS, RT_SUM, CT_BOOKMARK, RT_SUM, ts)

    print "Parsing ratings"
    with open(sys.argv[4]) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        count = 1
        for row in reader:
            if count % 100000 == 1:
                print count
            count += 1
            user_id = int(row[0])
            item_id = int(row[1])
            rating = int(row[2])
            ts = int(float(row[3]) * 6)

            item = item_counters[item_id]

            item.add(OT_GLOBAL, CT_HAS_RATING, RT_SUM, '', 1, ts)
            item.add(OT_GLOBAL, CT_HAS_RATING, RT_7D, '', 1, ts)
            item.add(OT_GLOBAL, CT_HAS_RATING, RT_30D, '', 1, ts)
            item.add(OT_GLOBAL, CT_RATING, RT_SUM, '', rating, ts)

            if user_id in target_users:
                user = user_counters[user_id]

                user.add(OT_GLOBAL, CT_HAS_RATING, RT_SUM, '', 1, ts)
                user.add(OT_ITEM, CT_RATING, RT_SUM, item_id, rating, ts)

                user.update_from(item, OT_ATTR, CT_HAS, RT_SUM, CT_HAS_RATING, RT_SUM, ts)
                user.update_from(item, OT_AVAIL, CT_HAS, RT_SUM, CT_HAS_RATING, RT_SUM, ts)
                user.update_from(item, OT_DURATION, CT_VALUE, RT_SUM, CT_HAS_RATING, RT_SUM, ts)
                user.update_from(item, OT_FEATURE, CT_VALUE, RT_SUM, CT_HAS_RATING, RT_SUM, ts)
                user.update_from(item, OT_ITEMTYPE, CT_HAS, RT_SUM, CT_HAS_RATING, RT_SUM, ts)

                user.update_from(item, OT_ATTR, CT_HAS, RT_SUM, CT_RATING, RT_SUM, rating, ts)
                user.update_from(item, OT_AVAIL, CT_HAS, RT_SUM, CT_RATING, RT_SUM, rating, ts)
                user.update_from(item, OT_DURATION, CT_VALUE, RT_SUM, CT_RATING, RT_SUM, rating, ts)
                user.update_from(item, OT_FEATURE, CT_VALUE, RT_SUM, CT_RATING, RT_SUM, rating, ts)
                user.update_from(item, OT_ITEMTYPE, CT_HAS, RT_SUM, CT_RATING, RT_SUM, rating, ts)

    print "Dumping user profiles"
    with open(sys.argv[6], 'w') as user_pickle:
        pickle.dump(user_counters, user_pickle)

    print "Dumping item profiles"
    with open(sys.argv[7], 'w') as item_pickle:
        pickle.dump(item_counters, item_pickle)


