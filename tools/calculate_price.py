
res_1 = 0
res_2 = 0
res_3 = 0

dur_1 = 0
dur_2 = 0
dur_3 = 0

tra_1 = 0
tra_2 = 0
tra_3 = 0

f = open('transcoding_data')
lines = f.readlines()
for line in lines:
    line  = line.strip('\n')
    items = line.split(' ')
    items = filter(None, items)
    if int(items[4]) == 409920:
        res_1 += 1
        dur_1 += float(items[0])
        tra_1 += float(items[5])

    if int(items[4]) == 230400:
        res_2 += 1
        dur_2 += float(items[0])
        tra_2 += float(items[5])

    if int(items[4]) == 102240:
        res_3 += 1
        dur_3 += float(items[0])
        tra_3 += float(items[5])

print tra_1 * 1.0 / dur_1
print tra_2 * 1.0 / dur_2
print tra_3 * 1.0 / dur_3
