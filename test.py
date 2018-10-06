import numpy
import random
import recommend
import rmSystem
import pickle
import csv

def dataProduct (imageNum, rowsNum, classNum, rowImageNumMin, rowImageNumMax, noise = 0.2):
	rows = []
	classid = 0
	t = 1
	
	for i in range (0, rowsNum):
		row = [0] * imageNum
		# 统计该设计过程中所用图片数量
		useImageNum = random.randint (rowImageNumMin, rowImageNumMax)
		# 生成非噪声数据
		for j in range (0, int(useImageNum * (1 - noise))):
			k = random.randint (classid, classid + imageNum/classNum - 1)
			while (row[k]):
				k = random.randint (classid, classid + imageNum/classNum - 1)
			row[k] = 1
		# 生成噪声数据
		for j in range (0, int(useImageNum * noise)):
			k = random.randint (0, imageNum - 1)
			while (row[k]):
				k = random.randint (0, imageNum - 1)
			row[k] = 1
		
		rows.append (row)
		# 移动色阶
		if i > (t * rowsNum / classNum):
			classid += imageNum / classNum
			t += 1

	return rows

def MAEmean (dataMat, rows, estMethod = recommend.svdEst, simMeas = recommend.cosSim):

	MAEsum = 0
	for row in rows:
		MAEsum += recommend.MAE(numpy.mat (dataMat), numpy.array(row), simMeas = simMeas, estMethod = estMethod)
	return MAEsum / len (rows)


def csvProduct (maxi, step, testNum):
	
	csvStore = []
	
	for i in range (step, maxi, step):
	
		# train
		dataMat = dataProduct (260, i, 5, 20, 35)

		# test
		testMat = dataProduct (260, testNum, 5, 20, 35)
		
		# 测试
		recommend.xformedItems = None
		maemean = MAEmean(dataMat, testMat, estMethod = recommend.standEst)
		print ('i = %d MAE = %f' % (i, maemean))
		csvStore.append ([i, maemean])
		
	with open('stand.csv', 'w') as f:
		writer = csv.writer(f)
		writer.writerows(csvStore)
		
def test ():
	# train
	dataMat = dataProduct (260, 100, 5, 15, 35)
	
	rmSystem.storageDataMat(dataMat)
	
#	# test
#	testMat = dataProduct (260, 10, 5, 15, 35)
#	
#	maemean = MAEmean(dataMat, testMat, estMethod = recommend.svdEst)
#	print (maemean)
	
		
if __name__ == '__main__':
#	# train
#	dataMat = dataProduct (260, 100, 5, 20, 35)
#	
#	rmSystem.storageDataMat(dataMat)
#	csvProduct (1000, 10, 10)

	test ()