import sys
import os
import os.path
import time
import threading
import _thread

import tkinter as tk

import copy

#sys.argv = ['0', 'PH2.txt', 'PH2test.txt', '500', 'FC', 'MRV', 'LCV']
#sys.argv = ['0', '16test.txt', '16out.txt', '50']
#sys.argv = ['0', '16test.txt', '16outMRVDHLCV.txt', '50', 'FC', 'LCV', 'DH', 'MRV']
#sys.argv = ['0', '16blank.txt', '16blankout.txt', '50', 'FC']
#sys.argv = ['0', 'PE1.txt', 'PE1out.txt', '50', 'FC']

class BTsolver:

	allTokens = ['0', '1', '2', '3', '4', '5', 
				 '6', '7', '8', '9', 'A', 'B', 
				 'C', 'D', 'E', 'F', 'G', 'H', 
				 'I', 'J', 'K', 'L', 'M', 'N', 
				 'O', 'P', 'Q', 'R', 'S', 'T', 
				 'U', 'V', 'W', 'X', 'Y', 'Z']

	#intTokens = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]

	def __init__(self, inputFileName, outputFileName, timeout):
		self.inName = inputFileName
		self.outName = outputFileName
		self.timeout = int(timeout)

		self.tokenMRV = False
		self.tokenDH = False
		self.tokenLCV = False

		self.startTime = time.time()
		self.startSearch = 0
		self.endSearch = 0
		self.startAC = 0
		self.endAC = 0
		self.status = 'error'

		self.timeUp = False

		self.N = 0
		self.P = 0
		self.Q = 0
		self.tokens = []
		self.grid = []
		self.rowGroup = []
		self.colGroup = []
		self.boxGroup = []

		self.nodeCount = 0
		self.deadEndCount = 0

		#NEW FC CODE
		self.domainDict = {}
		self.rowDict = {}
		self.colDict = {}
		self.boxDict = {}


	def readInput(self):
		if os.path.isfile(self.inName) == False:
			print("Input file does not exist.")
			sys.exit()

		inputFile = open(self.inName)
		inputSettings = inputFile.readline().split()
		self.N = int(inputSettings[0])
		self.P = int(inputSettings[1])
		self.Q = int(inputSettings[2])

		self.tokens = self.allTokens[1:self.N+1]

		self.initDicts()

		idxCount = 0

		inputValues = inputFile.readlines()
		inputFile.close()
		for line in inputValues:
			for value in line.split():
				self.grid.append(value)
				self.rowDict[int(idxCount/self.N)].append(idxCount)
				self.colDict[idxCount%self.N].append(idxCount)
				self.boxDict[int(idxCount/self.Q%self.P) + self.P*int(idxCount/(self.P*self.N))].append(idxCount)
				idxCount += 1

	def initDicts(self):
		for i in range(self.N):
			self.rowDict[i] = []
			self.colDict[i] = []
			self.boxDict[i] = []


	def initConstraints(self):
		self.rowGroup = []
		self.colGroup = []
		self.boxGroup = []
		for i in range(self.N):
			self.rowGroup.append([])
			self.colGroup.append([])
			self.boxGroup.append([])
			for j in range(self.N):
				self.rowGroup[i].append('0')
				self.colGroup[i].append('0')
				self.boxGroup[i].append('0')
		self.refreshConstraints()
		
	def refreshConstraints(self):
		for c, cell in enumerate(self.grid):
			self.rowGroup[int(c/self.N)][c%self.N] = cell
			self.colGroup[c%self.N][int(c/self.N)] = cell
			self.boxGroup[int(c/self.Q%self.P) + self.P*int(c/(self.P*self.N))][c%self.Q + self.Q*int(c/self.N) - self.N*int(c/(self.P*self.N))] = cell

	def updateConstraints(self, index):
		value = self.grid[index]
		rGidx1 = int(index/self.N)
		rGidx2 = index%self.N
		cGidx1 = index%self.N
		cGidx2 = int(index/self.N)
		bGidx1 = int(index/self.Q%self.P) + self.P*int(index/(self.P*self.N))
		bGidx2 = index%self.Q + self.Q*int(index/self.N) - self.N*int(index/(self.P*self.N))
		if value == '0':
			self.rowGroup[rGidx1][rGidx2] = value
			self.colGroup[cGidx1][cGidx2] = value
			self.boxGroup[bGidx1][bGidx2] = value
			return True
		#print(self.rowGroup[rGidx1])
		if (value not in self.rowGroup[rGidx1]) and (value not in self.colGroup[cGidx1]) and (value not in self.boxGroup[bGidx1]):
			self.rowGroup[rGidx1][rGidx2] = value
			self.colGroup[cGidx1][cGidx2] = value
			self.boxGroup[bGidx1][bGidx2] = value
			return True
		else: return False
		#if value not in self.colGroup[cGidx1]:
		#	self.rowGroup[cGidx1][cGidx2] = value
		#	return True
		#else: return False
		#if value not in self.boxGroup[bGidx1]:
		#	self.rowGroup[bGidx1][bGidx2] = value
		#	return True
		#else: return False
		#self.rowGroup[int(index/self.N)][index%self.N] = self.grid[index]
		#self.colGroup[index%self.N][int(index/self.N)] = self.grid[index]
		#self.boxGroup[int(index/self.Q%self.P) + self.P*int(index/(self.P*self.N))][index%self.Q + self.Q*int(index/self.N) - self.N*int(index/(self.P*self.N))] = self.grid[index]

	def checkConstraints(self, value):
		for row in self.rowGroup:
			if row.count(value) > 1:
				return False
		for col in self.colGroup:
			if col.count(value) > 1:
				return False
		for box in self.boxGroup:
			if box.count(value) > 1:
				return False
		return True

	def convert2int(self, string):
		return self.allTokens.index(string)

	def convert2str(self, integer):
		return self.allTokens[interger]

	def findEmptyCell(self):
		try:
			idx = self.grid.index('0')
		except:
			return -1
		return idx

	def findEmptyCells(self):
		emptyList = []
		for idx, value in enumerate(self.grid):
			if value == '0':
				emptyList.append(idx)
		return emptyList

	def solve(self):
		emptyIndex = self.findEmptyCell()
		if emptyIndex == -1:
			return True
		for token in self.tokens:
			self.nodeCount += 1
			self.grid[emptyIndex] = token
			if self.updateConstraints(emptyIndex):
				if self.solve(): 
					return True
			self.grid[emptyIndex] = '0'
			self.updateConstraints(emptyIndex)
			self.deadEndCount += 1

	#NEW FC CODE
	def initdomainDict(self):
		for idx, cell in enumerate(self.grid):
			if cell == '0':
				self.domainDict[idx] = self.tokens[:]

	def updatedomainDict(self, index, value):
		neighbors = self.findEmptyNeighbors(index)
		for idx in neighbors:
			domain = self.domainDict[idx]
			if value in domain:
				domain.remove(value)
				if len(domain) == 0:
					return False
		return True

	def FCsolve(self):
		if self.tokenMRV & self.tokenDH:
			emptyIndex = self.MRVDH()[0]
		elif self.tokenMRV:
			emptyIndex = self.MRV()[0]	
		elif self.tokenDH:
			emptyIndex = self.DH()[0]
		else:
			emptyIndex = self.findEmptyCell()
		if emptyIndex == -1:
			return True
		if self.tokenLCV:
			currentDomain = self.LCV(emptyIndex)
		else:
			currentDomain = copy.deepcopy(self.domainDict[emptyIndex])
		for token in currentDomain:
			tempdomainDict = copy.deepcopy(self.domainDict)
			if self.updatedomainDict(emptyIndex, token):
				self.grid[emptyIndex] = token
				self.nodeCount += 1
				if self.FCsolve(): 
					return True
			self.domainDict = tempdomainDict
			self.deadEndCount += 1
		self.grid[emptyIndex] = '0'
		return False

	def preAC(self):
		for idx, value in enumerate(self.grid):
			if value != '0':
				self.updatedomainDict(idx, value)

	def MRV(self):
		minLen = 36
		minIndexList = []
		emptyList = self.findEmptyCells()
		if len(emptyList) == 0: return [-1]
		for idx in emptyList:
			currLen = len(self.domainDict[idx])
			if currLen < minLen:
				minLen = currLen
				minIndexList = [idx]
			elif currLen == minLen:
				minIndexList.append(idx)
		return minIndexList

	def DH(self):
		maxLen = 0
		maxDegreeList = []
		emptyList = self.findEmptyCells()
		if len(emptyList) == 0: return [-1]
		for idx in emptyList:
			currLen = len(self.findEmptyNeighbors(idx))
			if currLen > maxLen:
				maxLen = currLen
				maxDegreeList = [idx]
			elif currLen == maxLen:
				maxDegreeList.append(idx)
		return maxDegreeList

	def MRVDH(self):
		maxLen = 0
		maxDegreeList = []
		emptyList = self.MRV()
		if emptyList == [-1]: return [-1]
		for idx in emptyList:
			currLen = len(self.findEmptyNeighbors(idx))
			if currLen > maxLen:
				maxLen = currLen
				maxDegreeList = [idx]
			elif currLen == maxLen:
				maxDegreeList.append(idx)
		return maxDegreeList

	def LCV(self, index):
		valueList = self.domainDict[index]
		sortedValueList = []
		sortingList = []
		for value in valueList:
			currCount = self.countConstraints(index, value)
			sortingList.append((value, currCount))
		sortingList.sort(key = lambda x: x[1])
		for element in sortingList:
			sortedValueList.append(element[0])
		return sortedValueList

	def countConstraints(self, index, value):
		constraintCount = 0
		tempDict = copy.deepcopy(self.domainDict)
		neighbors = self.findEmptyNeighbors(index)
		for idx in neighbors:
			domain = tempDict[idx]
			if value in domain:
				tempDict[idx].remove(value)
				constraintCount += 1
				#if len(self.domainDict[idx]) == 0:
					#return False
		return constraintCount

	def findEmptyNeighbors(self, index):
		allNeighbors = []
		#find neighboring row indices
		for i in range(self.N):
			if index in self.rowDict[i]: allNeighbors += self.rowDict[i]
			if index in self.colDict[i]: allNeighbors += self.colDict[i]
			if index in self.boxDict[i]: allNeighbors += self.boxDict[i]
		allNeighbors = list(set(allNeighbors))
		emptyNeighbors = allNeighbors[:]
		for n in allNeighbors:
			if self.grid[n] != '0':
				emptyNeighbors.remove(n)
		if index in emptyNeighbors:
			emptyNeighbors.remove(index)
		return emptyNeighbors


	def checkSolution(self):
		self.refreshConstraints()
		for token in self.tokens:
			if self.checkConstraints(token) == False:
				print("Solution Error")
				for idx,cell in enumerate(self.grid):
					self.grid[idx] = '0'
		if '0' in self.grid:
			for idx,cell in enumerate(self.grid):
				self.grid[idx] = '0'

	def output(self):

		if self.timeUp:
			return

		txt = ''
		txt += "TOTAL_START=" + str(int(self.startTime)) + '\n'
		txt += "PREPROCESSING_START=" + str(int(self.startAC)) + '\n'
		txt += "PREPROCESSING_DONE=" + str(int(self.endAC)) + '\n'
		txt += "SEARCH_START=" + str(int(self.startSearch)) + '\n'
		txt += "SEARCH_DONE=" + str(int(self.endSearch)) + '\n'
		txt += "SOLUTION_TIME=" + str(int(self.endSearch - self.startSearch)) + '\n'
		txt += "STATUS=" + self.status + '\n'
		txt += "SOLUTION=" + str(tuple(self.grid)) + '\n'
		txt += "COUNT_NODES=" + str(self.nodeCount) + '\n'
		txt += "COUNT_DEADENDS=" + str(self.deadEndCount)

		outFile = open(self.outName, 'w')
		outFile.write(txt)
		outFile.close()
		self.updateUI()

		os._exit(1)

	def overTime(self):
		self.timeUp = True

		txt = ''
		txt += "TOTAL_START=" + str(int(self.startTime)) + '\n'
		txt += "PREPROCESSING_START=" + str(int(self.startAC)) + '\n'
		txt += "PREPROCESSING_DONE=" + str(int(self.endAC)) + '\n'
		txt += "SEARCH_START=" + str(int(self.startSearch)) + '\n'
		txt += "SEARCH_DONE=" + str(int(time.time())) + '\n'
		txt += "STATUS=timeout" + '\n'
		txt += "COUNT_NODES=" + str(self.nodeCount) + '\n'
		txt += "COUNT_DEADENDS=" + str(self.deadEndCount) + '\n'

		outFile = open(self.outName, 'w')
		outFile.write(txt)
		outFile.close()
		self.updateUI()

		os._exit(1)

	def updateUI(self):
		txt = ''
		for i, value in enumerate(self.grid):
			if i%self.N == 0:
				txt += '\n'
			if i%(self.N*self.Q) == 0:
				txt += '--' * self.N + '--------\n'
			if i%self.P == 0:
				txt += '| '
			txt += str(value) + ' '
		displayFile = open('display', 'w')
		displayFile.write(txt)
		displayFile.close()
		threading.Timer(1, self.updateUI).start()


if __name__ == '__main__':
	try:
	#s = BTsolver('PE1.txt', 'PE1out.txt', '200')
		s = BTsolver(sys.argv[1], sys.argv[2], sys.argv[3])
		if 'MRV' in sys.argv:
			s.tokenMRV = True
		if 'DH' in sys.argv:
			s.tokenDH = True
		if 'LCV' in sys.argv:
			s.tokenLCV = True
		if 'FC' in sys.argv or s.tokenMRV or s.tokenDH or s.tokenLCV:
			timer = threading.Timer(s.timeout, s.overTime)
			timer.start()
			s.readInput()
			s.initConstraints()
			s.initdomainDict()
			s.startAC = time.time()
			s.preAC()
			s.endAC = time.time()
			s.updateUI()
			s.startSearch = time.time()
			s.FCsolve()
			s.endSearch = time.time()
			timer.cancel()
			s.checkSolution()
			s.status = "success"
		else: #basic BTSearch
			timer = threading.Timer(s.timeout, s.overTime)
			timer.start()
			s.readInput()
			s.initConstraints()
			s.startAC = time.time()
			s.endAC = time.time()
			s.updateUI()
			s.startSearch = time.time()
			s.solve()
			s.endSearch = time.time()
			timer.cancel()
			s.checkSolution()
			s.status = "success"
	except:
		pass
	s.output()

