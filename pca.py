import numpy

def findK (featValues, per = 0.9):
	n = len (featValues)
	total = sum (featValues) * per # 奇异值阈值

	# 寻找合适的特征数量
	s = 0
	for k in range (n):
		s += featValues[k]
		if s >= total:
			return k + 1

def standPCA (dataMat, topNfeat = 9999999):
	
	# 标准化
	meanVals = numpy.mean (dataMat, axis = 0)
	meanRemoved = dataMat - meanVals
	
	# 筛选主特征向量
	covMat = numpy.cov (meanRemoved, rowvar = 0) # 协方差矩阵
	eigVals, eigVects = numpy.linalg.eig (numpy.mat (covMat)) # 求特征值、特征向量
	eigValInd = numpy.argsort (eigVals) # 特征值排序后的下标
	eigValInd = eigValInd[: -(topNfeat + 1) : -1] # 取前topNfeat大特征值
	redEigVects = eigVects[:, eigValInd] # 根据特征值筛选特征向量
	
	# 将样本特征映射为更低维
	lowDDataMat = meanRemoved * redEigVects
	reconMat = (lowDDataMat * redEigVects.T) + meanVals # 将降维后的样本映射在原始维度中
	return lowDDataMat, reconMat
	
def svdPCA (dataMat):
	U, Sigma, VT = numpy.linalg.svd (dataMat) # SVD
	topNfeat = findK (Sigma ** 2) # 寻找合适的特征数量
	lowDDataMat = dataMat * VT.T[:, :topNfeat] # 降维
	
	return lowDDataMat