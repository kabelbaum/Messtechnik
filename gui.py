from tkinter import Frame,Entry,Label,Button
from figures import KML
import argparse
def getFilenameArguments():
	parser=argparse.ArgumentParser()
	parser.add_argument("-l","--letters",help="specify path to letter library",default="figurelib.xml")
	parser.add_argument("-w","--writings",help="specify folder for kml-Files",default="writings")
	args=parser.parse_args()
	return {
        "letterLib": args.letters,
        "writingsDir": args.writings
    } 

class Gui(Frame):
    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.grid()
        self.row=0
        self.createWidgets()
    
    def makeLabeledTB(self,labelText,initVal):
        l=Label(master=self,text=labelText)
        l.grid(row=self.row,column=0)

        tb=Entry(master=self)#TODO: change to slider
        tb.grid(row=self.row,column=1)
        tb.insert(0,str(initVal))
        self.row+=1
        return (l,tb)
    
    def createWidgets(self):
        (self.writeLabel,self.writeTextBox)=self.makeLabeledTB("Writing:","Hello World")
        (self.longLabel,self.longTextBox)=self.makeLabeledTB("Longitude:",0)
        (self.latLabel,self.latTextBox)=self.makeLabeledTB("Latitude:",-4.5)
        (self.sizeLabel,self.sizeTextBox)=self.makeLabeledTB("Size:",1000)
        (self.angleLabel,self.angleTextBox)=self.makeLabeledTB("Angle:",0)

        self.exitButton=Button(master=self,text="exit",command=self.quit)
        self.exitButton.grid(row=self.row,column=0)
        self.launchButton=Button(master=self,text="Go!",command=self.launchKMLGenerator)
        self.launchButton.grid(row=self.row,column=1)

    def readTextBoxes (self):
        return {
            "writing":self.writeTextBox.get(),
            "longitude":float(self.longTextBox.get()),
            "latitude":float(self.latTextBox.get()),
            "size":float(self.sizeTextBox.get()),
            "angle":float(self.angleTextBox.get())
        }
    def launchKMLGenerator(self):
        labels=self.readTextBoxes()
        args=getFilenameArguments()
        settings={**labels,**args} #merge command line args with inputs
        k=KML(settings)
        k.generateAllLetters()
        print("Sucessfully generated KML-File!")

g=Gui()
g.master.title("Change settings!")
g.mainloop()
#TODO: initial values
#TODO: extra information
#TODO: Handle Errors (message box?)