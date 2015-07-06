
fname = 'trans_res.dat'
f = open(fname, 'r')
lines = f.readlines()
f.close()

for line in lines:
    v = []
    line = line.strip('\n')
    items = line.split(' ')
    v.append(items[1])
    v.append(int(items[2]) * int(items[3]))
    v.append(items[4])
    v.append(items[5])
    w = int(items[7].split('x')[0])
    h = int(items[7].split('x')[1])
    v.append(w*h)
    v.append(items[8])
    for i in v:
        print i, ' ',
    print ' '
