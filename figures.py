# import matplotlib.pyplot as plt
import numpy as np 
import lxml.etree as et
from localconfig import config
from ast import literal_eval
import os


def checkFile(fileName):
	if not os.path.exists(fileName):
		raise FileNotFoundError(fileName+" does not exist!")

class Geo:
	def getPoints(self):
		print("Not implemented yet!")

class Line(Geo):
	def __init__(self, start,end,backto=1):
		self.start=start
		self.end=end
		self.bt=backto
	def getPoints(self):
		yield self.start
		yield self.end
		yield self.getSingle(self.bt)
	def getSingle(self,rel):
		x1,y1=self.start
		x2,y2=self.end
		xm=x1*(1-rel)+x2*rel
		ym=y1*(1-rel)+y2*rel
		return (xm,ym)
	
	def shift(self, dx=0,dy=0):
		self.start=np.add(self.start,dx,dy)
		self.end=np.add(self.end,dx,dy)

class Circle:
	def __init__(self,center,radius,segment):
		self.centerX,self.centerY=center
		self.radius=radius
		self.begin,self.end=segment
		pointsPerDegree=.5
		self.totalPoints=int(abs(self.end-self.begin)*pointsPerDegree+1)

	def getPoints(self):
		for angle in np.linspace(self.begin,self.end,self.totalPoints):
			yield self.getPoint(angle)
	
	def shift(self, dx=0,dy=0):
		self.centerX+=dx
		self.centerY+=dy
	
	def getSingle(self, rel):
		angle=self.begin*(1-rel)+self.end*rel
		return self.getPoint(angle)
	
	def getPoint(self, angle):
		x=self.radius*np.sin(np.pi/180*-angle)+self.centerX
		y=self.radius*np.cos(np.pi/180*angle)+self.centerY
		r= np.array([x,y])
		return r

class KML:
	def __init__(self,settings):
		#first we check if we can do anything at all:
		self.settings=settings
		checkFile(self.settings["letterLib"])
		#no exception? ok, we're good. run generateAllLetters whenever you want
	
	def generateAllLetters(self):
		writing=self.settings["writing"]
		self.makeKmlHeader()
		dx=0
		letterSpacing=.2 #TODO: customizable
		for charLetter in writing.upper():
			letter=Letter(charLetter,self.settings)
			points=letter.generate((dx,0))
			dx+=float(letter.letterSubtree.get("width"))+letterSpacing
			self.drawLetter(charLetter,points)
		self.makeFile(writing)


	def makeKmlHeader(self):
		self.kml=et.Element("kml",xmlns="http://www.opengis.net/kml/2.2")
		self.base=et.SubElement(self.kml,"Document")
		
	def lineStyle(self,placemark):
		style=et.SubElement(placemark,"Style")
		lstyle=et.SubElement(style,"LineStyle")
		col=et.SubElement(lstyle,"color")
		col.text="ff0000ff"
		w=et.SubElement(lstyle,"width")
		w.text="1"
	
	def drawLetter(self,charLetter, points):
		placemark=et.SubElement(self.base,"Placemark")
		name=et.SubElement(placemark,"name")
		name.text=charLetter

		lstring=et.SubElement(placemark,"LineString")
		coordinates=et.SubElement(lstring,"coordinates")
		coordinates.text=points
		self.lineStyle(placemark)

	def makeFile(self, writing):
		tree=et.ElementTree(self.kml)
		folderName=self.settings["writingsDir"]+"/"
		filename=writing+".kml"
		filepath=folderName+filename
		None if os.path.exists(folderName) else os.mkdir(folderName)
		tree.write(filepath,xml_declaration=True,encoding="utf-8",pretty_print=True)

class XmlLetter:
	"""
	read Letter from XML-File and turn it into Lines or Circles (returned by makeElements)
	"""
	def __init__(self, letter):
		self.letterName=letter
		self.treeRoot=self.getXMLRoot()
		self.letterSubtree=self.getXmlSubtree()
		self.elements=self.makeElements()
	
	def getXMLRoot(self):
		self.letterLibFilePath=self.settings["letterLib"]
		letterLibTree=et.parse(self.letterLibFilePath,et.XMLParser())
		return letterLibTree.getroot()
	
	def getXmlSubtree(self):
		# root=self.tree.getroot()
		xmlSubtree= self.treeRoot.find(f'letter[@name="{self.letterName}"]') 
		if xmlSubtree is None:
			raise NameError(f"Symbol {self.letterName} not found in {self.letterLibFilePath}")
		return xmlSubtree
		
	def getPairFromXML(self, XmlElement,first='x',sec='y'):
			#TODO: Regex to match more general input
		pointDict=literal_eval(XmlElement.text)
		return (pointDict[first],pointDict[sec])

	def makeElements(self):
		for element in self.letterSubtree:
			if element.tag=="Line":
				start=self.getPairFromXML(element.find("start"))
				end=self.getPairFromXML(element.find("end"))
				backtrack=float(element.find("backtrack").text)
				yield Line(start,end,backtrack)
			if element.tag=="Circle":
				center=self.getPairFromXML(element.find("center"))
				segment	=self.getPairFromXML(element.find("section"),"alpha1","alpha2")
				radius=float(element.find("radius").text)
				yield Circle(center,radius,segment)


class Letter(XmlLetter):	
	def __init__(self, charLetter,settings):
		self.settings=settings
		super().__init__(charLetter)
		# self.filename=filename
		# self.charLetter=charLetter

	def getWidth(self):
		return self.getWidth()

	def getAllPoints(self):
		for e in self.makeElements():
			yield from e.getPoints()

	def getRotatedPoints(self, angle,shift):
		phi=angle/180*np.pi
		dx,dy=shift
		rotMat=np.array(
		[[np.cos(phi),np.sin(phi)],
		[-np.sin(phi),np.cos(phi)]])

		for x,y in self.getAllPoints():
			yield np.array([x+dx,y+dy])@rotMat
	def generate(self,shift):
		kmToDegree=90/10000
		startLat=self.settings["latitude"]
		startLong=self.settings["longitude"]
		angle=self.settings["angle"]
		size=self.settings["size"]
		
		ret=""
		for x,y in self.getRotatedPoints(angle,shift):
			lat=startLat+y*kmToDegree*size
			lon=startLong+x*kmToDegree*size/np.cos(np.pi/180*lat)
			ret+=str(lon)+","+str(lat)+",0 "
		return ret

if __name__=="__main__":
	dummy={'angle': 0.0, 'latitude': -4.5, 'letterLib': 'figurelib.xml', 'longitude': 0.0, 'size': 1000.0, 'writing': 'Hello World', 'writingsDir': 'writings'}
	k=KML(dummy)
	k.generateAllLetters()

#TODO: Test special char input and weird long-lat input. negative size etc
#TODO: Use OS to make it run on linux, too
#TODO: Add requirements file