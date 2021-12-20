import sys,os

with open(os.path.join('docs','Tutorials','Keep.txt')) as f:
	keepFiles = [x.strip() for x in f.readlines()]

if not len(sys.argv)==1:
	folder = sys.argv[1]

	content = os.listdir(folder)
	if folder[-1]!=os.path.sep:
		folder+=os.path.sep
	if not len(content)==0:
		for f in content:
			if not f in keepFiles:
				try:
					os.remove(folder+f)
				except FileNotFoundError:
					pass
#			else:
#				print('Keeping: '+f)




