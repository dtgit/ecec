# Quick and dirty script to replace all instances of $$version$$ with the version number.

import sys
import string

f = open('../../version.txt', 'r')
ver = f.readline()[:-1]
f.close()

f = open(sys.argv[1], 'r')
ft = f.read()
f.close()

nft = string.replace(ft, '$$version$$', ver)

f = open(sys.argv[1], 'w')
f.write(nft)
f.close()

print 'Done.'
