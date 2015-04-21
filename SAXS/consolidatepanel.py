from PyQt4 import  QtGui
from PyQt4 import  QtCore
import json,os,collections
import jsonschematreemodel
import calibeditdelegate
import schematools
import Leash
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

import matplotlib.pyplot as plt
import prettyplotlib as ppl
class consolidatepanel(QtGui.QWidget):
    def __init__(self,app):
        super(consolidatepanel,self).__init__( )
        self.app=app
        self.hlayout=QtGui.QHBoxLayout()
        self.setLayout(self.hlayout)
        self.treeview=QtGui.QTreeView()
        self.hlayout.addWidget(self.treeview)
        
        self.model=jsonschematreemodel.jsonschematreemodel( app,
                        schema=json.load(open(os.path.dirname(__file__)
                        +os.sep+'DataConsolidationConf.json'),
                        object_pairs_hook=collections.OrderedDict) 
                                                           )
        self.treeview.setModel(self.model)
        self.treeview.setMinimumWidth(800)
        self.treeview.setMinimumHeight(800)
        self.treeview.setAlternatingRowColors(True)
        self.treeview.setItemDelegateForColumn(1,calibeditdelegate.calibEditDelegate( app ))
        self.reset()
        default= schematools.schematodefault( self.model.schema)
        self.filename=os.path.dirname(__file__)   +os.sep+'consolconftemplate.json'
       
        self.model.loadfile(self.filename)
        self.app.calibeditor.reset()
        self.connect(self.model, QtCore.SIGNAL('dataChanged(QModelIndex,QModelIndex)'),self.model.save)
        self.submitbutton=QtGui.QPushButton("Collect All Data")
        self.submitlayout=QtGui.QVBoxLayout()
        self.hlayout.addLayout(self.submitlayout)
        self.submitlayout.addWidget(   self.submitbutton)
        self.submitlayout.addStretch()
        self.connect(self.submitbutton, QtCore.SIGNAL("clicked()"),self.startmerge)
    def reset(self):
        self.model.invisibleRootItem().setColumnCount(3)
        self.treeview.setColumnWidth(0,320)
        self.treeview.setColumnWidth(1,320)
        self.treeview.expandAll()
    def startmerge(self):
        argu=["mergedata",self.filename]
        result=json.loads(Leash.initcommand(self.app.options,argu,self.app.netconf))
        if result['result']=="Error" or result['result']=="ServerError":
            self.app.errormessage.setWindowTitle("Server Error")
            self.app.errormessage.setMinimumSize(400, 300)
            self.app.errormessage.showMessage(result['data']["Error"])
        else:
            import pandas as pd
            dialog=QtGui.QDialog()
            dialog.setWindowTitle("Merge Sucessfull")
            vlayout=QtGui.QVBoxLayout()
            dialog.setLayout(vlayout)
            figure=plt.figure( )
            ax=figure.add_subplot(111)
            canvas= FigureCanvas(figure)
            navbar=NavigationToolbar(canvas,dialog)
            vlayout.addWidget(canvas)
            vlayout.addWidget(navbar)
            print json.dumps(result["data"]["syncplot"]['Images'])
            img=pd.io.json.read_json(json.dumps(result["data"]["syncplot"]['Images'])).transpose()
            peak= pd.io.json.read_json(json.dumps(result["data"]["syncplot"]['Shutter'])).transpose()
            img.plot(style="ro",ax=ax)  
            peak.plot(style="x",ax=ax)
            canvas.draw()
            dialog.exec_()
            