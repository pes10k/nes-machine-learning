import os
import random

model = '--model hmm'
shake = '--shake 3'
path = '--file ' + os.path.join("generated", "hmm")
for depth in range(2, 7):
	for index in range(0, 25):
		length = '--length ' + str(random.randint(180,200))
		filename = '0' + str(depth)
		if index < 9:
			filename += '0' + str(index+1)
		else:
			filename += str(index+1)
		filename += '.mid'
		full_path = os.path.join(path, filename)
		order = '--order ' + str(depth)
		cmd = 'python predict_songs.py ' + model + ' ' + order + ' ' + shake + ' ' + length + ' ' + full_path
		print cmd
		os.system(cmd)

model = '--model bayes'
import hmm
path = '--file ' + os.path.join("generated", "bayes")
for depth in range(2,7):
	for index in range(0,25):
		length = '--length ' + str(random.randint(180,200))
		filename = '0' + str(depth)
		if index<9:
			filename += '0' + str(index+1)
		else:
			filename += str(index+1)
		filename += '.mid'
		full_path = os.path.join(path, filename)
		order = '--order ' + str(depth)
		cmd = 'python predict_songs.py ' + model + ' ' + order + ' ' + shake + ' ' + length + ' ' + full_path
		print cmd
		os.system(cmd)
#os.system('python predict_songs.py --model hmm --order 4 --shake 3 --length 200 --file 0401.mid')
