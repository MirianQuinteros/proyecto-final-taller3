#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui, uic
from PyQt4 import QtCore as qtcore
from model import Experience, ExperienceExecutor, DataReaderAlert, tablemodel
from view import SignalTypeDelegate, OptimoDialog, TestSignalDialog
import threading
import json
import constants
import logging
 
form_class = uic.loadUiType("taller3.ui")[0]
app = QtGui.QApplication(sys.argv)

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Experience):
            return super(MyEncoder, self).default(obj)
        return obj.__dict__

class WorkerStart(qtcore.QThread):
    def __init__(self, executor):
        qtcore.QThread.__init__(self, parent=app)
        self.executor = executor
        self.signal = qtcore.SIGNAL("signal")
        self.signalhab = qtcore.SIGNAL("signalhab")
    
    def run(self):
        logging.debug('Lanzado')
        self.executor.startExecution()
        if self.executor.error:
            self.emit(self.signal, "")
        self.emit(self.signalhab, "")
        logging.debug('Deteniendo')

class WorkerRestart(qtcore.QThread):
    def __init__(self, executor):
        qtcore.QThread.__init__(self, parent=app)
        self.executor = executor
        self.signal = qtcore.SIGNAL("signal")
        self.signalhab = qtcore.SIGNAL("signalhab")
    
    def run(self):
        self.executor.restartExecution()
        if self.executor.error:
            self.emit(self.signal, "")
        self.emit(self.signalhab, "")

class EEControlWindowClass(QtGui.QMainWindow, form_class):
  
  def start(self):
      self.running = True
      self.tableView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
      self.executor = ExperienceExecutor(self.tableView.model().getRows(),
                    self.status, self.label_volts,
                    self.smoke_time, self.waiting_time, self.lcdNumber,
                    self.max_voltage.value(), self.expId, self.readvlbl,
                    self.read_enabled.isChecked())

      startThread = WorkerStart(self.executor)
      self.connect(startThread, startThread.signal, self.showError)
      self.connect(startThread, startThread.signalhab, self.habilitarTabla)
      startThread.start()
      self.start_btn.setEnabled(False)

  def pause(self):

      if self.running :
        self.running = False
        self.executor.pauseExecution()
        self.status.setText('En Pausa')
      else:
        self.running = True
        self.status.setText('Reanudando...')
        restartThread = WorkerRestart(self.executor)
        self.connect(restartThread, restartThread.signal, self.showError)
        self.connect(restartThread, restartThread.signalhab, self.habilitarTabla)
        restartThread.start()
      
      QApplication.processEvents()

  def stop(self):
      self.executor.stopExecution()
      self.status.setText('Detenido')
      self.start_btn.setEnabled(True)
      QApplication.processEvents()

  def newSet(self):
      if self.openFile is not None:
          self.openFile = None
          tmodel = tablemodel.MyTableModel(self, [], constants.columnFields, constants.columnHeaders)
          self.tableView.setModel(tmodel)

  def saveSet(self):
      data = self.tableView.model().getRows()
      s = json.dumps(data, cls=MyEncoder)
      name = QtGui.QFileDialog.getSaveFileName(self, 'Guardar', 'C:\\','JSON (*.json)')
      file = open(name,'w')
      file.write(s)
      file.close()    

  def loadSet(self):
      expList = []
      fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'C:\\', 'JSON (*.json)')
      f = open(fname, 'r')
      with f:
          self.openFile = f     
          data = f.read()
          s = json.loads(data)
          for exp in s:
              expstr = json.dumps(exp)
              e = Experience(jsonObj=expstr)
              expList.append(e)
          tmodel = tablemodel.MyTableModel(self, expList, constants.columnFields, constants.columnHeaders)
          self.tableView.setModel(tmodel)

  def add_experiment(self):
      rowcount = self.tableView.model().rowCount(0)
      self.tableView.model().insertRows(rowcount, 1, QModelIndex())

  def delete_row(self):
      indices = self.tableView.selectionModel().selectedRows()
      for index in sorted(indices):
          self.tableView.model().removeRows(index.row(), 1)

  def showHallarOpt(self):
      text, ok = OptimoDialog().getff()
      if ok:
          print(str(text))

  def testSignal(self):
      ok = TestSignalDialog().getff()
      if ok:
          print('OK')

  def showError(self):
      msg = DataReaderAlert()
      msg.exec_()

  def habilitarTabla(self):
      self.start_btn.setEnabled(True)
      self.tableView.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)

  def __init__(self, parent=None):
      QtGui.QMainWindow.__init__(self, parent)
      self.setupUi(self)
      self.openFile = None

      logging.basicConfig( level=logging.DEBUG, format='[%(levelname)s] - %(threadName)-10s : %(message)s')
      self.data=[]

      tmodel = tablemodel.MyTableModel(self, self.data, constants.columnFields, constants.columnHeaders)
      self.tableView.setItemDelegateForColumn(3,SignalTypeDelegate())

      self.tableView.setModel(tmodel)
      self.tableView.setColumnWidth(0,40)
      self.tableView.setColumnWidth(1,140)
      self.tableView.setColumnWidth(3,80)
      self.tableView.setColumnWidth(6,90)
      self.tableView.setColumnWidth(7,120)
    
      hh = self.tableView.horizontalHeader()
      hh.setStretchLastSection(True)
  
      #connect buttons actions
      self.start_btn.clicked.connect(self.start)
      self.pause_btn.clicked.connect(self.pause)
      self.stop_btn.clicked.connect(self.stop)
      self.add_btn.clicked.connect(self.add_experiment)
      self.delete_btn.clicked.connect(self.delete_row)
      
      self.actionNuevo.triggered.connect(self.newSet)
      self.actionAbrir.triggered.connect(self.loadSet)
      self.actionGuardar.triggered.connect(self.saveSet)
      self.actionHallar_optimo.triggered.connect(self.showHallarOpt)
      self.actionTestSig.triggered.connect(self.testSignal)

      #Timer
      self.lcdNumber.setDigitCount(8) 

if __name__ == '__main__':
      MyWindow = EEControlWindowClass(None)
      MyWindow.show()
      app.exec_()