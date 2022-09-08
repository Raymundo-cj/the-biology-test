from Bio.SeqUtils.ProtParam import ProteinAnalysis
import linecache
import sys
outfile = open(sys.argv[2], 'w')
with open (sys.argv[1],'r') as f:
    count = 0
    time = 0
    for idx, line in enumerate(f):
        count += 1
        if count%2==0:
            x = ProteinAnalysis(line)
            for ani in 'AFCDNEQGHLIKMPRSTVWY':
                per = (x.get_amino_acids_percent()[ani])
                time += 1
                if time % 20 == 0:
                    print('did once')
                if per > 0.3:
                    # print(linecache.getline(f, int(count-1)))
                    # print(int(count-1))
                    outfile.write(linecache.getline(sys.argv[1], int(count - 1)))
