import numpy as np
from scipy.stats import chisquare
import csv, re, json, os, math, string, cgi

### The following variables only apply to the BDH Spring 2013 Poll.
OFFSET = 1
DATA_FILE = "data.csv"
QUESTION_FILE = "newquestions.csv"
BAR_GRAPH_FILE = "bar.html"
CHI_SQUARES = []
###
class Document:
	def __init__(self, title, tables, currDir, transposedDir):
		strings = []
		strings.append('<!DOCTYPE html PUBLIC "-//IETF//DTD HTML 2.0//EN">')
		strings.append('<HTML><HEAD> <TITLE>')
		strings.append(title)
		strings.append('</TITLE>')
		strings.append('<style> .bottom-three {margin-bottom: 3cm;}</style>')
		strings.append('<link href="/bootstrap/css/bootstrap.css" rel="stylesheet">')
		strings.append('<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7/jquery.js"></script>')

		strings.append('</HEAD><BODY>')
		strings.append('<center><H1>'+title+'</H1></center>')
		strings.append('<div class="bottom-three">')
		strings.append('<center><a class="btn btn-info" href="'+str(transposedDir)+'">Invert Axes</a><a class="btn btn-success" href="../../html/matrix.html">Back to Matrix</a></center>')
		strings.append('</div>')
		strings.append('<div class="container">')
		
		for index, table in enumerate(tables):
			csvName = currDir+"/"+re.sub('[\W_]+', '', title)+str(index)+".csv"
			barName = currDir+"/"+re.sub('[\W_]+', '', title)+str(index)+".html"
			#print csvName, barName
			table.writeCSV(csvName, re.sub('[\W_]+', '', title)+str(index)+".csv")
			table.writeBarGraph(barName, re.sub('[\W_]+', '', title)+str(index)+".html")
			strings.append('<div class="bottom-three">')
			strings.append('<CENTER><P>')
			strings.append(table.write(index))
			strings.append('</P></CENTER>')
			strings.append('</div>')
		strings.append('</div>')
		strings.append('</BODY></HTML>')
		
		self.text = ''.join(strings)
	
class CrossTab:
	def __init__(self, title, xLabel, yLabel, data):
		self.xLabel = xLabel
		self.yLabel = yLabel
		self.data = data
		self.title = title
		
		self.expectedData = np.zeros((self.data.shape[0]-1, self.data.shape[1]-1))
		self.percents = np.zeros(self.data.shape)
		for i in xrange(self.percents.shape[0]):
			for j in xrange(self.percents.shape[1]):
				totalCol = float(self.data[i][-1])
				if totalCol == 0:
					self.percents[i][j] = 0
				else:
					self.percents[i][j] = self.data[i][j]/totalCol
		#print self.percents
				
		total = float(self.data[-1][-1])
		for i in xrange(self.data.shape[0]-1):
			for j in xrange(self.data.shape[1]-1):
				self.expectedData[i][j] = self.data[i][-1]*self.data[-1][j]/total
		
		toCompare = self.data[:-1, :-1]
		degrees = (toCompare.shape[0]-1)*(toCompare.shape[1]-1)
		diff = (toCompare.size-1)-degrees
		self.chisquare = chisquare(toCompare.flatten(), f_exp=self.expectedData.flatten(), ddof=diff)
		if self.chisquare[1] != 0:
			CHI_SQUARES.append(np.log(self.chisquare[1]))
		
	def writeCSV(self, fileName, shortFileName):
		self.csvFile = shortFileName
		with open(fileName, 'w') as csvFile:
			writer = csv.writer(csvFile, delimiter=",", quotechar='"')
			writer.writerow(["Option"]+self.yLabel)
			for index, element in enumerate(self.xLabel):
				writer.writerow([element]+list(self.data[index][:-1]))
		#print self.data.T
	
	def writeBarGraph(self, fileName, shortFileName):
		self.barFile = shortFileName
		#print self.barFile
		f = open(BAR_GRAPH_FILE,'r')
		text = f.read()
		text = string.replace(text, "test.csv", self.csvFile)
		f.close()
		with open(fileName, 'w') as barFile:
			barFile.write(text)
		return text
		
		
	def write(self, id):
		
		colorLabel = '<p class="text-success">' if self.chisquare[1] < 0.05 else '<p class="text-info">'
		tab1 = str(id)+"001"
		tab2 = str(id)+"002"
		strings = []
		strings.append('<h5>')
		strings.append(self.title[0])
		strings.append('</h5>')
		strings.append('<h5>')
		strings.append(self.title[1])
		strings.append('</h5>')
		
		strings.append('<div class="tabbable"><ul id="tabs" class="nav nav-tabs" data-tabs="tabs"><li class="active"><a href="#'+tab1+'" data-toggle="tab">Spreadsheet</a></li><li><a href="#'+tab2+'" data-toggle="tab">Bar Graph</a></li> </ul>')
		
		strings.append('<div class="tab-content"><div class="tab-pane active" id="'+tab1+'">')
		
		strings.append('<table class="table table-hover" width="300px">')
		strings.append('<tr>')
		strings.append('<td>')
		strings.append(' ')
		strings.append('</td>')
		for i in self.xLabel:
			strings.append('<td>')
			strings.append(i)
			strings.append('</td>')
			
		strings.append('<td>')
		strings.append('Total')
		strings.append('</td>')
		strings.append('</tr>')
		#print self.data.shape
		for index, j in enumerate(self.yLabel):
			strings.append('<tr>')
			strings.append('<td>')
			strings.append(j)
			strings.append('</td>')
			
			for index2, k in enumerate(self.data.T[index]):
				strings.append('<td>')
				strings.append(str(k))
				strings.append(colorLabel)
				strings.append(str(100*round(self.percents[index2][index], 3))+"%")
				strings.append('</p>')
				strings.append('</td>')	
		
			strings.append('</tr>')

		strings.append('<tr>')
		strings.append('<td>')
		strings.append('Total')
		strings.append('</td>')
		
		for i in xrange(self.data.shape[0]):
			strings.append('<td>')
			strings.append(str(self.data[i][-1]))
			strings.append(colorLabel)
			strings.append(str(100*round(self.percents[i][-1], 3))+"%")
			strings.append('</p>')
			strings.append('</td>')
			
		strings.append('</tr>')	
		strings.append('</table>')
		
		strings.append('</div><div class="tab-pane" id="'+tab2+'">')
		
		strings.append('<iframe src="'+self.barFile+'"width="900" height="500" scrolling="no" frameborder="0"></iframe>')
		strings.append('</div>') 
		strings.append('<script type="text/javascript">jQuery(document).ready(function ($){$("#tabs").tab();});</script>  ')
		strings.append('</div></div>')
		strings.append('<script type="text/javascript" src="/bootstrap/js/bootstrap.js"></script>')
		if self.chisquare[1] < 0.05:
			strings.append('<div class="alert alert-success">')
		else:
			strings.append('<div class="alert alert-info">')
		
		strings.append('<b> Chi squared p-value: '+str(round(self.chisquare[1], 3))+"</b>")
		strings.append('</div>')
		
		return ''.join(strings)
		
class Question:
	def __init__(self, id, index, choose_multiple, options, shortId):
		self.id = id
		self.choose_multiple = choose_multiple
		self.index = index
		self.options = options
		self.shortId = shortId
		
class PollData:
	def __init__(self, dataFile, questionsFile):
		self.questions = self.parseQuestions(questionsFile)
		self.responses = self.parseData(dataFile)
		#print self.questions
		
	def parseQuestions(self, questionsFile):
		questions = {}
		with open(questionsFile, 'r') as csvFile:
			reader = csv.reader(csvFile, delimiter=',', quotechar='"')
			firstLine = reader.next()
			counter = 0
			for row in reader:
				#print row
				options = filter(None, row[3:])
				#print len(options), row[1]
				b = False
				if row[0].upper() == "TRUE":
					b = True
				q = Question(row[2], counter+OFFSET, b, list(enumerate(options)), row[1])
				q.listOptions = options
				#print q.listOptions
				questions[row[2]] = q
				counter += 1
		return questions
	
	
	def parseData(self, fileName):
		responses = []
		with open(fileName, 'r') as csvFile:
			reader = csv.reader(csvFile, delimiter=',', quotechar='"')
			firstLine = reader.next()
			for row in reader:
				response = {}
				for q in self.questions.values():
					#raw = self.parseEntry(row,q)
					parsed = self.parseEntry(row, q)
					response[q.id] = parsed

					#if raw:
					#	response[q.id] = [q.options[int(i)-1] for i in raw]
					#else:#invalid answers and no answer
					#	response[q.id] = None
				responses.append(response)
		return responses
					
	def parseEntry(self, row, question):
		entry = row[question.index]
		#print entry
		answers = [option for option in question.listOptions if option in entry]
		#print answers, entry
		#temp = filter(None, entry.strip().replace('.', ',').split(','))
		#print temp
		#answers = filter(lambda x: 1 <= int(x) <= len(question.options), temp)
		#print answers, question.choose_multiple
		#temp2 = filter(lambda x: x in question.listOptions, answers)

		#print temp, question.listOptions
		#exit()
		#print answers
 		answers2 = map(lambda x: question.listOptions.index(x), answers)
 		#print answers, temp
		if ((not question.choose_multiple) and len(answers2) > 1) or len(answers2) < 1:
			#print answers, entry
			#print question.shortId, entry, question.choose_multiple, len(answers2)
			return None
		return answers2
		#return set([int(i) for i in answers])
	
	
	def crossTab(self, question1, question2):
		tables = []
		"""
		if (not question1.choose_multiple) and (not question2.choose_multiple):
			numbers = np.zeros((len(question1.options)+1, len(question2.options)+1))
			labels1 = question1.options
			labels2 = question2.options
			print labels1
			print labels2
			for r in self.responses:
				r1 = r[question1.id]
				r2 = r[question2.id]
				if r1 != None and r2 != None:
					i1, t1 = r1[0]
					i2, t2 = r2[0]
					numbers[i1][i2] += 1
			for i in xrange(len(question1.options)):
				s = 0.0
				for j in xrange(len(question2.options)):
					s += numbers[i][j]
				numbers[i][-1] = s
			
			for i in xrange(len(question2.options)):
				s = 0.0
				for j in xrange(len(question1.options)):
					s += numbers[j][i]
				numbers[-1][i] = s
			
			numbers[-1][-1] = np.sum(numbers[-1][:])
			tables.append(CrossTab(labels2, labels1, numbers))
			#print numbers
		"""
		
		options1 = []
		options2 = []
		
		if question1.choose_multiple:
			options1 = question1.options[:]
		else:
			options1.append(None)
		
		if question2.choose_multiple:
			options2 = question2.options[:]
		else:
			options2.append(None)
			
		#print question1.id, question2.id
		
		for o1 in options1:
			for o2 in options2:
				dim1 = 3 if o1 else len(question1.options)+1
				dim2 = 3 if o2 else len(question2.options)+1
				#print dim2
				numbers = np.zeros((dim1, dim2), dtype=np.int32)
				for r in self.responses:
					r1 = r[question1.id]
					r2 = r[question2.id]
					index1 = -1
					index2 = -1
					if r1 != None and r2 != None:
						#print o1, r1
						if o1:
							index1 = 0 if (o1[0] in r1) else 1
						else:
							#index1 = r1[0][0]
							index1 = r1[0]
						if o2:
							#print o2
							index2 = 0 if (o2[0] in r2) else 1
						else:
							#index2 = r2[0][0]
							index2 = r2[0]
						
						numbers[index1][index2] += 1
					
				for i in xrange(dim1-1):
					s = 0
					for j in xrange(dim2-1):
						s += numbers[i][j]
					numbers[i][-1] = s
				
				for i in xrange(dim2-1):
					s = 0
					for j in xrange(dim1-1):
						s += numbers[j][i]
					numbers[-1][i] = s
					
				numbers[-1][-1] = np.sum(numbers[-1][:])
				
				xLabels = [o1[1], "Not "+o1[1]] if o1 else [i[1] for i in question1.options]
				yLabels = [o2[1], "Not "+o2[1]] if o2 else [i[1] for i in question2.options]
				title1 = question1.id+" Option: "+str(o1[1]) if o1 else question1.id
				title2 = question2.id+" Option: "+str(o2[1]) if o2 else question2.id
				
				tables.append(CrossTab((title1, title2), xLabels, yLabels, numbers))
				#print question1, question2, numbers
		return tables
	
	def allCrossTabs(self):
		allTables = {}
		for k1, v1 in self.questions.items():
			allTables[k1] = {}
			for k2, v2 in self.questions.items():
				allTables[k1][k2] = self.crossTab(v1,v2)
		self.allTables = allTables
		return allTables
	
	def createJSON(self):
		root = {}
		root["nodes"] = []
		root["links"] = []
		
		temp = {}
		for index,k in enumerate(self.allTables.keys()):
			root["nodes"].append({"name":self.questions[k].shortId, "index":index})
			temp[k] = index
			
		for k,v in self.allTables.items():
			for k2, v2 in v.items():
				tables = v2
				value = 0
				for t in tables:
					curr = 0
					c = t.chisquare[1]
					print c, self.questions[k].shortId,temp[k], temp[k2]
					if c < 0.0001:
						curr += 1
					if c < 0.001:
						curr += 1
					if curr > value:
						value = c
					if c < .001:
						value = c
				
				root["links"].append({"source":temp[k], "target":temp[k2], "value":value})
		
		f = open('adjacency.json', 'w')
		#print "hello!"
		f.write(json.dumps(root))
		f.close()
		
	def createDocuments(self):
		dataDir = "data"
		if not os.path.exists(dataDir):
			os.makedirs(dataDir)
		for k,v in self.allTables.items():
			firstDir = self.questions[k].shortId
			tempDir = dataDir+'/'+firstDir
			if not os.path.exists(tempDir):
				os.makedirs(tempDir)
			for k2, v2 in v.items():
				secondDir = self.questions[k2].shortId
				fileDir = tempDir+'/'+secondDir+'.html'
				transposedDir = '../../'+dataDir+"/"+secondDir+"/"+firstDir+".html"
				#print tempDir
				doc = Document(firstDir+" vs. "+secondDir, v2, tempDir, transposedDir)
				f = open(fileDir, 'w')
				f.write(doc.text)
				f.close()
		
			
		
if __name__ == '__main__':
	#questions = [Question(*i) for i in QUESTIONS]
	data = PollData(DATA_FILE, QUESTION_FILE)
	data.allCrossTabs()
	data.createDocuments()
	data.createJSON()
	
	#tables = data.crossTab(data.questions.values()[0], data.questions.values()[4])
	#table = tables[0]
	#table.writeCSV('test.csv')
	#doc = Document('test', tables)
	#f = open('test.html', 'w')
	#f.write(doc.text)
	#f.close()
	
	