import numpy
import pca
import pickle

# 存储降维后的矩阵
xformedItems = None

def ecludSim (inA, inB):
	return 1.0 / (1.0 + numpy.linalg.norm (inA - inB))

def pearsSim (inA, inB):
	if len (inA) < 3:
		return 1.0
	return 0.5 + 0.5 * numpy.corrcoef (inA, inB, rowvar = 0)[0][1]

def cosSim (inA, inB):
	num = float (inA.T *  inB)
	denom = numpy.linalg.norm (inA) * numpy.linalg.norm (inB)
	if num == 0:
		return 0
	return 0.5 + 0.5 * num / denom
	
def standEst (dataMat, project, simMeas, item):
	n = numpy.shape (dataMat)[1]
	simTotal = 0.0 ; ratSimTotal = 0.0
	
	# 遍历物品，对item进行评价估计
	for j in range (n):
		projectRating = project[j] # 当前用户对物品j的评价
		if projectRating == 0:
			continue

		similarity = simMeas (dataMat[:, item], dataMat[:, j]) # 计算相似度
		simTotal += 1 # 相似度累计
		ratSimTotal += similarity * projectRating # 对item进行评价估计
	
	# 估算对item的评价
	if simTotal == 0:
		return 0
	else:
		return ratSimTotal / simTotal
		
def svdEst (dataMat, project, simMeas, item):
	n = numpy.shape (dataMat)[1]
	simTotal = 0.0 ; ratSimTotal = 0.0
	
	# PCA降维
	global xformedItems
	if (xformedItems == None):
		xformedItems = pca.svdPCA (dataMat.T)
#		try:
#			with open ('pca.pkl', 'rb') as fr:
#				xformedItems = pickle.load (fr)
#		except FileNotFoundError: 
#			xformedItems = pca.svdPCA (dataMat.T)
#			with open ('pca.pkl', 'wb') as fr:
#				pickle.dump (xformedItems, fr)
		
	# 遍历物品，对item进行评价估计
	for j in range (n):
		projectRating = project[j] # 当前项目对图片j的使用情况
		if projectRating == 0:
			continue
		similarity = simMeas (xformedItems[item, :].T, xformedItems[j, :].T) # 在低维空间计算相似度
		simTotal += 1 # 相似度累计
		ratSimTotal += similarity * projectRating # 对item进行风格相似度计算
	
	# 估算item的风格相似度
	if simTotal == 0:
		return 0
	else:
		return ratSimTotal / simTotal

def recommend (dataMat, project, per = 0.7, simMeas = cosSim, estMethod = svdEst):
	unratedItems = numpy.nonzero (project == 0)[0]
	if len (unratedItems) == 0:
		return []

	# 统计所有未使用的图片
	itemScores = []
	for item in unratedItems:
		estimatedScore = estMethod (dataMat, project, simMeas, item) # 获取评价的估计值
		itemScores.append ((item, estimatedScore))
	
	# 返回风格相似度per以上的图片
	itemScores = filter (lambda jj: jj[1] >= per, itemScores)
	return sorted (itemScores, key = lambda jj: jj[1], reverse = True)
	
def MAE (dataMat, project, simMeas = cosSim, estMethod = svdEst):
	ratedItems = numpy.nonzero (project == 1)[0]

	# 统计所有使用过的图片
	sumSores = 0
	for item in ratedItems:
		project[item] = 0
		estimatedScore = estMethod (dataMat, project, simMeas, item) # 获取评价的估计值
		project[item] = 1
		sumSores += 1 - estimatedScore
	
	return sumSores / len (ratedItems)