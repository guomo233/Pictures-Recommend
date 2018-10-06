import tkinter as tk
import recommend as rm
import numpy
import os
import pickle

class Imagerefresher (tk.Frame):
		
		def __init__ (self, master, images, content = [], row = 5, col = 5):
			tk.Frame.__init__ (self, master)
			
			# 存储变量
			self.row = row
			self.col = col
			self.images = []
			self.master = master
			self.selectedImages = [] # 初始化选中集
			self.gridedImages = [] # 在布局中的图片
			self.blankImage = tk.PhotoImage (file = 'blank.gif')
			self.scale = tk.Scale (self, from_ = 0, to = (len (images) + row * col - 1) // (row * col) - 1, 
									length = 40 * row) # 设置滑动调
			
			# 添加图片
			self.addImages (images, content)

			# 刷新界面
			self.refresh ()

			# 绑定滑动事件
			self.scale.bind ('<ButtonRelease-1>', self.changeScale)
			# 显示滑动条
			self.scale.grid (row = 0, column = col, rowspan = row, stick = tk.E)
		
		def unselectImages (self, images):
			for image in images.copy():
				if image in self.selectedImages:
					image['highlightbackground'] = 'white'
					self.selectedImages.remove (image)
					
		def unselectAll (self, event):
			self.unselectImages (self.selectedImages)

		def selectImage (self, event):
				
				# 获取所选图片
				label = event.widget
				
				# 判断是选中还是退选
				if label not in self.selectedImages: # 选中
					label['highlightbackground'] = 'black'
					self.selectedImages.append (label)
				else: # 退选
					label['highlightbackground'] = 'white'
					self.selectedImages.remove (label)
					
		def addImages (self, images, content = []):
			imagess2str = [str (image['image']) for image in self.images]
			
			for i in range (len (images)):
				# 不重复添加
				if str(images[i]) in imagess2str:
					continue
				# 生成图片上的文字
				if i < len (content):
					text = content[i]
				else:
					text = ''
				imageLabel = tk.Label (self,
										image = images[i],
										highlightbackground = 'white',
										compound = tk.CENTER,
										text = text,
										highlightthickness = 2,
										width = 32,
										height = 32)
				imageLabel.bind ('<Button-1>', self.selectImage) # 绑定事件
				self.images.append (imageLabel)
				
				# 更新scale
				self.scale['to'] = (len (self.images) + self.row * self.col - 1) // (self.row * self.col) - 1
		
		def removeImages (self, images):
			# 退选
			self.unselectImages (images)
			
			# 删除
			for image in images.copy():
				self.images.remove (image)
			
			# 更新scale
			self.scale['to'] = (len (self.images) + self.row * self.col - 1) // (self.row * self.col) - 1
					
		def removeAllImages (self):
			self.removeImages (self.images)
				
		def changeScale (self, event):
			self.refresh ()
			
		def refresh (self):
			
			# 清空布局中存在的图片
			for image in self.gridedImages.copy():
				image.grid_forget ()
				self.gridedImages.remove (image)
			
			# 将图片放入布局
			for i in range (self.row):
				for j in range (self.col):
					# 计算图片索引
					imageIndex = self.scale.get() * self.row * self.col + i * self.col + j
					if imageIndex + 1 <= len (self.images): # 如果还有足够的图片
						self.images[imageIndex].grid (row = i, column = j)
						self.gridedImages.append (self.images[imageIndex])
					else: # 没有足够的图片则填充空白
						blankImage = tk.Label (self, image = self.blankImage, 
												highlightbackground = 'white',
												compound = tk.CENTER,
												text = '',
												highlightthickness = 2,
												width = 32,
												height = 32)
						# 当点到空白，所有选中的都退选
						blankImage.bind ('<Button-1>', self.unselectAll)
						blankImage.grid (row = i, column = j)
						self.gridedImages.append (blankImage)
		
		def getSelectedImages (self):
			return self.selectedImages.copy ()
			
		def getAllImages (self):
			return self.images.copy ()

def addSelectedImages ():
	
	# 获取选中图片
	images = imageDisplerRm.getSelectedImages()
	images.extend (imageDisplerAll.getSelectedImages())

	# 退选这些图片
	imageDisplerAll.unselectImages (images)
	imageDisplerRm.unselectImages (images)

	# 将所选图片加入选中集
	imageDisplerSelected.addImages ([image['image'] for image in images])
	# 刷新
	imageDisplerSelected.refresh ()
	
def removeSelectedImages ():

	# 获取选中图片
	images = imageDisplerSelected.getSelectedImages()
	
	# 删除选中图片
	imageDisplerSelected.removeImages (images)
	# 刷新
	imageDisplerSelected.refresh ()
	
def refrushRecommend ():

	# 获取阈值
	threshold = float (etThreshold.get ())
	
	# 将当前所选图片生成向量
	selectedImages = imageDisplerSelected.getAllImages ()
	project = getProject (selectedImages)

	# 获取推荐图片
	if len (dataMat) > 0:
		if varSVD.get() == 0:
			estMethod = rm.standEst
		else: # SVD	
			estMethod = rm.svdEst
		similarImages = rm.recommend (numpy.mat (dataMat), numpy.array (project), per = threshold, estMethod = estMethod)
	else:
		similarImages = []
	
	# 删除当前所有图片
	imageDisplerRm.removeAllImages ()
	
	# 加入图片
	imageDisplerRm.addImages ([imagesAll[similarImage[0]] for similarImage in similarImages], 
								['%.2f' % similarImage[1] for similarImage in similarImages])
	# 刷新
	imageDisplerRm.refresh ()

def getProject (images):
	project = [0] * len (imagesAll)
	imagesAll2str = [str (image) for image in imagesAll]
	for image in images:
		project[imagesAll2str.index (image['image'])] = 1
		
	return project
	
def endProject ():
	# 将项目存入dataMat
	selectedImages = imageDisplerSelected.getAllImages ()
	project = getProject (selectedImages)
	storageProject (dataMat, project)
	
	# 删除已选集并刷新
	imageDisplerSelected.removeAllImages ()
	imageDisplerSelected.refresh ()
	
	# 删除推荐集并刷新
	imageDisplerRm.removeAllImages ()
	imageDisplerRm.refresh ()
	
def storageDataMat (dataMat):
	with open ('datamat.pkl', 'wb') as fr:
		pickle.dump (dataMat, fr)		
		
def storageImages (images):
	with open ('images.pkl', 'wb') as fr:
		pickle.dump (images, fr)

def storageProject (dataMat, project):
	dataMat.append (project)
	storageDataMat (dataMat)

def loadData (dirname):

	# 导入图片
	try:
		with open ('images.pkl', 'rb') as fr:
			images = pickle.load (fr)
	except FileNotFoundError:
		images = []

	# 导入dataMat
	try:
		with open ('datamat.pkl', 'rb') as fr:
			dataMat = pickle.load (fr)
	except FileNotFoundError:
		dataMat = []

	# 更新images
	for filename in [files[2] for files in os.walk (dirname)][0]:
		if filename not in images and filename != '.DS_Store':
			images.append (filename)
	storageImages (images)

	# 更新dataMat
	for project in dataMat:
		projectLenght = len (project)
		project.extend ([0] * (len (images) - projectLenght))
	storageDataMat (dataMat)
	
	return dataMat, images


################################################################################

if __name__ == '__main__':
	root = tk.Tk ()

	# 导入数据
	dataMat, imagesFilename = loadData ('images')
	imagesAll = [tk.PhotoImage (file = 'images/' + imageFilename) for imageFilename in imagesFilename]

	# 定义上下两个框架
	frameShow = tk.Frame (root)
	frameShow.pack (side = tk.LEFT)
	frameControl = tk.Frame (root)
	frameControl.pack (side = tk.RIGHT)

	# 显示3个图片显示组件
	imageDisplerAll = Imagerefresher (frameShow, imagesAll, row = 10, col = 5)
	imageDisplerAll.grid (row = 0, column = 0, rowspan = 2)

	imageDisplerRm = Imagerefresher (frameShow, [])
	imageDisplerRm.grid (row = 0, column = 1)

	imageDisplerSelected = Imagerefresher (frameShow, [])
	imageDisplerSelected.grid (row = 1, column = 1)

	# 定义控制面板
	tk.Label (frameControl, text = '阈值:').grid (row = 0, column = 0)
	etThresholdValue = tk.StringVar ()
	etThresholdValue.set ('0.7') # 默认值
	etThreshold = tk.Entry (frameControl, width = 3, textvariable = etThresholdValue)
	etThreshold.grid (row = 0, column = 1)

	varSVD = tk.IntVar ()
	cbSVD = tk.Checkbutton (frameControl, text = 'SVD', variable = varSVD)
	cbSVD.grid (row = 1, column = 0)

	btAdd = tk.Button (frameControl, text = '添加', command = addSelectedImages, width = 5)
	btAdd.grid (row = 2, column = 0, columnspan = 2, stick = tk.N)

	btRemove = tk.Button (frameControl, text = '移除', command = removeSelectedImages, width = 5)
	btRemove.grid (row = 3, column = 0, columnspan = 2)

	btRecommend = tk.Button (frameControl, text = '推荐', command = refrushRecommend, width = 5)
	btRecommend.grid (row = 4, column = 0, columnspan = 2)

	btProjectEnd = tk.Button (frameControl, text = '结项', command = endProject, width = 5)
	btProjectEnd.grid (row = 5, column = 0, columnspan = 2)



	root.mainloop ()