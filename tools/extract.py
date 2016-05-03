from sets import Set

data_path = '/home/guanyu/Data/cona_result.txt'
f = open(data_path, 'r')
lines = f.readlines()
f.close()
d = {}

for line in lines:
    items = line.split('\t')
    if len(items) == 7:
        if items[4].find('video') < 0:
            continue

        date = items[0]
        hour = date.split('.')[1].split(':')[0]
        hour = int(hour)
        day  = date.split('.')[0]
        #print day
        if d.has_key(hour):
            if d[hour].has_key(day):
                d[hour][day] += 1
            else:
                d[hour][day] = 1
        else:
            d[hour] = {}
            d[hour][day] = 1

x = []
for i in d.keys():
    sum = 0
    n = 0
    for j in d[i].keys():
        #print i
        #print d[i][j]
        sum += d[i][j]
        n += 1

    #print i
    print sum/n
    x.append(sum/n)


print x
'''
for i in range(0, 24):
    #print i
    print d[i]
'''

'''
for key in keys:
    print key
'''
