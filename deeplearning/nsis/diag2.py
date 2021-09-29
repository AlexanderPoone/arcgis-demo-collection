# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets, QtTest, Qt
from arcgis.gis import GIS
# import arcpy
from arcgis import geometry, features
from urllib.request import urlopen as u
from urllib.parse import quote

from csv import DictWriter
from json import loads
from glob import glob
import multiprocessing
from re import sub
from collections import Counter

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(990, 643)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/globe.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet("QMainWindow {\n"
"background-image: url(:/icon/bg2.png);\n"
"}\n"
"QWidget {\n"
"font: 8pt \"AvenirNext LT Pro Medium\";\n"
"}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.attrWidget = QtWidgets.QWidget(self.centralwidget)
        self.attrWidget.setStyleSheet("QLabel {\n"
"color: rgb(255, 255, 255);\n"
"}\n"
"QCheckBox { color: rgb(255, 255, 255); }\n")
        self.attrWidget.setObjectName("attrWidget")
        self.attrLayout = QtWidgets.QFormLayout(self.attrWidget)
        self.attrLayout.setObjectName("attrLayout")
        self.label_4 = QtWidgets.QLabel(self.attrWidget)
        self.label_4.setStyleSheet("font: 8pt \"AvenirNext LT Pro Medium\";")
        self.label_4.setObjectName("label_4")
        self.attrLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.sceneComboBox = QtWidgets.QComboBox(self.attrWidget)
        self.sceneComboBox.setObjectName("sceneComboBox")
        self.attrLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.sceneComboBox)
        self.oic_label = QtWidgets.QLabel(self.attrWidget)
        self.oic_label.setStyleSheet("font: 8pt \"AvenirNext LT Pro Medium\";")
        self.oic_label.setObjectName("oic_label")
        self.attrLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.oic_label)
        self.oicComboBox = QtWidgets.QComboBox(self.attrWidget)
        self.oicComboBox.setObjectName("oicComboBox")
        self.attrLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.oicComboBox)
        self.label_5 = QtWidgets.QLabel(self.attrWidget)
        self.label_5.setStyleSheet("font: 8pt \"AvenirNext LT Pro Medium\";")
        self.label_5.setObjectName("label_5")
        self.attrLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.nameHorizontalLayout = QtWidgets.QHBoxLayout()
        self.nameHorizontalLayout.setObjectName("nameHorizontalLayout")
        self.prefix_label = QtWidgets.QLabel(self.attrWidget)
        self.prefix_label.setStyleSheet("font: 8pt \"AvenirNext LT Pro Medium\";")
        self.prefix_label.setText("")
        self.prefix_label.setObjectName("prefix_label")
        self.nameHorizontalLayout.addWidget(self.prefix_label)
        self.nameFeatureLayer = QtWidgets.QLineEdit(self.attrWidget)
        self.nameFeatureLayer.setObjectName("nameFeatureLayer")
        self.nameHorizontalLayout.addWidget(self.nameFeatureLayer)
        self.attrLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.nameHorizontalLayout)
        self.label_2 = QtWidgets.QLabel(self.attrWidget)
        self.label_2.setStyleSheet("font: 8pt \"AvenirNext LT Pro Medium\";")
        self.label_2.setObjectName("label_2")
        self.attrLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.imgRootFolder = QtWidgets.QLineEdit(self.attrWidget)
        self.imgRootFolder.setObjectName("imgRootFolder")
        self.horizontalLayout.addWidget(self.imgRootFolder)
        self.toolButton = QtWidgets.QToolButton(self.attrWidget)
        self.toolButton.setStyleSheet("font: 8pt \"AvenirNext LT Pro Medium\";")
        self.toolButton.setObjectName("toolButton")
        self.horizontalLayout.addWidget(self.toolButton)
        self.attrLayout.setLayout(3, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)

        self.streetEdit = QtWidgets.QLabel(self.attrWidget)
        self.streetEdit.setStyleSheet("font: 8pt \"AvenirNext LT Pro Medium\";")
        self.streetEdit.setObjectName("streetEdit")
        self.attrLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.streetEdit)
        self.streetEditEdit = QtWidgets.QLineEdit(self.attrWidget)
        self.streetEditEdit.setObjectName("nameFeatureLayer")
        self.attrLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.streetEditEdit)

        self.skipFillingDeadholeCheckbox = QtWidgets.QCheckBox(self.attrWidget)
        self.skipFillingDeadholeCheckbox.setObjectName("skipFillingDeadholeCheckbox")
        self.attrLayout.setWidget(5, QtWidgets.QFormLayout.SpanningRole, self.skipFillingDeadholeCheckbox)

        self.disableFTPCheckbox = QtWidgets.QCheckBox(self.attrWidget)
        self.disableFTPCheckbox.setObjectName("disableFTPCheckbox")
        self.attrLayout.setWidget(6, QtWidgets.QFormLayout.SpanningRole, self.disableFTPCheckbox)

        self.labelUrl = QtWidgets.QLabel(self.attrWidget)
        self.labelUrl.setStyleSheet("font: 8pt \"AvenirNext LT Pro Medium\";")
        self.labelUrl.setObjectName("labelUrl")
        self.attrLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.labelUrl)
        self.labelUrlEdit = QtWidgets.QLineEdit(self.attrWidget)
        self.labelUrlEdit.setObjectName("nameFeatureLayer")
        self.attrLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.labelUrlEdit)

        self.disableFTPUpdateOICMenuCheckbox = QtWidgets.QCheckBox(self.attrWidget)
        self.disableFTPUpdateOICMenuCheckbox.setObjectName("disableFTPUpdateOICMenuCheckbox")
        self.attrLayout.setWidget(8, QtWidgets.QFormLayout.SpanningRole, self.disableFTPUpdateOICMenuCheckbox)

        self.labelUsr = QtWidgets.QLabel(self.attrWidget)
        self.labelUsr.setStyleSheet("font: 8pt \"AvenirNext LT Pro Medium\";")
        self.labelUsr.setObjectName("labelUsr")
        self.attrLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole, self.labelUsr)
        self.labelUsrEdit = QtWidgets.QLineEdit(self.attrWidget)
        self.labelUsrEdit.setObjectName("nameFeatureLayer")
        self.attrLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole, self.labelUsrEdit)

        self.labelFtpPassword = QtWidgets.QLabel(self.attrWidget)
        self.labelFtpPassword.setStyleSheet("font: 8pt \"AvenirNext LT Pro Medium\";")
        self.labelFtpPassword.setObjectName("labelFtpPassword")
        self.attrLayout.setWidget(10, QtWidgets.QFormLayout.LabelRole, self.labelFtpPassword)
        self.labelFtpPasswordEdit = QtWidgets.QLineEdit(self.attrWidget)
        self.labelFtpPasswordEdit.setObjectName("nameFeatureLayer")
        self.labelFtpPasswordEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.attrLayout.setWidget(10, QtWidgets.QFormLayout.FieldRole, self.labelFtpPasswordEdit)

        self.verticalLayout.addWidget(self.attrWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btnAnnotateOrLocate = QtWidgets.QPushButton(self.centralwidget)
        self.btnAnnotateOrLocate.setEnabled(False)
        self.btnAnnotateOrLocate.setStyleSheet("font: 8pt \"AvenirNext LT Pro Medium\";")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon/execute.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnAnnotateOrLocate.setIcon(icon1)
        self.btnAnnotateOrLocate.setObjectName("btnAnnotateOrLocate")
        self.horizontalLayout_2.addWidget(self.btnAnnotateOrLocate)
        self.openContainerFolderBtn = QtWidgets.QPushButton(self.centralwidget)
        self.openContainerFolderBtn.setStyleSheet("font: 8pt \"AvenirNext LT Pro Medium\";")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icon/open_folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.openContainerFolderBtn.setIcon(icon2)
        self.openContainerFolderBtn.setObjectName("openContainerFolderBtn")
        self.openContainerFolderBtn.setEnabled(False)
        self.horizontalLayout_2.addWidget(self.openContainerFolderBtn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setStyleSheet("QWidget {\n"
"background-color: rgba(255, 255, 255, 125);\n"
"}\n"
"QLabel {\n"
"background-color: rgba(255, 255, 255, 0);\n"
"}")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 512, 425))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.horizontalLayout_5.addLayout(self.formLayout_2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 1, 1, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setStyleSheet("QTabWidget::pane {\n"
"    background: rgba(255, 255, 255, 180);\n"
"    border:0;\n"
"}")
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tab1gridLayout = QtWidgets.QGridLayout(self.tab)
        self.tab1gridLayout.setContentsMargins(0, 0, 0, 0)
        self.tab1gridLayout.setObjectName("tab1gridLayout")
        self.listWidget = QtWidgets.QListWidget(self.tab)
        self.listWidget.setStyleSheet("background-color: rgba(255, 255, 255, 150);")
        self.listWidget.setIconSize(QtCore.QSize(200, 100))
        self.listWidget.setSelectionRectVisible(False)
        self.listWidget.setObjectName("listWidget")
        item = QtWidgets.QListWidgetItem()
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icon/camera.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon3)
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icon/blurs.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon4)
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        iconSW = QtGui.QIcon()
        iconSW.addPixmap(QtGui.QPixmap(":/icon/from_street_view.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(iconSW)
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        iconOic = QtGui.QIcon()
        iconOic.addPixmap(QtGui.QPixmap(":/icon/oriented-imagery-small.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(iconOic)
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        iconRoad = QtGui.QIcon()
        iconRoad.addPixmap(QtGui.QPixmap(":/icon/road-condition.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(iconRoad)
        self.listWidget.addItem(item)
        self.tab1gridLayout.addWidget(self.listWidget, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab, icon, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tab2gridLayout = QtWidgets.QGridLayout(self.tab_2)
        self.tab2gridLayout.setObjectName("tab2gridLayout")
        self.tab2gridLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.headingAutoAnnotation = QtWidgets.QLabel(self.tab_2)
        self.headingAutoAnnotation.setStyleSheet("")
        self.headingAutoAnnotation.setObjectName("headingAutoAnnotation")
        self.headingAutoAnnotation.setMargin(8)
        self.headingAutoAnnotation.setStyleSheet("QMainWindow {\n"
"background-image: url(:/icon/bg2.png);\n"
"}\n"
"QWidget {\n"
"font: 9pt \"AvenirNext LT Pro Medium\";\n"
"}")
        self.verticalLayout_2.addWidget(self.headingAutoAnnotation)
        self.listWidgetAutoAnnotation = QtWidgets.QListWidget(self.tab_2)
        self.listWidgetAutoAnnotation.setStyleSheet("background-color: rgba(255, 255, 255, 150);")
        self.listWidgetAutoAnnotation.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.listWidgetAutoAnnotation.setIconSize(QtCore.QSize(200, 100))
        self.listWidgetAutoAnnotation.setObjectName("listWidgetAutoAnnotation")
        item = QtWidgets.QListWidgetItem()
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icon/overhanging_signs.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon5)
        self.listWidgetAutoAnnotation.addItem(item)
        item = QtWidgets.QListWidgetItem()
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/icon/sewer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon6)
        self.listWidgetAutoAnnotation.addItem(item)
        item = QtWidgets.QListWidgetItem()
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/icon/firehydrant.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon7)
        self.listWidgetAutoAnnotation.addItem(item)
        item = QtWidgets.QListWidgetItem()
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/icon/cones.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon8)
        self.listWidgetAutoAnnotation.addItem(item)
        item = QtWidgets.QListWidgetItem()
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/icon/bin.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon9)
        self.listWidgetAutoAnnotation.addItem(item)
        item = QtWidgets.QListWidgetItem()
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/icon/trafficlight.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon10)
        self.listWidgetAutoAnnotation.addItem(item)
        item = QtWidgets.QListWidgetItem()
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/icon/parkingmeter.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon11)
        self.listWidgetAutoAnnotation.addItem(item)
        self.verticalLayout_2.addWidget(self.listWidgetAutoAnnotation)
        self.tab2gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(":/icon/autoannotation.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.tab_2, icon12, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 2, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 990, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        self.statusbar.showMessage("Build 2020.12.17")
        self.statusbar.setStyleSheet("color: rgb(255, 255, 255);")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Preprocessing Utility for oriented images"))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        item = self.listWidget.item(0)
        item.setText(_translate("MainWindow", "Generate EXIF and coordinates.txt for images (do first)"))
        item = self.listWidget.item(1)
        item.setText(_translate("MainWindow", "Blur faces + blur licence plates (Hong Kong) + fill dead holes"))
        item = self.listWidget.item(2)
        item.setText(_translate("MainWindow", "Adapt an entire street from Street View to OIC (Copyright Google, do not redistribute)"))
        item = self.listWidget.item(3)
        item.setText(_translate("MainWindow", "Create Oriented Imagery Catalog from server"))
        item = self.listWidget.item(4)
        item.setText(_translate("MainWindow", "Inspect road condition (experimental)"))

        self.listWidget.setSortingEnabled(__sortingEnabled)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "General"))
        self.headingAutoAnnotation.setText(_translate("MainWindow", "Select object(s) to be detected below (can choose multiple):"))
        __sortingEnabled = self.listWidgetAutoAnnotation.isSortingEnabled()
        self.listWidgetAutoAnnotation.setSortingEnabled(False)
        item = self.listWidgetAutoAnnotation.item(0)
        item.setText(_translate("MainWindow", "Overhanging signs (experimental)"))
        item = self.listWidgetAutoAnnotation.item(1)
        item.setText(_translate("MainWindow", "Manholes (Hong Kong)"))
        item = self.listWidgetAutoAnnotation.item(2)
        item.setText(_translate("MainWindow", "Fire hydrants"))
        item = self.listWidgetAutoAnnotation.item(3)
        item.setText(_translate("MainWindow", "Traffic cones"))
        item = self.listWidgetAutoAnnotation.item(4)
        item.setText(_translate("MainWindow", "Orange rubbbish bins"))
        item = self.listWidgetAutoAnnotation.item(5)
        item.setText(_translate("MainWindow", "Traffic lights"))
        item = self.listWidgetAutoAnnotation.item(6)
        item.setText(_translate("MainWindow", "Parking meters"))
        self.listWidgetAutoAnnotation.setSortingEnabled(__sortingEnabled)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Auto-annotation (experimental)"))

        self.label_4.setText(_translate("MainWindow", "Select scene from ArcGIS Online:"))
        self.oic_label.setText(_translate("MainWindow", "Select Oriented Imagery Catalog:"))
        self.label_5.setText(_translate("MainWindow", "Name of the new Feature Layer:"))
        self.streetEdit.setText(_translate("MainWindow", "Street name:"))
        self.labelUrl.setText(_translate("MainWindow", "URL to the folder online:"))
        self.label_2.setText(_translate("MainWindow", "Image root folder:"))
        self.toolButton.setText(_translate("MainWindow", "..."))
        self.btnAnnotateOrLocate.setText(_translate("MainWindow", " Execute"))
        self.openContainerFolderBtn.setText(_translate("MainWindow", " Open containing folder"))
        self.labelUsr.setText(_translate("MainWindow", "FTP Server user name:"))
        self.labelFtpPassword.setText(_translate("MainWindow", "FTP Server password:"))
        self.skipFillingDeadholeCheckbox.setText(_translate("MainWindow", "Do not fill dead holes"))
        self.disableFTPCheckbox.setText(_translate("MainWindow", "Do not use FTP, I wish to move the images to the server myself"))
        self.disableFTPUpdateOICMenuCheckbox.setText(_translate("MainWindow", "Do not use FTP to update web app's OIC Menu"))
import preprocess_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(645, 291)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/globe.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setStyleSheet("#Dialog { background-image: url(:/icon/bg.png); }\n"
"QLabel { color: rgb(255, 255, 255); }\n")
        self.horizontalLayout = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setFamily("AvenirNext LT Pro Medium")
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.label)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_portalUrl = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setFamily("AvenirNext LT Pro Medium")
        self.label_portalUrl.setFont(font)
        self.label_portalUrl.setObjectName("label_portalUrl")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_portalUrl)
        self.label_3 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setFamily("AvenirNext LT Pro Medium")
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setFamily("AvenirNext LT Pro Medium")
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.portalUrlEdit = QtWidgets.QLineEdit(Dialog)
        self.portalUrlEdit.setStyleSheet("color: rgb(0,0,0);")
        self.portalUrlEdit.setObjectName("portalUrlEdit")
        self.portalUrlEdit.setText('https://www.arcgis.com')
        font = QtGui.QFont()
        font.setFamily("AvenirNext LT Pro Medium")
        self.portalUrlEdit.setFont(font)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.portalUrlEdit)
        self.usrnameEdit = QtWidgets.QLineEdit(Dialog)
        self.usrnameEdit.setStyleSheet("color: rgb(0,0,0);")
        self.usrnameEdit.setObjectName("usrnameEdit")
        self.usrnameEdit.setFocus()
        font = QtGui.QFont()
        font.setFamily("AvenirNext LT Pro Medium")
        self.usrnameEdit.setFont(font)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.usrnameEdit)
        self.pwdEdit = QtWidgets.QLineEdit(Dialog)
        self.pwdEdit.setStyleSheet("color: rgb(0,0,0);")
        self.pwdEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pwdEdit.setObjectName("pwdEdit")
        font = QtGui.QFont()
        font.setFamily("AvenirNext LT Pro Medium")
        self.pwdEdit.setFont(font)

        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.pwdEdit)
        self.horizontalLayout.addLayout(self.formLayout)
        self.dialogStandardButtonBox = QtWidgets.QDialogButtonBox(Dialog)
        font = QtGui.QFont()
        font.setFamily("AvenirNext LT Pro Medium")
        font.setPointSize(8)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(7)
        self.dialogStandardButtonBox.setFont(font)
        self.dialogStandardButtonBox.setStyleSheet("font: 57 8pt \"AvenirNext LT Pro Medium\";")
        self.dialogStandardButtonBox.setOrientation(QtCore.Qt.Vertical)
        self.dialogStandardButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.dialogStandardButtonBox.setObjectName("dialogStandardButtonBox")
        self.horizontalLayout.addWidget(self.dialogStandardButtonBox)

        self.retranslateUi(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Preprocessing Utility for oriented images"))
        self.label.setText(_translate("Dialog", "Log in to ArcGIS Online or Portal"))
        self.label_portalUrl.setText(_translate("Dialog", "Portal URL:"))
        self.label_2.setText(_translate("Dialog", "User name:"))
        self.label_3.setText(_translate("Dialog", "Password:"))

class Form(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.isExecuting = False

        self.threadpool = QtCore.QThreadPool()

        self.ui.toolButton.clicked.connect(self.browseDir)
        self.ui.tabWidget.currentChanged.connect(self.operationChanged)
        self.ui.listWidget.currentRowChanged.connect(self.operationChanged)
        self.ui.listWidgetAutoAnnotation.currentRowChanged.connect(self.operationChanged)
        self.ui.nameFeatureLayer.textChanged.connect(self.validate)
        self.ui.imgRootFolder.textChanged.connect(self.validate)
        self.ui.imgRootFolder.textChanged.connect(self.validate)
        self.ui.streetEditEdit.textChanged.connect(self.validate)
        self.ui.streetEditEdit.textChanged.connect(self.changeCompleter)
        self.ui.labelUrlEdit.textChanged.connect(self.validate)
        self.ui.labelUsrEdit.textChanged.connect(self.validate)
        self.ui.labelFtpPasswordEdit.textChanged.connect(self.validate)
        self.ui.btnAnnotateOrLocate.clicked.connect(self.execute)
        self.ui.openContainerFolderBtn.clicked.connect(self.openContainerFolder)
        self.ui.oicComboBox.currentTextChanged.connect(self.prefixName)
        self.ui.disableFTPCheckbox.stateChanged.connect(self.validate)
        self.ui.disableFTPCheckbox.stateChanged.connect(self.ftpOnOff)
        self.ui.disableFTPUpdateOICMenuCheckbox.stateChanged.connect(self.validate)
        self.ui.disableFTPUpdateOICMenuCheckbox.stateChanged.connect(self.ftpOicMenuOnOff)

        self.signal = Signals()
        self.signal.threadReturnSig.connect(self.threadReturn)
        self.signal.updateProgressExifSig.connect(self.updateProgressExif)
        self.signal.updateProgressPreprocessSig.connect(self.updateProgressPreprocess)
        self.signal.updateProgressDetectSig.connect(self.updateProgressDetect)
        self.signal.downloadProgressSig.connect(self.downloadProgress)
        self.signal.uploadProgressSig.connect(self.uploadProgress)
        
        QtCore.QMetaObject.connectSlotsByName(self)

        self.ui.listWidget.setCurrentRow(0)

    def changeCompleter(self):
        try:
            keyword = quote(self.ui.streetEditEdit.text())

            if keyword != '':
                v=u('https://api.hkmapservice.gov.hk/ags/gc/ib1000/transportation/streetcentrelines/suggest?f=json&maxSuggestions=10&text={0}&key=584b2fa686f14ba283874318b3b8d6b0'.format(keyword))
                h=v.read().decode('utf-8')
                l=loads(h)

                completer = QtWidgets.QCompleter([z['text'] for z in l['suggestions']], self)
                completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
                self.ui.streetEditEdit.setCompleter(completer)
        except:
            pass

    def prefixName(self, name):
        self.ui.prefix_label.setText(name+'_')
        # try:
        #     oldName = self.ui.nameFeatureLayer.text()
        #     self.ui.nameFeatureLayer.setText(oldName[oldName.index('|')+1:])
        # except:
        #     pass
        # self.ui.nameFeatureLayer.setText(name + '|' + self.ui.nameFeatureLayer.text())

    def ftpOnOff(self):
        if self.ui.disableFTPCheckbox.isChecked():
            self.ui.labelUrl.hide()
            self.ui.labelUsr.hide()
            self.ui.labelFtpPassword.hide()
            self.ui.labelUrlEdit.hide()
            self.ui.labelUsrEdit.hide()
            self.ui.labelFtpPasswordEdit.hide()
        else:
            self.ui.labelUrl.show()
            self.ui.labelUsr.show()
            self.ui.labelFtpPassword.show()
            self.ui.labelUrlEdit.show()
            self.ui.labelUsrEdit.show()
            self.ui.labelFtpPasswordEdit.show()

    def ftpOicMenuOnOff(self):
        if self.ui.disableFTPUpdateOICMenuCheckbox.isChecked():
            self.ui.labelUsr.hide()
            self.ui.labelFtpPassword.hide()
            self.ui.labelUsrEdit.hide()
            self.ui.labelFtpPasswordEdit.hide()
        else:
            self.ui.labelUsr.show()
            self.ui.labelFtpPassword.show()
            self.ui.labelUsrEdit.show()
            self.ui.labelFtpPasswordEdit.show()        

    def browseDir(self):
        print(self)
        filed=QtWidgets.QFileDialog()
        filed.setFileMode(QtWidgets.QFileDialog.Directory)
        if filed.exec():
            fileName = filed.selectedFiles()           #QtCore.QStringList
            self.ui.imgRootFolder.setText(fileName[0])

    def operationChanged(self):
        _translate = QtCore.QCoreApplication.translate
        if self.ui.tabWidget.currentIndex() == 0 and self.ui.listWidget.currentRow() in (0,1,2,3):
            self.ui.label_4.hide()
            self.ui.label_5.hide()
            self.ui.sceneComboBox.hide()
            self.ui.oic_label.hide()
            self.ui.oicComboBox.hide()
            self.ui.nameFeatureLayer.hide()
            self.ui.prefix_label.hide()
            self.ui.streetEdit.hide()
            self.ui.streetEditEdit.hide()
            self.ui.labelUsr.hide()
            self.ui.labelUsrEdit.hide()
            self.ui.labelFtpPassword.hide()
            self.ui.labelFtpPasswordEdit.hide()
            self.ui.disableFTPCheckbox.hide()
            self.ui.disableFTPUpdateOICMenuCheckbox.hide()
            self.ui.skipFillingDeadholeCheckbox.hide()
            if self.ui.listWidget.currentRow() == 1:
                self.ui.skipFillingDeadholeCheckbox.show()
            elif self.ui.listWidget.currentRow() in (2,3):
                self.ui.labelUrl.show()
                self.ui.labelUrlEdit.show()
                if self.ui.listWidget.currentRow() == 2:
                    self.ui.streetEdit.show()
                    self.ui.streetEditEdit.show()
                #     self.ui.labelUsr.show()
                #     self.ui.labelUsrEdit.show()
                #     self.ui.labelFtpPassword.show()
                #     self.ui.labelFtpPasswordEdit.show()
                #     self.ui.disableFTPCheckbox.show()
                #     self.ftpOnOff()
                #     self.ui.labelUrl.setText(_translate("MainWindow", "FTP URL of the server:"))
                # else:
                #     self.ui.labelUrl.setText(_translate("MainWindow", "URL to the folder online:"))
            else:
                self.ui.labelUrl.hide()
                self.ui.labelUrlEdit.hide()
            if self.ui.listWidget.currentRow() in (1,2,3):
                # self.ui.streetEdit.show()
                # self.ui.streetEditEdit.show()
                self.ui.labelUsr.show()
                self.ui.labelUsrEdit.show()
                self.ui.labelFtpPassword.show()
                self.ui.labelFtpPasswordEdit.show()
                if self.ui.listWidget.currentRow() in (1,2):
                    self.ui.disableFTPUpdateOICMenuCheckbox.hide()
                    self.ui.disableFTPCheckbox.show()
                    self.ftpOnOff()
                    self.ui.labelUrl.setText(_translate("MainWindow", "FTP URL of the server:"))
                    # self.ui.attrLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, None)
                    # self.ui.attrLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, None)
                    # self.ui.attrLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, None)
                    # self.ui.attrLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, None)
                    # self.ui.attrLayout.setWidget(5, QtWidgets.QFormLayout.SpanningRole, self.ui.disableFTPCheckbox)
                    # self.ui.attrLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.ui.labelUrl)
                    # self.ui.attrLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.ui.labelUrlEdit)
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap(":/icon/open_folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    self.ui.openContainerFolderBtn.setIcon(icon)
                    self.ui.openContainerFolderBtn.setText(_translate("MainWindow", " Open containing folder"))
                else:
                    self.ui.disableFTPCheckbox.hide()
                    self.ui.disableFTPUpdateOICMenuCheckbox.show()
                    self.ftpOicMenuOnOff()
                    self.ui.labelUrl.setText(_translate("MainWindow", "URL to the folder online:"))
                    # self.ui.attrLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, None)
                    # self.ui.attrLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, None)
                    # self.ui.attrLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, None)
                    # self.ui.attrLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, None)
                    # self.ui.attrLayout.setWidget(6, QtWidgets.QFormLayout.SpanningRole, self.ui.disableFTPCheckbox)
                    # self.ui.attrLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.ui.labelUrl)
                    # self.ui.attrLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.ui.labelUrlEdit)
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap(":/icon/globe.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    self.ui.openContainerFolderBtn.setIcon(icon)
                    self.ui.openContainerFolderBtn.setText(_translate("MainWindow", " Open \"My Contents\" on ArcGIS Portal"))
            else:
                self.ui.labelUrl.setText(_translate("MainWindow", "URL to the folder online:"))
            self.validate()
        else:
            self.ui.label_4.show()
            self.ui.label_5.show()
            self.ui.sceneComboBox.show()
            self.ui.oic_label.show()
            self.ui.oicComboBox.show()
            self.ui.nameFeatureLayer.show()
            self.ui.prefix_label.show()
            self.ui.labelUrl.hide()
            self.ui.labelUrlEdit.hide()
            self.ui.streetEdit.hide()
            self.ui.streetEditEdit.hide()
            self.ui.labelUsr.hide()
            self.ui.labelUsrEdit.hide()
            self.ui.labelFtpPassword.hide()
            self.ui.labelFtpPasswordEdit.hide()
            self.ui.disableFTPCheckbox.hide()
            self.ui.disableFTPUpdateOICMenuCheckbox.hide()
            self.ui.skipFillingDeadholeCheckbox.hide()
            # print(self.ui.listWidgetAutoAnnotation.currentRow())
            if self.ui.listWidgetAutoAnnotation.currentRow() >= 0 and not self.ui.listWidgetAutoAnnotation.item(self.ui.listWidgetAutoAnnotation.currentRow()).isSelected():
                self.ui.nameFeatureLayer.setText(self.ui.listWidgetAutoAnnotation.item(self.ui.listWidgetAutoAnnotation.currentRow()).text().replace('Annotate and locate ',''))
            
            if self.ui.listWidgetAutoAnnotation.currentRow() == 0 and not self.ui.listWidgetAutoAnnotation.item(0).isSelected():
                self.ui.listWidgetAutoAnnotation.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
                self.ui.listWidgetAutoAnnotation.setCurrentRow(0)
                self.ui.listWidgetAutoAnnotation.item(0).setSelected(True)
                self.ui.listWidgetAutoAnnotation.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
            elif self.ui.listWidgetAutoAnnotation.currentRow() == 1 and not self.ui.listWidgetAutoAnnotation.item(1).isSelected():
                self.ui.listWidgetAutoAnnotation.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
                self.ui.listWidgetAutoAnnotation.setCurrentRow(1)
                self.ui.listWidgetAutoAnnotation.item(1).setSelected(True)
                self.ui.listWidgetAutoAnnotation.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)


            self.validate()
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/icon/globe.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.ui.openContainerFolderBtn.setIcon(icon)
            self.ui.openContainerFolderBtn.setText(_translate("MainWindow", " Open \"My Contents\" on ArcGIS Portal"))

    def validate(self):
        if self.isExecuting:
            self.ui.btnAnnotateOrLocate.setEnabled(False)
        elif self.ui.tabWidget.currentIndex() == 0 and self.ui.listWidget.currentRow() in (0,1,2,3): 
            if self.ui.listWidget.currentRow() in (0,1):
                if self.ui.imgRootFolder.text() != '':
                    self.ui.btnAnnotateOrLocate.setEnabled(True)
                else:
                    self.ui.btnAnnotateOrLocate.setEnabled(False)
            elif self.ui.listWidget.currentRow() == 2:
                if self.ui.imgRootFolder.text() != '' and self.ui.streetEditEdit.text() != '' and (self.ui.disableFTPCheckbox.isChecked() or (self.ui.labelUrlEdit.text() != '' and self.ui.labelUsrEdit.text() != '' and self.ui.labelFtpPasswordEdit.text() != '')):
                    self.ui.btnAnnotateOrLocate.setEnabled(True)
                else:
                    self.ui.btnAnnotateOrLocate.setEnabled(False)
            elif self.ui.listWidget.currentRow() == 3:
                if self.ui.imgRootFolder.text() != '' and self.ui.labelUrlEdit.text() != '':
                    self.ui.btnAnnotateOrLocate.setEnabled(True)
                else:
                    self.ui.btnAnnotateOrLocate.setEnabled(False) 
        elif self.ui.nameFeatureLayer.text() != '' and self.ui.imgRootFolder.text() != '':
            self.ui.btnAnnotateOrLocate.setEnabled(True)
        else:
            self.ui.btnAnnotateOrLocate.setEnabled(False)

    def execute(self):
        imgRoot = self.ui.imgRootFolder.text()
        if imgRoot[-1] in ('/','\\'):
            imgRoot = imgRoot[:-1]

        if self.ui.tabWidget.currentIndex() == 0:
            if self.ui.listWidget.currentRow() != 2:
                if self.ui.listWidget.currentRow() == 0:
                    if len(glob(imgRoot + '/*/Imagery/Camera Data/*/*.csv')) == 0:
                        msg = QtWidgets.QMessageBox()
                        msg.setIcon(QtWidgets.QMessageBox.Critical)

                        msg.setText(imgRoot + '/*/Imagery/Camera Data/*/*.csv are not found. Please make sure that the path is correct.')
                        # msg.setInformativeText("This is additional information")
                        msg.setWindowTitle("Error")
                        # msg.setDetailedText("The details are as follows:")
                        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                        msg.exec()
                        return
                if len(glob(imgRoot +'/*/Imagery/JPG/*/*/*.jpg')) == 0:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Critical)

                    msg.setText(imgRoot + '/*/Imagery/JPG/*/*/*.jpg are not found. Please make sure that the path is correct.')
                    # msg.setInformativeText("This is additional information")
                    msg.setWindowTitle("Error")
                    # msg.setDetailedText("The details are as follows:")
                    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                    msg.exec()
                    return
        elif len(glob(imgRoot +'/*/Imagery/JPG/*/*/*.jpg')) == 0:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)

            msg.setText(imgRoot + '/*/Imagery/JPG/*/*/*.jpg are not found. Please make sure that the path is correct.')
            # msg.setInformativeText("This is additional information")
            msg.setWindowTitle("Error")
            # msg.setDetailedText("The details are as follows:")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()
            return     

        self.isExecuting = True
        self.ui.sceneComboBox.setEnabled(False)
        self.ui.oicComboBox.setEnabled(False)
        self.ui.nameFeatureLayer.setEnabled(False)
        self.ui.imgRootFolder.setEnabled(False)
        self.ui.streetEditEdit.setEnabled(False)
        self.ui.labelUrlEdit.setEnabled(False)
        self.ui.labelUsrEdit.setEnabled(False)
        self.ui.labelFtpPasswordEdit.setEnabled(False)
        self.ui.disableFTPCheckbox.setEnabled(False)
        self.ui.disableFTPUpdateOICMenuCheckbox.setEnabled(False)
        # self.ui.btnAnnotateOrLocate.setEnabled(False)

        self.ui.btnAnnotateOrLocate.setText(' Pause')
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/icon/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.btnAnnotateOrLocate.setIcon(icon9)

        self.ui.toolButton.setEnabled(False)
        self.ui.openContainerFolderBtn.setEnabled(True)

        if self.ui.tabWidget.currentIndex() == 0:
            if self.ui.listWidget.currentRow() == 0:
                self.panoramaTagExif(imgRoot)
            elif self.ui.listWidget.currentRow() == 1:
                self.preprocess_unified(imgRoot)
            elif self.ui.listWidget.currentRow() == 2:
                if self.ui.disableFTPCheckbox.isChecked():
                    self.adapt_sw(imgRoot,self.ui.streetEditEdit.text())
                else:
                    self.adapt_sw(imgRoot,self.ui.streetEditEdit.text(),self.ui.labelUrlEdit.text(),self.ui.labelUsrEdit.text(),self.ui.labelFtpPasswordEdit.text())
            elif self.ui.listWidget.currentRow() == 3:
                if self.ui.disableFTPCheckbox.isChecked():
                    self.create_oic(self.ui.labelUrlEdit.text() if self.ui.labelUrlEdit.text().startswith('http') else 'https://' + self.ui.labelUrlEdit.text(),imgRoot)
                else:
                    self.create_oic(self.ui.labelUrlEdit.text() if self.ui.labelUrlEdit.text().startswith('http') else 'https://' + self.ui.labelUrlEdit.text(),imgRoot,self.ui.labelUrlEdit.text(),self.ui.labelUsrEdit.text(),self.ui.labelFtpPasswordEdit.text())
            elif self.ui.listWidget.currentRow() == 4:
                self.outline(imgRoot)
        else:
            # TBD
            if self.ui.listWidgetAutoAnnotation.currentRow() == 0:
                self.detectOverhangingSigns(imgRoot) #self.autoAnnotate('cone',imgRoot)
            elif self.ui.listWidgetAutoAnnotation.currentRow() == 1:
                self.autoAnnotate('sewer',imgRoot)
            elif self.ui.listWidgetAutoAnnotation.currentRow() == 2:
                self.autoAnnotate('fire_hydrant',imgRoot)
            elif self.ui.listWidgetAutoAnnotation.currentRow() == 3:
                self.autoAnnotate('cone',imgRoot)
            elif self.ui.listWidgetAutoAnnotation.currentRow() == 4:
                self.autoAnnotate('orange_bin',imgRoot)
            elif self.ui.listWidgetAutoAnnotation.currentRow() == 5:
                self.autoAnnotate('traffic_light',imgRoot)
            elif self.ui.listWidgetAutoAnnotation.currentRow() == 6:
                self.autoAnnotate('parking_meter',imgRoot)

    def openContainerFolder(self):
        if self.ui.tabWidget.currentIndex() == 0 and self.ui.listWidget.currentRow() in (0,1,2):
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(form.ui.imgRootFolder.text()))
        else:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(portalUrl+ '/home/content.html'))

    def panoramaTagExif(self, imgRoot):
        self.ui.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.ui.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 490, 480))
        self.ui.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.ui.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.ui.scrollAreaWidgetContents)
        self.ui.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.ui.formLayout_2 = QtWidgets.QFormLayout()
        self.ui.formLayout_2.setObjectName("formLayout_2")
        
        self.ui.horizontalLayout_5.addLayout(self.ui.formLayout_2)
        self.ui.scrollArea.setWidget(self.ui.scrollAreaWidgetContents)
        
        worker = PanoramaTagExifWorker(imgRoot)
        self.threadpool.start(worker)
        print('ThreadPool')

    def preprocess_unified(self, imgRoot):
        self.ui.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.ui.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 490, 480))
        self.ui.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.ui.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.ui.scrollAreaWidgetContents)
        self.ui.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.ui.formLayout_2 = QtWidgets.QFormLayout()
        self.ui.formLayout_2.setObjectName("formLayout_2")
        
        self.ui.horizontalLayout_5.addLayout(self.ui.formLayout_2)
        self.ui.scrollArea.setWidget(self.ui.scrollAreaWidgetContents)

        self.ui.label_6 = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.label_6.setObjectName("label_6")
        self.ui.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.ui.label_6)
        self.ui.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.ui.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.ui.progressBar = QtWidgets.QProgressBar(self.ui.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui.progressBar.sizePolicy().hasHeightForWidth())
        self.ui.progressBar.setSizePolicy(sizePolicy)
        self.ui.progressBar.setObjectName("progressBar")
        self.ui.horizontalLayout_3.addWidget(self.ui.progressBar)
        self.ui.label = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.label.setObjectName("label")
        self.ui.horizontalLayout_3.addWidget(self.ui.label)
        self.ui.formLayout_2.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.ui.horizontalLayout_3)
        
        self.ui.label_8 = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.label_8.setObjectName("label_8")
        self.ui.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.ui.label_8)
        self.ui.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.ui.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.ui.progressBar_2 = QtWidgets.QProgressBar(self.ui.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui.progressBar_2.sizePolicy().hasHeightForWidth())
        self.ui.progressBar_2.setSizePolicy(sizePolicy)
        self.ui.progressBar_2.setObjectName("progressBar_2")
        self.ui.horizontalLayout_4.addWidget(self.ui.progressBar_2)
        self.ui.label_7 = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.label_7.setObjectName("label_7")
        self.ui.horizontalLayout_4.addWidget(self.ui.label_7)
        self.ui.formLayout_2.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.ui.horizontalLayout_4)
        
        self.ui.label_9 = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.label_9.setObjectName("label_9")
        self.ui.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.ui.label_9)
        self.ui.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.ui.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.ui.progressBar_3 = QtWidgets.QProgressBar(self.ui.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui.progressBar_3.sizePolicy().hasHeightForWidth())
        self.ui.progressBar_3.setSizePolicy(sizePolicy)
        self.ui.progressBar_3.setObjectName("progressBar_3")
        self.ui.horizontalLayout_5.addWidget(self.ui.progressBar_3)
        self.ui.label_10 = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.label_10.setObjectName("label_10")
        self.ui.horizontalLayout_5.addWidget(self.ui.label_10)
        self.ui.formLayout_2.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.ui.horizontalLayout_5)


        worker = PreprocessWorker(imgRoot, self.ui.skipFillingDeadholeCheckbox.isChecked())
        self.threadpool.start(worker)

    def adapt_sw(self, imgRoot, streetName, ftpUrl=None, ftpUsr=None, ftpPwd=None):
        self.ui.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.ui.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 490, 480))
        self.ui.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.ui.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.ui.scrollAreaWidgetContents)
        self.ui.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.ui.formLayout_2 = QtWidgets.QFormLayout()
        self.ui.formLayout_2.setObjectName("formLayout_2")
        
        self.ui.horizontalLayout_5.addLayout(self.ui.formLayout_2)
        self.ui.scrollArea.setWidget(self.ui.scrollAreaWidgetContents)

        self.ui.label_6 = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.label_6.setObjectName("label_6")
        self.ui.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.ui.label_6)
        self.ui.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.ui.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.ui.progressBar = QtWidgets.QProgressBar(self.ui.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui.progressBar.sizePolicy().hasHeightForWidth())
        self.ui.progressBar.setSizePolicy(sizePolicy)
        self.ui.progressBar.setObjectName("progressBar")
        self.ui.horizontalLayout_3.addWidget(self.ui.progressBar)
        self.ui.label = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.label.setObjectName("label")
        self.ui.horizontalLayout_3.addWidget(self.ui.label)
        self.ui.formLayout_2.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.ui.horizontalLayout_3)

        worker = SWAdaptorWorker(imgRoot, streetName, ftpUrl, ftpUsr, ftpPwd)
        self.threadpool.start(worker)

    def create_oic(self, prefix, imgRoot, ftpUrl=None, ftpUsr=None, ftpPwd=None):
        self.ui.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.ui.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 490, 480))
        self.ui.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.ui.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.ui.scrollAreaWidgetContents)
        self.ui.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.ui.formLayout_2 = QtWidgets.QFormLayout()
        self.ui.formLayout_2.setObjectName("formLayout_2")
        
        self.ui.horizontalLayout_5.addLayout(self.ui.formLayout_2)
        self.ui.scrollArea.setWidget(self.ui.scrollAreaWidgetContents)

        self.ui.label_6 = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.label_6.setObjectName("label_6")
        self.ui.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.ui.label_6)
        self.ui.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.ui.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.ui.progressBar = QtWidgets.QProgressBar(self.ui.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui.progressBar.sizePolicy().hasHeightForWidth())
        self.ui.progressBar.setSizePolicy(sizePolicy)
        self.ui.progressBar.setObjectName("progressBar")
        self.ui.horizontalLayout_3.addWidget(self.ui.progressBar)
        self.ui.label = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.label.setObjectName("label")
        self.ui.horizontalLayout_3.addWidget(self.ui.label)
        self.ui.formLayout_2.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.ui.horizontalLayout_3)

        worker = CreateOICWorker(prefix, imgRoot, ftpUrl, ftpUsr, ftpPwd)
        self.threadpool.start(worker)

    def outline(self, imgRoot):
        self.ui.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.ui.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 490, 480))
        self.ui.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.ui.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.ui.scrollAreaWidgetContents)
        self.ui.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.ui.formLayout_2 = QtWidgets.QFormLayout()
        self.ui.formLayout_2.setObjectName("formLayout_2")
        
        self.ui.horizontalLayout_5.addLayout(self.ui.formLayout_2)
        self.ui.scrollArea.setWidget(self.ui.scrollAreaWidgetContents)

        self.ui.label_6 = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.label_6.setObjectName("label_6")
        self.ui.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.ui.label_6)
        self.ui.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.ui.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.ui.progressBar = QtWidgets.QProgressBar(self.ui.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui.progressBar.sizePolicy().hasHeightForWidth())
        self.ui.progressBar.setSizePolicy(sizePolicy)
        self.ui.progressBar.setObjectName("progressBar")
        self.ui.horizontalLayout_3.addWidget(self.ui.progressBar)
        self.ui.label = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.label.setObjectName("label")
        self.ui.horizontalLayout_3.addWidget(self.ui.label)
        self.ui.formLayout_2.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.ui.horizontalLayout_3)

        worker = CrackFinderWorker(imgRoot, self.ui.prefix_label.text() + sub("[^0-9a-zA-Z]+", "_", self.ui.nameFeatureLayer.text()))
        self.threadpool.start(worker)

    #TODO: Change to process
    def autoAnnotate(self, objtype, imgRoot):
        self.ui.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.ui.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 490, 480))
        self.ui.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.ui.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.ui.scrollAreaWidgetContents)
        self.ui.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.ui.formLayout_2 = QtWidgets.QFormLayout()
        self.ui.formLayout_2.setObjectName("formLayout_2")
        
        self.ui.horizontalLayout_5.addLayout(self.ui.formLayout_2)
        self.ui.scrollArea.setWidget(self.ui.scrollAreaWidgetContents)

        self.ui.label_6 = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.label_6.setObjectName("label_6")
        self.ui.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.ui.label_6)
        self.ui.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.ui.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.ui.progressBar = QtWidgets.QProgressBar(self.ui.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui.progressBar.sizePolicy().hasHeightForWidth())
        self.ui.progressBar.setSizePolicy(sizePolicy)
        self.ui.progressBar.setObjectName("progressBar")
        self.ui.horizontalLayout_3.addWidget(self.ui.progressBar)
        self.ui.label = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.label.setObjectName("label")
        self.ui.horizontalLayout_3.addWidget(self.ui.label)
        self.ui.formLayout_2.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.ui.horizontalLayout_3)

        worker = DetectionWorker(objtype, imgRoot)
        self.threadpool.start(worker)
        
    def detectOverhangingSigns(self, imgRoot):
        self.ui.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.ui.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 490, 480))
        self.ui.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.ui.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.ui.scrollAreaWidgetContents)
        self.ui.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.ui.formLayout_2 = QtWidgets.QFormLayout()
        self.ui.formLayout_2.setObjectName("formLayout_2")
        
        self.ui.horizontalLayout_5.addLayout(self.ui.formLayout_2)
        self.ui.scrollArea.setWidget(self.ui.scrollAreaWidgetContents)

        self.ui.label_6 = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.label_6.setObjectName("label_6")
        self.ui.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.ui.label_6)
        self.ui.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.ui.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.ui.progressBar = QtWidgets.QProgressBar(self.ui.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui.progressBar.sizePolicy().hasHeightForWidth())
        self.ui.progressBar.setSizePolicy(sizePolicy)
        self.ui.progressBar.setObjectName("progressBar")
        self.ui.horizontalLayout_3.addWidget(self.ui.progressBar)
        self.ui.label = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
        self.ui.label.setObjectName("label")
        self.ui.horizontalLayout_3.addWidget(self.ui.label)
        self.ui.formLayout_2.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.ui.horizontalLayout_3)

        worker = OverhangingSignsWorker(imgRoot, self.ui.prefix_label.text() + sub("[^0-9a-zA-Z]+", "_", self.ui.nameFeatureLayer.text()))
        self.threadpool.start(worker)

    def threadReturn(self, txt):
        _translate = QtCore.QCoreApplication.translate
        
        self.isExecuting = False
        self.ui.sceneComboBox.setEnabled(True)
        self.ui.oicComboBox.setEnabled(True)
        self.ui.nameFeatureLayer.setEnabled(True)
        self.ui.imgRootFolder.setEnabled(True)
        self.ui.streetEditEdit.setEnabled(True)
        self.ui.labelUrlEdit.setEnabled(True)
        self.ui.labelUsrEdit.setEnabled(True)
        self.ui.labelFtpPasswordEdit.setEnabled(True)
        self.ui.disableFTPCheckbox.setEnabled(True)
        self.ui.disableFTPUpdateOICMenuCheckbox.setEnabled(True)
        # self.ui.btnAnnotateOrLocate.setEnabled(False)

        self.ui.btnAnnotateOrLocate.setText(' Execute')
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/icon/execute.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.btnAnnotateOrLocate.setIcon(icon9)
        self.ui.btnAnnotateOrLocate.setAutoDefault(True)
        self.ui.btnAnnotateOrLocate.setDefault(True)

        self.ui.toolButton.setEnabled(True)
        self.ui.openContainerFolderBtn.setEnabled(False)

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Success")

        if txt == 'ftperr':
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Error")

            msg.setText('Cannot connect to FTP server. Please check your credentials.') 
        elif txt != '':
            msg.setText("Completed with issues. Please click \"Details\" for more information.")
            msg.setDetailedText(txt)
        else:
            msg.setText("Success.")
        # msg.setInformativeText("This is additional information")
        # msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()

    def updateProgressExif(self, panopath, cnt, imgslen):
        _translate = QtCore.QCoreApplication.translate

        layoutRowCount = self.ui.formLayout_2.rowCount()
        if cnt==1:
            # print('Hi!')
            self.ui.scrollArea.setWidget(self.ui.scrollAreaWidgetContents)
            self.ui.label_6 = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
            self.ui.label_6.setObjectName("label_6")
            self.ui.label_6.setText(_translate("MainWindow", str(layoutRowCount+1)))
            self.ui.formLayout_2.setWidget(layoutRowCount, QtWidgets.QFormLayout.LabelRole, self.ui.label_6)
            self.ui.horizontalLayout_3 = QtWidgets.QHBoxLayout()
            self.ui.horizontalLayout_3.setObjectName("horizontalLayout_3")
            self.ui.progressBar = QtWidgets.QProgressBar(self.ui.scrollAreaWidgetContents)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.ui.progressBar.sizePolicy().hasHeightForWidth())
            self.ui.progressBar.setSizePolicy(sizePolicy)
            self.ui.progressBar.setObjectName("progressBar")
            self.ui.horizontalLayout_3.addWidget(self.ui.progressBar)
            self.ui.label = QtWidgets.QLabel(self.ui.scrollAreaWidgetContents)
            self.ui.label.setObjectName("label")
            self.ui.horizontalLayout_3.addWidget(self.ui.label)
            self.ui.formLayout_2.setLayout(layoutRowCount, QtWidgets.QFormLayout.FieldRole, self.ui.horizontalLayout_3)
            # print('Hi!!!')

        self.ui.progressBar.setValue(round((cnt-1)/imgslen*100))
        self.ui.label.setText(_translate("MainWindow", "Retrieving data from {0}... ({1}/{2})".format(panopath,cnt,imgslen)))

    def updateProgressPreprocess(self, panopath, cnt, imgslen):
        _translate = QtCore.QCoreApplication.translate
        self.ui.label_6.setText(_translate("MainWindow", "1"))
        self.ui.label.setText(_translate("MainWindow", "Filling dead hole in {0}... ({1}/{2})".format(panopath,cnt,imgslen)))
        self.ui.label_8.setText(_translate("MainWindow", "2"))
        self.ui.label_7.setText(_translate("MainWindow", "Blurring licence plates in {0}... ({1}/{2})".format(panopath,cnt,imgslen)))
        self.ui.label_9.setText(_translate("MainWindow", "3"))
        self.ui.label_10.setText(_translate("MainWindow", "Blurring faces in {0}... ({1}/{2})".format(panopath,cnt,imgslen)))


        self.ui.progressBar.setValue(round((cnt-1)/imgslen*100))
        self.ui.progressBar_2.setValue(round((cnt-1)/imgslen*100))
        self.ui.progressBar_3.setValue(round((cnt-1)/imgslen*100))

    def updateProgressDetect(self, panopath, cnt, imgslen, objtype):
        _translate = QtCore.QCoreApplication.translate
        self.ui.progressBar.setValue(round(cnt/imgslen*100))
        self.ui.label_6.setText(_translate("MainWindow", "1"))
        self.ui.label.setText(_translate("MainWindow", "Finding {0} in {1}... ({2}/{3})".format(objtype.replace('_',' ')+'s',panopath,cnt,imgslen)))

    def downloadProgress(self, progVal, street):
        _translate = QtCore.QCoreApplication.translate
        self.ui.progressBar.setValue(progVal)
        self.ui.label_6.setText(_translate("MainWindow", "1"))
        self.ui.label.setText(_translate("MainWindow", "Downloading 360 images of {0} from Street View...".format(street)))

    def uploadProgress(self, progVal, oic):
        _translate = QtCore.QCoreApplication.translate
        self.ui.progressBar.setValue(progVal)
        self.ui.label_6.setText(_translate("MainWindow", "1"))
        self.ui.label.setText(_translate("MainWindow", "Making OIC {0} on ArcGIS Online... (1/1)".format(oic)))

class Signals(QtCore.QObject):
    ''' Why a whole new class? See here: 
    https://stackoverflow.com/a/25930966/2441026 '''
    updateProgressExifSig = QtCore.pyqtSignal(str, int, int)
    updateProgressPreprocessSig = QtCore.pyqtSignal(str, int, int)
    updateProgressDetectSig = QtCore.pyqtSignal(str, int, int, str)
    downloadProgressSig = QtCore.pyqtSignal(int, str)
    uploadProgressSig = QtCore.pyqtSignal(int, str)
    threadReturnSig = QtCore.pyqtSignal(str)

class PanoramaTagExifWorker(QtCore.QRunnable):
    def __init__(self, imgRoot):
        super(PanoramaTagExifWorker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.imgRoot = imgRoot

    @QtCore.pyqtSlot()
    def run(self):
        #TODO: File-level multiprocessing

        import piexif
        from PIL import Image
        from pyproj import Proj
        from pyproj.transformer import Transformer
        # Standard libraries
        from csv import reader, DictReader, DictWriter
        import datetime
        from glob import glob
        from math import atan2, pi, sqrt, sin, cos, tan
        from os.path import expanduser, basename

        from concurrent.futures import ThreadPoolExecutor

        errorLog = ''

        transformerOut = Transformer.from_crs(
            "epsg:2326",
            "epsg:4326",
        )
        transformerMerc = Transformer.from_crs(
            "epsg:2326",
            "epsg:3857",
        )

        def decdeg2dms(dd):
            mnt,sec = divmod(dd*3600,60)
            deg,mnt = divmod(mnt,60)
            return deg,mnt,sec

        folders = glob(self.imgRoot + r'\*\Imagery\JPG')

        customdic = {}
        for f in folders:
            datafolder = f.replace('JPG','Camera Data')
            datafiles = glob(f'{datafolder}/*/*LB5, 0.csv')
            for x in datafiles:
                with open(x, 'r') as rowCnt:
                    # Notice that 'Northing' headers are duplicated, DictReader cannot be used
                    reader = DictReader(f=rowCnt)
                    row_count = sum(1 for row in reader)
                with open(x, 'r') as input_file:
                    # Notice that 'Northing' headers are duplicated, DictReader cannot be used
                    reader = DictReader(f=input_file)
                    cnt = 0
                    for row in reader:
                        cnt += 1
                        form.signal.updateProgressExifSig.emit(x,cnt,row_count)
                        x2,y2,z2 = transformerOut.transform(float(row[reader.fieldnames[3]]),float(row[reader.fieldnames[2]]),float(row[reader.fieldnames[4]]))
                        dispX = float(row[reader.fieldnames[5]])
                        dispY = float(row[reader.fieldnames[6]])
                        dispZ = float(row[reader.fieldnames[7]])


                        xm,ym,zm = transformerMerc.transform(float(row[reader.fieldnames[3]]),float(row[reader.fieldnames[2]]),float(row[reader.fieldnames[4]]))
                        # print(xm,ym,zm)
                        xmD,ymD,zmD = transformerMerc.transform(float(row[reader.fieldnames[3]])+dispX,float(row[reader.fieldnames[2]])+dispY,float(row[reader.fieldnames[4]])+dispZ)
                        dispX = xmD - xm
                        dispY = ymD - ym
                        dispZ = zmD - zm

                        thirteen = float(row[reader.fieldnames[13]])
                        twelve = float(row[reader.fieldnames[12]])
                        eleven = float(row[reader.fieldnames[11]])

                        heading = (90-thirteen) if (thirteen<90) else (450-thirteen)
                        pitch = 90-twelve
                        roll = eleven

                        # if float(dispY) > 0 and float(dispX) < 0:
                        #     heading = 450 - atan2(dispY, dispX) * 180 / pi
                        # else:
                        #     heading = 90 - atan2(dispY, dispX) * 180 / pi

                        # pitch = 90 + atan2(dispZ,sqrt(dispX**2 + dispY**2) * 180 / pi)
                        
                        # upX = float(row[reader.fieldnames[8]])
                        # upY = float(row[reader.fieldnames[9]])
                        # upZ = float(row[reader.fieldnames[10]])
                        # xmU,ymU,zmU = transform(inProj,webMerc,float(row[reader.fieldnames[3]])+upX,float(row[reader.fieldnames[2]])+upY,float(row[reader.fieldnames[4]])+upZ)
                        # upX = xmU - xm
                        # upY = ymU - ym
                        # upZ = zmU - zm

                        # revHeadingInRad = -heading * pi / 180
                        # revPitchInRad = -(pitch - 90) * pi / 180
                        # upX = upX * cos(revHeadingInRad) + upY * -sin(revHeadingInRad)
                        # upZ = upY * sin(revPitchInRad) + upZ * cos(revPitchInRad)
                        # roll = tan(upX/upZ) * 180 / pi

                        customdic[row[reader.fieldnames[1]]] = {'lat': x2, 'lng': y2, 'alt': z2, 'heading': heading, 'pitch': pitch, 'roll': roll, 'webmercx': xm, 'webmercy': ym, 'webmercz': zm}
                # print(customdic)

            panos = glob(f'{f}/*/Panorama/*.jpg')

            def panoLoop(p):
                if basename(p) in customdic:
                    currEle = customdic[basename(p)]

                    with open(p.replace('.jpg', '.jpt')) as jpt:
                        ts = datetime.datetime.fromtimestamp(float(jpt.read().split(' ')[0]))
                        rts = ((ts.hour,1),(ts.minute,1),(ts.second,1))
                        dates = bytes(ts.strftime('%Y:%m:%d'),'ascii')
                        datesfull = bytes(ts.strftime('%Y:%m:%d %H:%M:%S'),'ascii')

                    im = Image.open(p)

                    xRes = decdeg2dms(currEle['lat'])
                    degX = xRes[0]
                    minutesX = xRes[1]
                    secondsX = xRes[2]

                    yRes = decdeg2dms(currEle['lng'])
                    degY = yRes[0]
                    minutesY = yRes[1]
                    secondsY = yRes[2]

                    exif_dict = piexif.load(im.info["exif"])
                    # print(exif_dict)
                    # print(exif_dict['GPS'])
                    exif_dict['0th'][306] = datesfull
                    exif_dict['Exif'][33437] = (9, 5)
                    exif_dict['Exif'][34850] = 2
                    exif_dict['Exif'][34855] = 20
                    exif_dict['Exif'][36867] = datesfull
                    exif_dict['Exif'][36868] = datesfull
                    exif_dict['Exif'][37121] = b'\x01\x02\x03\x00'
                    exif_dict['Exif'][37377] = (10328, 1105)
                    exif_dict['Exif'][37378] = (2159, 1273)
                    exif_dict['Exif'][37379] = (12262, 1477)
                    exif_dict['Exif'][37380] = (0, 1)
                    exif_dict['Exif'][37383] = 5
                    exif_dict['Exif'][37385] = 16
                    exif_dict['Exif'][37386] = (440, 100)
                    exif_dict['Exif'][37521] = b'007'
                    exif_dict['Exif'][37522] = b'007'
                    exif_dict['Exif'][40960] = b'0100'
                    exif_dict['Exif'][40961] = 65535
                    exif_dict['Exif'][40962] = 2048
                    exif_dict['Exif'][40963] = 2448
                    exif_dict['Exif'][41495] = 2
                    exif_dict['Exif'][41729] = b'\x01'
                    exif_dict['Exif'][41986] = 0
                    exif_dict['Exif'][41987] = 0
                    exif_dict['Exif'][41989] = 28
                    exif_dict['Exif'][41990] = 0
                    exif_dict['Exif'][42034] = ((440, 100), (440, 100), (9, 5), (9, 5))
                    
                    # 11 and 13 are reserved for PitchAngle and RollAngle
                    # , 11: (int(round(currEle['pitch'] * 1000)), 1000), 13: (int(round(currEle['roll'] * 1000)), 1000)
                    exif_dict['GPS'] = {0: (2, 2, 0, 0), 1: b'N', 2: ((int(degX), 1), (int(minutesX), 1), (int(round(secondsX*1000)), 1000)), 3: b'E', 4: ((int(degY), 1), (int(minutesY), 1), (int(round(secondsY*1000)), 1000)), 5: 0, 6: (int(round(currEle['alt']*1000)), 1000), 7: rts, 17: (int(round(currEle['heading'] * 100)), 100), 18: b'WGS-8', 24: (int(round(currEle['heading'] * 100)), 100), 29: dates}
                    # for ifd in ("0th", "Exif", "GPS", "1st"):
                    #     for tag in exif_dict[ifd]:
                    #         print(piexif.TAGS[ifd][tag]["name"], exif_dict[ifd][tag])
                    exif_bytes = piexif.dump(exif_dict)
                    im.save(p, "jpeg", exif=exif_bytes)
                    # print('end')
                else:
                    # print(f'!!! {p} Not found !!!')
                    return f'!!! {p} Not found !!!\n'
            with ThreadPoolExecutor(max_workers=40) as executor:
                for p in panos:
                    res = executor.submit(panoLoop, p)
                    if isinstance(res.result(), str):
                        errorLog += res.result()
            print(errorLog)
            
        base = ', '.join([basename(b.replace('\\Imagery\\JPG','')) for b in folders])
        
        fieldnames = ['filename', 'lat', 'lng', 'alt', 'heading', 'pitch', 'roll', 'webmercx', 'webmercy', 'webmercz']
        coordinatesFieldnames = ['File', 'Time', 'Lat', 'Long', 'Alt', 'course', 'pitch', 'roll']

        with open(self.imgRoot + f'/{base}.csv', 'w', newline='') as csvfile:
            writer = DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            with open(self.imgRoot + '/coordinates.txt', 'w', newline='') as coordinatesTxt:
                coordinatesWriter = DictWriter(coordinatesTxt, fieldnames=coordinatesFieldnames, delimiter='\t')
                coordinatesWriter.writeheader()

                serial = 0
                for x in customdic:
                    writer.writerow({'filename': x, 'lat': customdic[x]['lat'],'lng': customdic[x]['lng'],'alt': customdic[x]['alt'],'heading': customdic[x]['heading'], 'pitch': customdic[x]['pitch'], 'roll': customdic[x]['roll'], 'webmercx': customdic[x]['webmercx'], 'webmercy': customdic[x]['webmercy'], 'webmercz': customdic[x]['webmercz']})
                    coordinatesWriter.writerow({'File': x, 'Time': serial, 'Lat': customdic[x]['lat'],'Long': customdic[x]['lng'], 'Alt': customdic[x]['alt'], 'course': customdic[x]['heading'], 'pitch': customdic[x]['pitch'], 'roll': customdic[x]['roll']})
                    serial += 1
        ''' Output coordinates.txt for Potree'''
        form.signal.threadReturnSig.emit(errorLog)

class PreprocessWorker(QtCore.QRunnable):
    def __init__(self, imgRoot, skipFillingDeadhole):
        super(PreprocessWorker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.imgRoot = imgRoot
        self.skipFillingDeadhole = skipFillingDeadhole

    @QtCore.pyqtSlot()
    def run(self):
        cnt = 0

        panolist = glob(self.imgRoot+'/*/Imagery/JPG/*/Panorama/*.jpg')
        imgslen = len(panolist)
        from gc import collect
        for panopath in panolist:
            cnt += 1
            print(panopath)
            form.signal.updateProgressPreprocessSig.emit(panopath,cnt,imgslen)
            loop = multiprocessing.Process(target=busyProcess, args=(panopath,cnt,self.skipFillingDeadhole,))


            # loop = BusyLoop(panopath)
            collect()
            loop.start()
            loop.join()

            # loop.start()
            # loop.wait()
        form.signal.threadReturnSig.emit('')

class SWAdaptorWorker(QtCore.QRunnable):
    """Street View adaptor."""
    def __init__(self, imgRoot, streetName, ftpUrl=None, ftpUsr=None, ftpPwd=None):
        super(SWAdaptorWorker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.imgRoot = imgRoot
        self.streetName = streetName
        self.ftpUrl = ftpUrl
        self.ftpUsr = ftpUsr
        self.ftpPwd = ftpPwd
        self.prog = 0

    @QtCore.pyqtSlot()
    def run(self):
        from os import chdir, makedirs, remove, rename
        from os.path import expanduser, exists
        from time import sleep
        from re import sub, findall

        from PIL import Image
        import piexif
        from wget import download

        import networkx as nx

        from arcgis.geocoding import geocode
        from urllib.request import urlopen as u
        from bs4 import BeautifulSoup as b

        from selenium import webdriver as wd
        from selenium.webdriver.firefox.options import Options

        from concurrent.futures import ThreadPoolExecutor

        # from csv import DictWriter

        from ftplib import FTP

        if self.ftpUrl is not None:
            try:
                ftpobj = FTP(self.ftpUrl, timeout=99999)
                # ftpobj.set_pasv(True)
                ftpobj.login(self.ftpUsr, self.ftpPwd)
            except:
                form.signal.threadReturnSig.emit('ftperr')
                return

        chdir(self.imgRoot)
        try:
            makedirs(f'{self.streetName}/0/Imagery/JPG/0/Panorama')
        except:
            pass
        chdir(f'{self.streetName}/0/Imagery/JPG/0/Panorama')

        location = geocode('1 ' + self.streetName + ', Hong Kong')[0]['location']
        print(location)
        # location['x'],location['y']

        options = Options()
        options.headless = True

        self.graph = nx.Graph()
        self.former_address = ''
        self.driver = wd.Firefox(options=options)

        def decdeg2dms(dd):
            mnt,sec = divmod(dd*3600,60)
            deg,mnt = divmod(mnt,60)
            return deg,mnt,sec

        def downloadTile(in_id, x, y):
            download('http://cbk0.google.com/cbk?output=tile&panoid={0}&zoom=5&x={1}&y={2}'.format(in_id, x, y), out='{0}_{1}_{2}.jpg'.format(in_id,x,y))

        def recursion(in_id, last_id=None):
            self.prog += 2
            form.signal.downloadProgressSig.emit(self.prog, self.streetName)

            for a in range(10):
                try:
                    self.driver.get('https://istreetview.com/{0}'.format(in_id))
                    sleep(10)
                    self.driver.execute_script("document.querySelector('#pano > div > div:nth-child(11) > div.gmnoprint.gm-bundled-control.gm-bundled-control-on-bottom > div:nth-child(2) > div > button.gm-control-active.gm-compass-needle').click()")
                    break
                except:
                    print('Retry after 5 seconds...')
                    sleep(5)

            # print(self.driver.page_source)

            sleep(4)

            soup=b(self.driver.page_source,'html.parser')

            address=soup.select('#pano > div > div:nth-child(2) > div:nth-child(2) > div.gm-iv-address > div.gm-iv-address-description > div.gm-iv-short-address-description')[0].text

            if self.former_address != '' and sub('^[0-9]+ ', '', address) != self.former_address:
                return

            self.former_address=sub('^[0-9]+ ', '', address)
            print(self.former_address)

            arrows=soup.select('#pano > div > div:nth-child(1) > div > div.gmnoprint > svg')

            for c in arrows[0].children:
                if 'pano' in c.attrs and c['pano'] not in self.graph:
                    headingHack = c['transform']
                    headingHack = (360 + float(findall(r'(?<=rotate\().*(?=\))', c['transform'])[0])) % 360
                    print('Heading: ', headingHack)
                    break

            latlng = findall('(?<=@).*(?=,13z)', soup.select('#pano > div > div:nth-child(2) > div:nth-child(2) > div.gm-iv-address > div.gm-iv-marker > a')[0]['href'])[0].split(',')
            lat = decdeg2dms(float(latlng[0]))
            lng = decdeg2dms(float(latlng[1]))
            print('Lat: ', lat)
            print('Lng: ', lng)

            # Save images
            width_tiles = 32
            length_tiles = 16

            exif_dict = {'GPS': {0: (2, 2, 0, 0), 1: b'N', 2: ((int(lat[0]), 1), (int(lat[1]), 1), (int(round(lat[2]*1000)), 1000)), 3: b'E', 4: ((int(lng[0]), 1), (int(lng[1]), 1), (int(round(lng[2]*1000)), 1000)), 5: 0, 17: (int(round(headingHack * 100)), 100), 18: b'WGS-8', 24: (int(round(headingHack * 100)), 100)}}
            exif_bytes = piexif.dump(exif_dict)


            for a in range(6):
                try:
                    download('http://cbk0.google.com/cbk?output=tile&panoid={0}&zoom=5&x=31&y=15'.format(in_id), out='{0}_31_15.jpg'.format(in_id))
                    break
                except:
                    print('Retry after 3 seconds...')
                    sleep(3)
            if exists('{0}_31_15.jpg'.format(in_id)):
                remove('{0}_31_15.jpg'.format(in_id))
            else:
                width_tiles = 26
                length_tiles = 13

            im = Image.new('RGB', (width_tiles*512, length_tiles*512))

            # Multithreading
            #with ThreadPoolExecutor(max_workers=40) as executor:
            for x in range(width_tiles):
                for y in range(length_tiles):
                    for a in range(10):
                        try:
                            download('http://cbk0.google.com/cbk?output=tile&panoid={0}&zoom=5&x={1}&y={2}'.format(in_id, x, y), out='{0}_{1}_{2}.jpg'.format(in_id,x,y))
                            break
                        except:
                            print('Retry after 3 seconds...')
                            sleep(3)
                    
                    tile = Image.open('{0}_{1}_{2}.jpg'.format(in_id,x,y))

                    im.paste(tile, box=(x*512,y*512))
                    remove('{0}_{1}_{2}.jpg'.format(in_id,x,y))

            im = im.resize((8192,4096))

            if exists(address+'.jpg'):
                suffix = 1
                while exists(address + ' ' + str(suffix) + '.jpg'):
                    suffix += 1
                savename = address + ' ' + str(suffix) + '.jpg'
            else:
                savename = address + '.jpg'
            im.save(savename, exif=exif_bytes)


            self.graph.add_node(in_id, filename=savename)
            if last_id is not None:
                self.graph.add_edge(last_id, in_id)
            
            # if self.ftpUrl is not None:
            #     with open(savename,'rb') as file:
            #         ftpobj.storbinary('STOR '+savename, file)
            # Save images

            for c in arrows[0].children:
                if 'pano' in c.attrs and c.attrs['pano'] not in self.graph:
                    recursion(c.attrs['pano'], in_id)


        self.driver.get('https://maps.google.com/maps?ll={y},{x}&q={y},{x}&hl=en&t=h&z=15&layer=c&cbll={y},{x}'.format(**location))
        print('https://maps.google.com/maps?ll={y},{x}&q={y},{x}&hl=en&t=h&z=15&layer=c&cbll={y},{x}'.format(**location))
        sleep(8)

        print(self.driver.current_url)
        gpanid = findall(r'(?<=\!1s).*(?=\!2e)', self.driver.current_url)[0]


        recursion(gpanid)


        for x in self.graph.degree:
            if x[1] == 1:
                source = x[0]
                break
        
        # FTP reinitiate connection
        if self.ftpUrl is not None:
            try:
                ftpobj = FTP(self.ftpUrl, timeout=99999)
                # ftpobj.set_pasv(True)
                ftpobj.login(self.ftpUsr, self.ftpPwd)
            except:
                form.signal.threadReturnSig.emit('ftperr')
                return

        cnt = 0
        for a in nx.dfs_preorder_nodes(self.graph, source):
            sorted_name = format(cnt,'05')+'_'+self.graph.nodes[a]['filename']
            rename(self.graph.nodes[a]['filename'], sorted_name)
            cnt += 1
            if self.ftpUrl is not None:
                with open(sorted_name,'rb') as file:
                    ftpobj.storbinary('STOR '+sorted_name, file)

        if self.ftpUrl is not None:
            ftpobj.quit()

        form.signal.downloadProgressSig.emit(100, self.streetName)
        form.signal.threadReturnSig.emit('')




class CreateOICWorker(QtCore.QRunnable):
    """Create OIC from either custom or Street View data."""
    def __init__(self, prefix, imgRoot, ftpUrl=None, ftpUsr=None, ftpPwd=None):
        super(CreateOICWorker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.prefix = prefix
        self.imgRoot = imgRoot
        self.ftpUrl = ftpUrl
        self.ftpUsr = ftpUsr
        self.ftpPwd = ftpPwd

    @QtCore.pyqtSlot()
    def run(self):
        from subprocess import run as srun
        from ftplib import FTP
        from json import dumps, loads
        from os import remove
        from os.path import basename
        from time import sleep

        form.signal.uploadProgressSig.emit(10, basename(self.imgRoot))
        srun(r'"C:\Program Files\ArcGIS\Pro\bin\Python\envs\my-env\python.exe" "C:\Image_Mgmt_Workflows\OrientedImagery\GPTool\justfortesting.py" {} "{}"'.format(self.prefix, self.imgRoot))
        form.signal.uploadProgressSig.emit(100, basename(self.imgRoot))
        # form.signal.threadReturnSig.emit('')

        ###################################
        #
        #   Use FTP to update OIC list
        #
        ###################################
        
        # AGOL has to process...
        sleep(3)

        # Search for recently added item
        oic = gis.content.search(query="owner:" + gis.users.me.username,item_type="oriented imagery catalog",sort_field="created",sort_order="desc")[0]
        title = oic.title
        homepage = oic.homepage
        oic = gis.content.search(query="owner:" + gis.users.me.username,item_type="feature",sort_field="created",sort_order="desc")[0]
        pointsUrl = oic.url + '/0'
        oic = gis.content.search(query="owner:" + gis.users.me.username,item_type="vector tile layer",sort_field="created",sort_order="desc")[0]
        coverageMapUrl = oic.url

        if self.ftpUrl is not None:
            ftpobj = FTP(self.ftpUrl)
            ftpobj.login(self.ftpUsr, self.ftpPwd)

            ftpobj.retrbinary('RETR %s' % r'oiclayout/configs/OrientedImagery3D/config_widgets_OrientedImagery3D_Widget_13.json', open('tmp.tmp', 'wb').write)
            a = loads(open('tmp.tmp').read())
            a['oic'].append({"title": title, "serviceUrl": pointsUrl, "overviewUrl": coverageMapUrl, "itemUrl": homepage})
            with open('tmp.tmp', 'w') as file:
                file.write(dumps(a))
            ftpobj.storbinary('STOR %s' % r'oiclayout/configs/OrientedImagery3D/config_widgets_OrientedImagery3D_Widget_13.json', open('tmp.tmp', 'rb'))

            remove('tmp.tmp')

        form.signal.threadReturnSig.emit('')


'''TBD: Web app - 8192 * 4096. 
if 'crack':
    'area0'
    'area1'
(819/8192*360-heading) % 360           (819/8192*360+heading) % 360          image.shape[1]
(4096 / 2 - 1638 / 2)/4096*180         (4096 / 2 + 1638 / 2)/4096*180        image.shape[0]       Constants'''
class OverhangingSignsWorker(QtCore.QRunnable):
    """Use YOLOv3 <https://developers.arcgis.com/python/api-reference/arcgis.learn.html#yolov3> to detect overhanging signs."""
    def __init__(self, imgRoot, featureLayerName):
        super(OverhangingSignsWorker, self).__init__()
        # TBD: Store constructor arguments (re-used for processing)
        self.imgRoot = imgRoot
        self.featureLayerName = featureLayerName

    @QtCore.pyqtSlot()
    def run(self):
        from glob import glob
        from os import chdir, mkdir, remove
        from os.path import expanduser, exists
        from shutil import rmtree, copy2
        from subprocess import run
        from random import randint

        from PIL import Image
        from pyproj import Proj
        from pyproj.transformer import Transformer#, AreaOfInterest
        import arcpy

        from json import dumps, loads

        arcpy.SignInToPortal(portalUrl, _u, _p)


        if exists('C:/temp.sddraft'):
            remove('C:/temp.sddraft')

        if exists('C:/temp.sd'):
            remove('C:/temp.sd')

        def dms2decdeg(grad,min,sec):
            return grad + (min * 1/60) + (sec * 1/3600)

        transformer = Transformer.from_crs(
            "epsg:4326",
            "epsg:3857",
            # area_of_interest=AreaOfInterest(114.200322, 22.312877, 114.215299, 22.329041),
        )

        self.imgRoot = expanduser('~/Desktop/tmp/Wing Kee Commerical Building')
        self.imgRoot += '/0/Imagery/JPG/0/Panorama'
         
        chdir(self.imgRoot)

        try:
            rmtree(expanduser(r'~/Desktop/yolov5/runs/detect/temp'))
        except:
            pass

        try:
            mkdir('chips')
        except:
            pass

        uncropped = glob('*.jpg')
        cropppedLen = len(uncropped) * 2
        for img in uncropped:
            i = Image.open(img)
            i2=i.crop((i.size[0]/2-819, i.size[1]/2-819, i.size[0]/2+819, i.size[1]/2+819))
            i2.save('chips/'+img[:-4]+'_cropped0.jpg')

            i3=Image.new('RGB', (1638, 1638))
            i3.paste(i.crop((0, i.size[1]/2-1-819, 819, i.size[1]/2-1+819)), (819,0))
            i3.paste(i.crop((i.size[0]-819, i.size[1]/2-1-819, i.size[0], i.size[1]/2-1+819)), (0,0))
            i3.save('chips/'+img[:-4]+'_cropped1.jpg')
        # python detect.py --source C:/Users/Alex/Desktop/advert_boards/*.jpg --weights runs/train/exp16/weights/best.pt
        chdir(expanduser(r'~\Desktop\yolov5'))

        form.signal.updateProgressDetectSig.emit(img,0,cropppedLen,'overhanging sign')
        run('"C:/Program Files/ArcGIS/Pro/bin/Python/envs/yolov5/python.exe" detect.py --source "{wildcard}" --weights runs/train/exp16/weights/best.pt --save-txt --name temp'.format(wildcard=self.imgRoot + '/chips/*.jpg'))

        # allElements = []
        verticesInPano = []

        # Still needs to get parent EXIF for heading!!!
        chdir(self.imgRoot)
        t = 0.0001 - 0.2
        for p in glob('*.jpg'):
            t += 0.2

            im = Image.open(p)
            exif = im._getexif()
            try:
                # print('Hi')
                lat = exif[34853][2]
                lng = exif[34853][4]

                #############################
                # lat = dms2decdeg(lat[0], lat[1], lat[2])
                # lng = dms2decdeg(lng[0], lng[1], lng[2])

                # lat,lng = transformer.transform(lat,lng)
                # print(lat,lng)
                # # plt.text(lat, lng, f'{cnt}', c='cornflowerblue')
                # heading = exif[34853][24]

                # print(lat[0][0], lat[1][0], lat[2][0] / lat[2][1])
                lat = dms2decdeg(lat[0][0], lat[1][0], lat[2][0] / lat[2][1])
                lng = dms2decdeg(lng[0][0], lng[1][0], lng[2][0] / lng[2][1])

                lat,lng = transformer.transform(lat,lng)
                print(lat,lng)
                # plt.text(lat, lng, f'{cnt}', c='cornflowerblue')
                try:
                    heading = exif[34853][24][0]/exif[34853][24][1]
                except:
                    heading = 0
            except Exception as e:
                print(e)
            l0 = expanduser(r'~/Desktop/yolov5/runs/detect/temp/labels/'+p[:-4]+'_cropped0.txt')
            l1 = expanduser(r'~/Desktop/yolov5/runs/detect/temp/labels/'+p[:-4]+'_cropped1.txt')
            try:
                with open(l0, 'r') as f0:
                    print(l0)
                    txt=f0.read()
                    txt=txt.split('\n')[:-1]
                    for y in txt:
                        splat=y.split(' ')
                        row=[int(splat[0])] + [round(1638*float(x)) for x in splat[1:]]

                        leftPoint = (heading - 1638 / 2 / im.size[0] * 360 + 360) % 360

                        # row=[int(splat[0])] + [(leftPoint + 1638*float(x)/im.size[0] * 360) % 360 for x in splat[1:]]
                        print([
                        (leftPoint + 1638*float(splat[1])/im.size[0] * 360) % 360,
                        (leftPoint + 1638*float(splat[2])/im.size[0] * 360) % 360,
                        (- 1638/2 + 1638*float(splat[3]))/im.size[1]*180,
                        (- 1638/2 + 1638*float(splat[4]))/im.size[1]*180
                        ])

                        verticesInPano.append(dumps({'xy': [
                        (leftPoint + 1638*float(splat[1])/im.size[0] * 360) % 360,
                        (leftPoint + 1638*float(splat[2])/im.size[0] * 360) % 360,
                        (- 1638/2 + 1638*float(splat[3]))/im.size[1]*180,
                        (- 1638/2 + 1638*float(splat[4]))/im.size[1]*180
                        ], 'title': 'gd_sign', 't': p}))
            except:
                print('No instances detected in '+p+' (crop 0)')
            try:
                with open(l1, 'r') as f1:
                    print(l1)
                    txt=f1.read()
                    txt=txt.split('\n')[:-1]
                    for y in txt:
                        splat=y.split(' ')
                        rightPoint = (leftPoint + 180) % 360

                        print([
                        (rightPoint + 1638*float(splat[1])/im.size[0] * 360) % 360,
                        (rightPoint + 1638*float(splat[2])/im.size[0] * 360) % 360,
                        (- 1638/2 + 1638*float(splat[3]))/im.size[1]*180,
                        (- 1638/2 + 1638*float(splat[4]))/im.size[1]*180
                        ])

                        verticesInPano.append(dumps({'xy': [
                        (leftPoint + 1638*float(splat[1])/im.size[0] * 360) % 360,
                        (leftPoint + 1638*float(splat[2])/im.size[0] * 360) % 360,
                        (- 1638/2 + 1638*float(splat[3]))/im.size[1]*180,
                        (- 1638/2 + 1638*float(splat[4]))/im.size[1]*180
                        ], 'title': 'gd_sign', 't': p}))
                        # ([(ttmmpp[0]/image.shape[1]*360+heading) % 360 - 180, (ttmmpp[1] - image.shape[0]/2)/image.shape[0]*180])
            # Store the boxes, Use polygon notation for now.

            except:
                print('No instances detected in '+p+' (crop 1)')

            # allElements.append({'polygon': verticesInPano, 't': t}) #'filename': p
            # allElements.append({'xy': verticesInPano, 't': p, 'title': 'gd_sign'}) #'filename': p

        form.signal.updateProgressDetectSig.emit(img,cropppedLen,cropppedLen,'overhanging sign')


        # Upload to portal

        result = arcpy.management.CreateFeatureclass(
            "C:/temp.gdb", 
            "esri_square" + str(randint(0,10000)), "POINT", spatial_reference=3857)
        feature_class = result[0]

        copy2('C:/Template/Template.aprx', 'C:/temp.aprx')
        copy2('C:/Template/Template.tbx', 'C:/temp.tbx')

        aprx = arcpy.mp.ArcGISProject('C:/temp.aprx')

        map = aprx.listMaps()[0]
        for l in map.listLayers():
            map.removeLayer(l)


        arcpy.management.AddField(feature_class, 'ImgUrn', 'TEXT')
        arcpy.management.AddField(feature_class, 'ImgGeom', 'TEXT', field_length=999999)

        layer = map.addDataFromPath(feature_class)

        for c in verticesInPano:
            with arcpy.da.InsertCursor(layer, ['SHAPE@', 'ImgUrn', 'ImgGeom']) as cursor:
                cursor.insertRow([(lat,lng,),loads(c)['title'],c])
                # cursor.insertRow([c[0], c[1], c[2]])

        aprx.save()

        webFeatureLayerName = self.featureLayerName + str(randint(0,10000))
        draft=map.getWebLayerSharingDraft("HOSTING_SERVER", "FEATURE", webFeatureLayerName)
        bugfix = str(randint(0,10000))
        draft.description = "Automatically generated using customized Preprocessing Tool by Esri China (Hong Kong)"
        draft.summary = "Automatically generated using customized Preprocessing Tool by Esri China (Hong Kong)"
        draft.exportToSDDraft('C:/temp'+bugfix+'.sddraft')

        arcpy.StageService_server('C:/temp'+bugfix+'.sddraft','C:/temp'+bugfix+'.sd') 
        arcpy.UploadServiceDefinition_server('C:/temp'+bugfix+'.sd','My Hosted Services', in_override="OVERRIDE_DEFINITION", in_organization="SHARE_ORGANIZATION")


        form.signal.threadReturnSig.emit('')


class CrackFinderWorker(QtCore.QRunnable):
    """Use MaskRCNN <https://developers.arcgis.com/python/api-reference/arcgis.learn.html#yolov3> to detect common road defects, inclusing cracks and potholes."""
    def __init__(self, imgRoot, featureLayerName):
        super(CrackFinderWorker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.imgRoot = imgRoot
        self.featureLayerName = featureLayerName

    @QtCore.pyqtSlot()
    def run(self):
        import astropy.units as u
        import cv2
        from fil_finder import FilFinder2D
        from imantics import Mask
        import matplotlib.pyplot as plt
        import mrcnn.model as modellib
        import coco
        from numba import cuda
        import numpy as np
        from PIL import Image
        from pprint import pprint
        from random import randint
        from shapely.geometry import Polygon
        import skimage.io
        from skimage.morphology import skeletonize
        from sklearn.cluster import MeanShift as ms
        from subprocess import Popen
        from time import sleep

        from collections import Counter
        from json import dumps, loads
        import os
        from os import chdir
        from os.path import exists, basename, expanduser
        from glob import glob
        from shutil import copy2
        import sys

        from numba import cuda
        from pyproj import Proj
        from pyproj.transformer import Transformer#, AreaOfInterest
        from shapely.geometry import Polygon

        import arcpy
        from arcgis.gis import GIS


        def dms2decdeg(grad,min,sec):
            return grad + (min * 1/60) + (sec * 1/3600)

        gis = GIS('https://www.arcgis.com', username=_u, password=_p)

        # r'C:/Program Files/Preprocessing Utility for Oriented Images\HighwaysTestSet\aaa\Imagery\JPG\bbb\Panorama
        imgRoot = expanduser(r'~\Desktop\HighwaysTestSet\aaa\Imagery\JPG\bbb\Panorama') #r'C:\Users\Alex\Desktop\cracks') #r'C:\Users\Alex\Desktop\cracks'
        chdir(imgRoot)

        device = cuda.get_current_device()
        device.reset()
        cuda.select_device(0)
        cuda.close()

        tally = Counter()

        t = 0.0001 - 0.2
        cnt = 0
        allElements = []
        bufferedObjs = []
        bufferedLbls = []
        buffered = []
        ignore = []

        featureLayerName = 'HighwaysTestSet_Annotate_cracks'

        if os.path.exists('C:/temp.sddraft'):
          os.remove('C:/temp.sddraft')

        if os.path.exists('C:/temp.sd'):
          os.remove('C:/temp.sd')

        CAR_HEIGHT = 2.9

        transformer = Transformer.from_crs(
            "epsg:4326",
            "epsg:3857",
            # area_of_interest=AreaOfInterest(114.200322, 22.312877, 114.215299, 22.329041),
        )

        myms = ms(bandwidth=0.5) #(distance_threshold=0.5, n_clusters=None)

        ####################################################
        #       Define road footprint model - BEGIN
        ####################################################

        # Root directory of the project
        ROOT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + r"\Mask_RCNN-tensorflowone_sewer")# OIC imagery\Mask_RCNN-master")

        # Import Mask RCNN
        sys.path.append(ROOT_DIR)  # To find local version of the library

        sys.path.append(os.path.join(ROOT_DIR, "samples/coco/"))  # To find local version

        # Directory to save logs and trained model
        MODEL_DIR = os.path.join(ROOT_DIR, "logs")

        # Local path to trained weights file
        COCO_MODEL_PATH = os.path.join(ROOT_DIR, "outliner.h5")    # defects.h5

        class InferenceConfig(coco.CocoConfig):
            # Set batch size to 1 since we'll be running inference on
            # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
            GPU_COUNT = 1
            IMAGES_PER_GPU = 1
            NUM_CLASSES = 1 + 1
            IMAGE_MAX_DIM = 2496 #- 64

        config = InferenceConfig()
        

        # Create model object in inference mode.
        model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

        #print(COCO_MODEL_PATH)
        # Load weights trained on MS-COCO
        model.load_weights(COCO_MODEL_PATH, by_name=True)

        class_names = ['BG', 'road']
        allowed_tags = ['road']

        ####################################################
        #       Define road footprint model - END
        ####################################################

        lot = {104: 'crocodile_crack', 179: 'crack', 226: 'pothole'}
        
        jpgs = glob('*.jpg')
        imgslen = len(jpgs)
        for g in jpgs:
            cnt += 1
            t += 0.2
            png = g.replace('.jpg', '_m.png')

            ######################################################
            #   Crop background and pavement out - BEGIN
            #   Output raw form
            ######################################################

            image = skimage.io.imread(panopath)
            results = model.detect([image], verbose=0)

            for r in range(len(results[0]['class_ids'])):
                mask = Mask(results[0]['masks'][:,:,r])


                print(image.shape)

                classname = class_names[results[0]['class_ids'][r]]
                tmp = []

                if len(mask.polygons().points) > 1:
                    outlines = []
                    for pts in mask.polygons().points:
                        for p in pts:
                            outlines.append(p)
                        outlines.append(pts[0])
                    outlines = np.asarray(outlines)
                else:
                    polygon = Polygon(mask.polygons().points[0])
                    polygon = polygon.simplify(1) #0.1


                    outlines = np.asarray(polygon.exterior.coords)[:-1]

                #################################################################
                #   TBD - Outline not a manhole - BEGIN
                #################################################################
                for ttmmpp in outlines:
                    tmp.append([(ttmmpp[0]/image.shape[1]*360+heading) % 360 - 180, (ttmmpp[1] - image.shape[0]/2)/image.shape[0]*180])

                panoY = (mask.bbox()[1] + mask.bbox()[3])/2 /image.shape[0] * (1024 * ZOOM_FACTOR)
                print('panoY is ', panoY)
                x = np.roots([-0.201727, 9.53632, -160.789, 3219.23 - panoY])

                angle = ((mask.bbox()[0] + mask.bbox()[2])/2 /image.shape[1]*360+heading) % 360
                print('angle is ',angle)
                dist = x[x.imag == 0][0].real + 0.5

                print('Estimated ',dist,' m from the centre.')

                polygonLat = lat - dist * np.sin(angle * np.pi/180)
                polygonLng = lng - dist * np.cos(angle * np.pi/180)

                bufferedObjs.append([polygonLat, polygonLng])
                bufferedLbls.append(classname)
                buffered.append({'t': basename(panopath), 'title': classname, 'xy': tmp})
                #################################################################
                #   TBD - Outline not a manhole - END
                #################################################################

                verticesInPano.append({'xy': tmp, 'title': classname})

            allElements.append({'t':t, 'polygon':verticesInPano})
            print(allElements)



            #  Shape of the road => 'Longitudinal', 'Latitudinal', 'Diagonal'
            #  if label == 'crack':
            #      label = 'Longitudinal crack'


            #  For now,
            # if bbox.shape[1] > bbox.shape[0]:
            #     print('')

            #  May need SVC here: outline to category
            #  image[invert(mask)] = 0     # Already in nparray form



            ######################################################
            #   Crop background and pavement out - END
            ######################################################


            #################################################################
            #   Instance segmentation - BEGIN - Switch MaskRCNN
            #################################################################
            #################################################################
            #   Instance segmentation - END - Switch MaskRCNN
            #################################################################

            if exists(png):
                i = np.array(Image.open(png).convert('L'))
                print(i.shape)
                uniq = np.unique(i)

                verticesInPano = []

                testopen = Image.open(g)
                widthToTest = testopen.size[0]
                exif = testopen._getexif()
                try:
                    # print('Hi')
                    lat = exif[34853][2]
                    lng = exif[34853][4]

                    #############################
                    # lat = dms2decdeg(lat[0], lat[1], lat[2])
                    # lng = dms2decdeg(lng[0], lng[1], lng[2])

                    # lat,lng = transformer.transform(lat,lng)
                    # print(lat,lng)
                    # # plt.text(lat, lng, f'{cnt}', c='cornflowerblue')
                    # heading = exif[34853][24]

                    # print(lat[0][0], lat[1][0], lat[2][0] / lat[2][1])
                    lat = dms2decdeg(lat[0][0], lat[1][0], lat[2][0] / lat[2][1])
                    lng = dms2decdeg(lng[0][0], lng[1][0], lng[2][0] / lng[2][1])

                    lat,lng = transformer.transform(lat,lng)
                    print(lat,lng)
                    # plt.text(lat, lng, f'{cnt}', c='cornflowerblue')
                    try:
                        heading = exif[34853][24][0]/exif[34853][24][1]
                    except:
                        heading = 0
                except Exception as e:
                    print(e)


                for detclass in uniq[1:]:
                    if detclass not in (104, 179):
                        continue
                    # polygon = Polygon(mask.polygons().points[0])
                    # polygon = polygon.simplify(1) #0.1


                    # manholes = np.asarray(polygon.exterior.coords)[:-1]

                    skeleton = (i == detclass) #skeletonize(i == 104)
                    fil = FilFinder2D(skeleton, distance=250 * u.pc, mask=skeleton)
                    fil.preprocess_image(flatten_percent=85)
                    fil.create_mask(border_masking=True, verbose=False, use_existing_mask=True)
                    fil.medskel(verbose=False)

                    # Heuristics: If timeout, treat the type as 'crocodile_crack' - Begin
                    print('Start analyze_skeletons')
                   
                    class FilFindThread(QtCore.QThread):
                        def run(self):
                            fil.analyze_skeletons(branch_thresh=40* u.pix, skel_thresh=10 * u.pix, prune_criteria='length')


                    thread = FilFindThread()
                    thread.start()
                    timeoutCnt = 0
                    crocodile_crack = False
                    while thread.isRunning():
                        if timeoutCnt == 20:
                            thread.terminate()
                            crocodile_crack = True
                        timeoutCnt += 1
                        sleep(1)

                    print('End analyze_skeletons')
                    # Heuristics: If timeout, treat the type as 'crocodile_crack' - End

                    if crocodile_crack:
                        print('Crocodile crack ***')
                        mask = Mask(skeleton)
                        mask.polygons().points
                        # bufferedObjs.append([polygonLat, polygonLng])
                        # bufferedLbls.append(lot[detclass])
                        # buffered.append({'t': basename(g), 'title': lot[detclass], 'xy': tmp, 'totalLength': filament.length().to_value(), 'largestBranchLength': max(filament.branch_properties['length']).to_value()})
                        continue
                    else:                    
                        tmp = []
                        print(fil.filaments[0].longpath_pixel_coords)
                        for filament in fil.filaments:
                            for ttmmpp in range(len(filament.longpath_pixel_coords[0])):
                                if 'Highways' in imgRoot:
                                    heading = filament.longpath_pixel_coords[1][ttmmpp]/i.shape[1]*108.32469177 - 108.32469177/2

                                    heading = (heading + 360) if heading < 0 else heading

                                    tmp.append([heading, filament.longpath_pixel_coords[0][ttmmpp]/i.shape[0]*85.41877747 - 85.41877747/2])

                            item = {}
                            item['xy'] = tmp
                            item['t'] = basename(g)
                            item['title'] = lot[detclass]
                            item['totalLength'] = filament.length().to_value()
                            item['largestBranchLength'] = max(filament.branch_properties['length']).to_value()

                            angle = 0 #TBD
                            dist = 5 #TBD

                            polygonLat = lat - dist * np.sin(angle * np.pi/180)
                            polygonLng = lng - dist * np.cos(angle * np.pi/180)

                            bufferedObjs.append([polygonLat, polygonLng])
                            bufferedLbls.append(lot[detclass])
                            buffered.append({'t': basename(g), 'title': lot[detclass], 'xy': tmp, 'totalLength': filament.length().to_value(), 'largestBranchLength': max(filament.branch_properties['length']).to_value()})
                            
                            verticesInPano.append(item)
                allElements.append({'t': t, 'polygon': verticesInPano})
                print(allElements)

            if t % 15 >= 14.0 and t % 15 < 14.2 or cnt == imgslen:
                if os.path.exists('C:/temp.sddraft'):
                    os.remove('C:/temp.sddraft')

                if os.path.exists('C:/temp.sd'):
                    os.remove('C:/temp.sd')

                coordinates = []

                ###################################################################

                print('Buffered:')
                print(bufferedObjs)
                myms = ms(bandwidth=0.5) #(distance_threshold=0.5, n_clusters=None)

                myms.fit(bufferedObjs)
                print(myms.labels_)
                print(myms.cluster_centers_)

                for x in bufferedObjs:
                    plt.plot(x[0],x[1],'x',color='silver')

                for x in range(len(myms.cluster_centers_)):
                    if np.argmax(myms.labels_ == x) not in ignore and np.count_nonzero(myms.labels_ == x) >= 0: #>= 3: 
                        ignore.append(np.argmax(myms.labels_ == x))

                        lbls = np.array(bufferedLbls)[myms.labels_ == x]
                        (values,counts) = np.unique(lbls,return_counts=True)
                        realLbl = values[counts.argmax()]

                        tally[realLbl] += 1

                        objs = dumps(np.array(buffered)[myms.labels_ == x].tolist()) #.toarray()

                        # print('String rep: ',objs)

                        # plt.plot(myms.cluster_centers_[x][0],myms.cluster_centers_[x][1],'o', color='orange' if realLbl == 'sewer' else 'green' if realLbl == 'road_sewer' else 'midnightblue')
                        # plt.text(polygonLat, polygonLng,f'{cnt}',color='orange' if realLbl == 'sewer' else 'green' if realLbl == 'road_sewer' else 'midnightblue')#, alpha=0.6)
                        coordinates.append(((myms.cluster_centers_[x][0],myms.cluster_centers_[x][1]),realLbl,objs))

                # if initial
                if t >= 14.0 and t < 14.2:
                    ###########################################################
                    #           INIT
                    ###########################################################
                    # Create a feature class with a spatial reference of GCS WGS 1984
                    result = arcpy.management.CreateFeatureclass(
                        "C:/temp.gdb", 
                        "esri_square" + str(randint(0,10000)), "POINT", spatial_reference=3857)
                    feature_class = result[0]

                    copy2('C:/Template/Template.aprx', 'C:/temp.aprx')
                    copy2('C:/Template/Template.tbx', 'C:/temp.tbx')

                    aprx = arcpy.mp.ArcGISProject('C:/temp.aprx')

                    map = aprx.listMaps()[0]
                    for l in map.listLayers():
                        map.removeLayer(l)


                    arcpy.management.AddField(feature_class, 'ImgUrn', 'TEXT')
                    arcpy.management.AddField(feature_class, 'ImgGeom', 'TEXT', field_length=999999)

                    layer = map.addDataFromPath(feature_class)

                    # layer.metadata.description = "[['pavement', 12], ['clearwater', 12], ['large', 12], ['circular', 12], ['wastewater', 12], ['small', 12], ['gas', 12], ['grid', 12], ['striped', 12]]"
                    # layer.metadata.save()
                else:
                    # Override the old web feature layer
                    print('Remove/override old feature layer online')
                    gis.content.search(webFeatureLayerName, item_type='Feature Layer',max_items=1)[0].delete()
                # Write feature to new feature class
                print('Coordinates: ',coordinates)
                for c in coordinates:
                    print('Row inserted: ', [c[0], c[1], 'placeholder'])
                    with arcpy.da.InsertCursor(layer, ['SHAPE@', 'ImgUrn', 'ImgGeom']) as cursor:
                        cursor.insertRow([c[0], c[1], c[2]])


                aprx.save()


                webFeatureLayerName = featureLayerName + str(randint(0,10000))
                draft=map.getWebLayerSharingDraft("HOSTING_SERVER", "FEATURE", webFeatureLayerName)
                bugfix = str(randint(0,10000))
                draft.description = str(tally) # "Automatically generated using customized Preprocessing Tool by Esri China (Hong Kong)"
                draft.summary = str(tally) # "Automatically generated using customized Preprocessing Tool by Esri China (Hong Kong)"
                draft.exportToSDDraft('C:/temp'+bugfix+'.sddraft')

                arcpy.StageService_server('C:/temp'+bugfix+'.sddraft','C:/temp'+bugfix+'.sd') 
                arcpy.UploadServiceDefinition_server('C:/temp'+bugfix+'.sd','My Hosted Services', in_override="OVERRIDE_DEFINITION", in_organization="SHARE_ORGANIZATION")
        form.signal.threadReturnSig.emit('')


# TBD: Handle if .startswith('Highway')
def busyProcess(panopath,cnt,skipFillingDeadhole=False):
    from glob import glob
    import os
    from os import chdir, remove
    from os.path import basename, expanduser
    from subprocess import run
    import sys
    import math
    import random
    from gc import collect
    from shutil import copy2

    import cv2
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image
    import skimage.io
    from numba import cuda

    chdir(os.path.dirname(os.path.realpath(__file__)) + r'\Mask_RCNN-tensorflowone_sewer\samples')
    # import keras

    # Root directory of the project
    ROOT_DIR = os.path.abspath("../")

    # Import Mask RCNN
    sys.path.append(ROOT_DIR)  # To find local version of the library
    import mrcnn.model as modellib
    #from mrcnn import visualize
    # Import COCO config
    sys.path.append(os.path.join(ROOT_DIR, "samples/coco/"))  # To find local version
    import coco


    # Directory to save logs and trained model
    MODEL_DIR = os.path.join(ROOT_DIR, "logs")

    # Local path to trained weights file
    COCO_MODEL_PATH = os.path.join(ROOT_DIR, "carplates.h5")

    # Directory of images to run detection on
    # IMAGE_DIR = os.path.join(ROOT_DIR, "carframes")

    class InferenceConfig(coco.CocoConfig):
        # Set batch size to 1 since we'll be running inference on
        # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
        GPU_COUNT = 1
        IMAGES_PER_GPU = 1
        NUM_CLASSES = 1 + 4

    # COCO Class names

    class_names = ['BG', 'carplate', 'carplatecn', 'carplatet', 'carplatew']

    allowed_tags = ['carplate', 'carplatecn', 'carplatet', 'carplatew']

    # ROI in [ymin, xmin, ymax, xmax] format
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    face_profile = cv2.CascadeClassifier('haarcascade_profileface.xml')

    PADDING_FACE = 0
    PADDING_CARPLATE = 5

    #Invoke

    # form.signal.updateProgressPreprocessSig.emit(panopath,cnt,imgslen)

    outpanopath = 'D:/MMS/' + basename(panopath)

    ########################  INPAINTING ########################
    # if skipFillingDeadhole:
    #     try:
    #         remove(outpanopath)
    #     except:
    #         pass
    #     copy2(panopath, outpanopath)
    # else:
    if True:
        # r'C:/Program Files/Preprocessing Utility for Oriented Images/generative_inpainting_master'
        chdir(expanduser(r'~/Desktop/generative_inpainting_master'))

        run('krpanotools64 transform cube ' + panopath.replace('\\','/') + ' cubemap.jpg -lookat=0,90,0')
        run('krpanotools64 cube2sphere cubemap_b.jpg cubemap_d.jpg cubemap_f.jpg cubemap_l.jpg cubemap_r.jpg cubemap_u.jpg -o='+outpanopath.replace('\\','/'))
        im = Image.open(outpanopath)
        exif_raw = im.info["exif"]
        im = im.crop((716, 138, 716+598, 138+774))
        im.save('tmp.jpg')

        device = cuda.get_current_device()
        device.reset()
        cuda.select_device(0)
        cuda.close()
        run(r'"C:\Program Files\ArcGIS\Pro\bin\Python\envs\my-env\python.exe" test.py --image tmp.jpg --mask sobel9.png --output tmp2.png --checkpoint model_logs/release_places2_256')
        # run(r'"C:\Users\Alexandre Poon\AppData\Local\ESRI\conda\envs\tensorflow2\python.exe" test.py --image tmp.jpg --mask sobel9.png --output tmp2.png --checkpoint model_logs/release_places2_256')
        
        # device = cuda.get_current_device()
        # device.reset()
        run(r'"C:\Program Files\ArcGIS\Pro\bin\Python\envs\my-env\python.exe" test.py --image tmp2.png --mask sobel6.png --output mid.png --checkpoint model_logs/release_places2_256')
        # run(r'"C:\Users\Alexandre Poon\AppData\Local\ESRI\conda\envs\tensorflow2\python.exe" test.py --image tmp2.png --mask sobel6.png --output ' + outpanopath.replace('\\','/').replace('.jpg','_mid') + '.png --checkpoint model_logs/release_places2_256')

        device = cuda.get_current_device()
        device.reset()
        cuda.select_device(0)
        cuda.close()

        im = Image.open(outpanopath)
        im2 = Image.open('mid.png')
        im.paste(im2,box=(716, 138))
        im.save(outpanopath.replace('\\','/'))
        run('krpanotools64 transform cube ' + outpanopath.replace('\\','/') + ' cubemap.jpg -lookat=0,-90,0')
        run('krpanotools64 cube2sphere cubemap_b.jpg cubemap_d.jpg cubemap_f.jpg cubemap_l.jpg cubemap_r.jpg cubemap_u.jpg -o='+outpanopath.replace('\\','/'))
        # run('krpanotools64 cube2sphere cubemap_b.jpg cubemap_d.jpg cubemap_f.jpg cubemap_l.jpg cubemap_r.jpg cubemap_u.jpg -o=./out/'+outpanopath.replace('\\','/').replace('/fill',''))
        remove('tmp.jpg')
        remove('mid.png')
        remove('cubemap_b.jpg')
        remove('cubemap_d.jpg')
        remove('cubemap_f.jpg')
        remove('cubemap_l.jpg')
        remove('cubemap_r.jpg')
        remove('cubemap_u.jpg')

        # Cut since twisted
        a = Image.open(outpanopath)
        b = Image.open(panopath)
        region = a.crop((0, 630, a.size[0], a.size[1]))

        b.paste(region, (0, 630, a.size[0], a.size[1]))
        b.save(outpanopath, quality=100)

    #######################################################

    # chdir(os.path.dirname(os.path.realpath(__file__)) + r'\Mask_RCNN-tensorflowone_sewer\samples') # Just for testing

    pano = cv2.imread(outpanopath, cv2.IMREAD_COLOR)

    pano = cv2.resize(pano, (pano.shape[1]*4, pano.shape[0]*4))

    pano2 = pano.copy()

    #######################################################

    # if 'model' not in vars():
    # Create model object in inference mode.
    config = InferenceConfig()
    
    
    model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

    print(COCO_MODEL_PATH)
    # Load weights trained on MS-COCO
    model.load_weights(COCO_MODEL_PATH, by_name=True)

    for p in range(5):
        ########################  CARPLATE BLURRING ########################        
        
         #0,1,2,3,4 only; 5 is skywards
        framepath = panopath.replace('Panorama','Camera_'+str(p)).replace('.jpg','_Camera_'+str(p)+'.jpg')
        print(f'****** Processing {framepath}')
        
        polished_results = []

        image = skimage.io.imread(framepath)
        image = np.rot90(image,3)
        results = model.detect([image], verbose=0)

        for r in range(len(results[0]['class_ids'])):
            classname = class_names[results[0]['class_ids'][r]]
            # print(results[0]['rois'][r][1],results[0]['rois'][r][3])
            polished_results.append((results[0]['rois'][r], results[0]['masks'][:,:,r][results[0]['rois'][r][0]-PADDING_CARPLATE:results[0]['rois'][r][2]+PADDING_CARPLATE,results[0]['rois'][r][1]-PADDING_CARPLATE:results[0]['rois'][r][3]+PADDING_CARPLATE], classname))
        
        #r = results[0]
        #visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'], class_names, r['scores'])

        # Use OpenCV version of the image

        img = cv2.imread(framepath, cv2.IMREAD_COLOR)
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

        for m in polished_results:
            template = img[m[0][0]-PADDING_CARPLATE:m[0][2]+PADDING_CARPLATE, m[0][1]-PADDING_CARPLATE:m[0][3]+PADDING_CARPLATE].copy()

            w = template.shape[-2]
            h = template.shape[-3]
            print('carplate')   # print(w,h)
            # print(template.shape)
            try:
                res = cv2.matchTemplate(pano,template,cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                top_left = max_loc
                bottom_right = (top_left[0] + w, top_left[1] + h)
                # print(top_left, bottom_right)

                pano[top_left[1]:top_left[1] + h, top_left[0]:top_left[0]+w][m[1]] = cv2.GaussianBlur(pano[top_left[1]:top_left[1] + h, top_left[0]:top_left[0]+w],(55, 55),0)[m[1]]
            except:
                pass
        ########################  FACE BLURRING ########################

        img = img[1250:1250+765, 0:2048].copy()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.1, 1, maxSize=(60,60))
        faces_p = face_profile.detectMultiScale(gray, 1.1, 1, maxSize=(60,60))

        # Frontal face
        for (x,y,w,h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]

            template = img[y-PADDING_FACE:y+h+PADDING_FACE, x-PADDING_FACE:x+w+PADDING_FACE].copy()

            w = template.shape[-2]
            h = template.shape[-3]
            print('frontface')   # print(w,h)

            try:
                res = cv2.matchTemplate(pano,template,cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                top_left = max_loc
                bottom_right = (top_left[0] + w, top_left[1] + h)
                # print(top_left, bottom_right)
                pano[top_left[1]:top_left[1] + h, top_left[0]:top_left[0]+h] =cv2.GaussianBlur(pano[top_left[1]:top_left[1] + h, top_left[0]:top_left[0]+h],(25, 25),0)
            except:
                pass

        # Sideways face
        for (x,y,w,h) in faces_p:
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]

            template = img[y-PADDING_FACE:y+h+PADDING_FACE, x-PADDING_FACE:x+w+PADDING_FACE].copy()

            w = template.shape[-2]
            h = template.shape[-3]
            print('sideface')   # print(w,h)

            try:
                res = cv2.matchTemplate(pano,template,cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                top_left = max_loc
                bottom_right = (top_left[0] + w, top_left[1] + h)
                # print(top_left, bottom_right)
                pano[top_left[1]:top_left[1] + h, top_left[0]:top_left[0]+h] =cv2.GaussianBlur(pano[top_left[1]:top_left[1] + h, top_left[0]:top_left[0]+h],(25, 25),0)
            except:
                pass
    # device = cuda.get_current_device()
    # device.reset()
    # clear_session()
    pano = cv2.resize(pano, (int(round(pano.shape[1]/4)), int(round(pano.shape[0]/4))))

    # /outpano
    # outpanopath = 'D:/MMS/' + basename(panopath)
    cv2.imwrite(outpanopath, pano, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

    # Add back the EXIF
    Image.open(outpanopath).save(outpanopath, exif=exif_raw)
    model.clear_session()
    del model
    del config
    del modellib
    del coco
    collect()

# Unused
def detectionProcess(panopath, cnt, imgslen, preset, featureLayerName, portalUrl, _u, _p, return_dict): #panopath, cnt, preset, featureLayerName):
    print(return_dict)
    tally = return_dict['tally']
    t = return_dict['t']
    allElements = return_dict['allElements']
    bufferedObjs = return_dict['bufferedObjs']
    bufferedLbls = return_dict['bufferedLbls']
    buffered = return_dict['buffered']
    ignore = return_dict['ignore']
    webFeatureLayerName = return_dict['webFeatureLayerName']

    _translate = QtCore.QCoreApplication.translate

    import cv2
    from imantics import Mask
    from matplotlib import pyplot as plt
    import numpy as np
    import skimage.io
    from sklearn.cluster import MeanShift as ms
    from numba import cuda

    from glob import glob
    from os.path import basename
    from pprint import pprint
    from json import dumps
    from shutil import copy2

    from PIL import Image
    from pyproj import Proj
    from pyproj.transformer import Transformer#, AreaOfInterest
    from shapely.geometry import Polygon

    import arcpy
    from arcgis import GIS
    import os
    from random import randint

    #################################################################
    #
    #
    #
    #
    #   Search for the last feature layer and remove it
    #
    #
    #
    #
    #################################################################


    device = cuda.get_current_device()
    device.reset()
    cuda.select_device(0)
    cuda.close()

    arcpy.SignInToPortal(portalUrl, _u, _p)

    if os.path.exists('C:/temp.sddraft'):
      os.remove('C:/temp.sddraft')

    if os.path.exists('C:/temp.sd'):
      os.remove('C:/temp.sd')

    CAR_HEIGHT = 2.9

    transformer = Transformer.from_crs(
        "epsg:4326",
        "epsg:3857",
        # area_of_interest=AreaOfInterest(114.200322, 22.312877, 114.215299, 22.329041),
    )

    import sys
    # import keras

    # Root directory of the project
    ROOT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + r"\Mask_RCNN-tensorflowone_sewer")# OIC imagery\Mask_RCNN-master")

    # Import Mask RCNN
    sys.path.append(ROOT_DIR)  # To find local version of the library
    import mrcnn.model as modellib
    # from mrcnn import visualize
    # Import COCO config
    sys.path.append(os.path.join(ROOT_DIR, "samples/coco/"))  # To find local version
    import coco

    # Directory to save logs and trained model
    MODEL_DIR = os.path.join(ROOT_DIR, "logs")

    # Local path to trained weights file
    if preset == 'sewer':
        COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco_0119.h5") #"mask_rcnn_coco_0080.h5") # 53.h5") #"mask_rcnn_coco_0040.h5")
    else:
        COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco_0087.h5")

    class InferenceConfig(coco.CocoConfig):
        # Set batch size to 1 since we'll be running inference on
        # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
        GPU_COUNT = 1
        IMAGES_PER_GPU = 1
        if preset == 'sewer':
            NUM_CLASSES = 1 + 8
        else:
            NUM_CLASSES = 1 + 4
        IMAGE_MAX_DIM = 2496 + 64 * 6

    config = InferenceConfig()
    

    # Create model object in inference mode.
    model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

    #print(COCO_MODEL_PATH)
    # Load weights trained on MS-COCO
    model.load_weights(COCO_MODEL_PATH, by_name=True)

    if preset == 'sewer':
        class_names = ['BG', 'pavement', 'clearwater', 'small', 'circular', 'wastewater', 'gas', 'grid', 'striped']
        allowed_tags = ['BG', 'pavement', 'clearwater', 'small', 'circular', 'wastewater', 'gas', 'grid', 'striped']
    else:
        class_names = ['BG', 'cone', 'fire_hydrant', 'orange_bin', 'parking_meter']
        allowed_tags = [preset]

    PADDING = 12
    ZOOM_FACTOR = 4


    def dms2decdeg(grad,min,sec):
        return grad + (min * 1/60) + (sec * 1/3600)

    verticesInPano = []

    testopen = Image.open(panopath)
    widthToTest = testopen.size[0]
    exif = testopen._getexif()
    try:
        # print('Hi')
        lat = exif[34853][2]
        lng = exif[34853][4]

        #############################
        # lat = dms2decdeg(lat[0], lat[1], lat[2])
        # lng = dms2decdeg(lng[0], lng[1], lng[2])

        # lat,lng = transformer.transform(lat,lng)
        # print(lat,lng)
        # # plt.text(lat, lng, f'{cnt}', c='cornflowerblue')
        # heading = exif[34853][24]

        # print(lat[0][0], lat[1][0], lat[2][0] / lat[2][1])
        lat = dms2decdeg(lat[0][0], lat[1][0], lat[2][0] / lat[2][1])
        lng = dms2decdeg(lng[0][0], lng[1][0], lng[2][0] / lng[2][1])

        lat,lng = transformer.transform(lat,lng)
        print(lat,lng)
        # plt.text(lat, lng, f'{cnt}', c='cornflowerblue')
        try:
            heading = exif[34853][24][0]/exif[34853][24][1]
        except:
            heading = 0
    except Exception as e:
        print(e)
        return


    '''
    Check pano size. If pano is large enough (or frames not available, like in Google Street View), directly detect on the pano image. 
    '''
    if widthToTest >= 3999: #> 6000:
        image = skimage.io.imread(panopath)
        results = model.detect([image], verbose=0)

        for r in range(len(results[0]['class_ids'])):
            # if results[0]['scores'][r] < 0.9:
            #     print('skip1')
            #     continue
            #print(results[0]['rois'][r][1],results[0]['rois'][r][3])
            mask = Mask(results[0]['masks'][:,:,r])
            print('Area: ',mask.area())
            if mask.area() < 700:
                continue
            print(image.shape)
            # if len(mask.polygons().points) > 1 or mask.polygons().points[0][0][1] < image.shape[1]/2:
            #     print('skip3')
            #     continue



            classname = class_names[results[0]['class_ids'][r]]
            tmp = []

            if len(mask.polygons().points) > 1:
                manholes = []
                for pts in mask.polygons().points:
                    for p in pts:
                        manholes.append(p)
                    manholes.append(pts[0])
                manholes = np.asarray(manholes)
            else:
                polygon = Polygon(mask.polygons().points[0])
                polygon = polygon.simplify(1) #0.1


                manholes = np.asarray(polygon.exterior.coords)[:-1]

            for ttmmpp in manholes:
                if 'Highways' in panopath:
                    heading = ttmmpp[0]/image.shape[1]*108.32469177 - 108.32469177/2

                    heading = (heading + 360) if heading < 0 else heading

                    tmp.append([heading, ttmmpp[1]/image.shape[0]*85.41877747 - 85.41877747/2])
                else:
                    tmp.append([(ttmmpp[0]/image.shape[1]*360+heading) % 360 - 180, (ttmmpp[1] - image.shape[0]/2)/image.shape[0]*180])

            #################################################################
            #                                                               #
            #################################################################

            # The formula / 1024, then * ImageHeight.
            # print('!!!!!!!!!!!!!!',mask.polygons().points[0], mask.bbox())
            # TODO: centroid
            panoY = (mask.bbox()[1] + mask.bbox()[3])/2 /image.shape[0] * (1024 * ZOOM_FACTOR)
            print('panoY is ', panoY)
            x = np.roots([-0.201727, 9.53632, -160.789, 3219.23 - panoY])

            angle = ((mask.bbox()[0] + mask.bbox()[2])/2 /image.shape[1]*360+heading) % 360
            print('angle is ',angle)
            dist = x[x.imag == 0][0].real + 0.5

            print('Estimated ',dist,' m from the centre.')

            polygonLat = lat - dist * np.sin(angle * np.pi/180)
            polygonLng = lng - dist * np.cos(angle * np.pi/180)

            bufferedObjs.append([polygonLat, polygonLng])
            bufferedLbls.append(classname)
            buffered.append({'t': basename(panopath), 'title': classname, 'xy': tmp})
            #################################################################
            #################################################################
            #################################################################

            verticesInPano.append({'xy': tmp, 'title': classname})

        allElements.append({'t':t, 'polygon':verticesInPano})
        print(allElements)
    else:

        '''
        If pano is too small, use frames for detection.
        '''

        pano = cv2.imread(panopath, cv2.IMREAD_COLOR)


        pano = cv2.resize(pano, (pano.shape[1]*ZOOM_FACTOR, pano.shape[0]*ZOOM_FACTOR))

        pano2 = pano.copy()
        #img = cv2.flip(img, 1)


        outpanopath = 'D:/MMS/' + basename(panopath)


        for p in range(5):
             #0,1,2,3,4 only; 5 is skywards
            framepath = panopath.replace('Panorama','Camera_'+str(p)).replace('.jpg','_Camera_'+str(p)+'.jpg')


            #print(framepath)
            
            polished_results = []

            image = skimage.io.imread(framepath)
            image = image[:,-image.shape[0]+400:,:]
            image = np.rot90(image,3)
            results = model.detect([image], verbose=0)

            for r in range(len(results[0]['class_ids'])):
                if results[0]['scores'][r] < 0.9:
                    continue
                #print(results[0]['rois'][r][1],results[0]['rois'][r][3])
                mask = Mask(results[0]['masks'][:,:,r])
                print('Area: ',mask.area())
                if mask.area() < 900 or mask.area() > 80000:#50000:
                    continue
                print(image.shape)
                if len(mask.polygons().points) > 1 or mask.polygons().points[0][0][1] < image.shape[1]/2:
                    continue
                classname = class_names[results[0]['class_ids'][r]]

                polygon = Polygon(mask.polygons().points[0])
                polygon = polygon.simplify(1)
                polygon = np.asarray(polygon.exterior.coords, dtype=np.int32)[:-1]

                # polished_results.append((results[0]['rois'][r],
                #                          results[0]['masks'][:,:,r][results[0]['rois'][r][0]-PADDING:results[0]['rois'][r][2]+PADDING,
                #                                                     results[0]['rois'][r][1]-PADDING:results[0]['rois'][r][3]+PADDING],
                #                          classname,
                #                          mask.polygons().points[0] - np.array([results[0]['rois'][r][1], results[0]['rois'][r][0]])))

                
                polished_results.append((results[0]['rois'][r],
                                         None,# polygon[results[0]['rois'][r][0]-PADDING:results[0]['rois'][r][2]+PADDING,
                                         #                            results[0]['rois'][r][1]-PADDING:results[0]['rois'][r][3]+PADDING],
                                         classname,
                                         polygon - np.array([results[0]['rois'][r][1], results[0]['rois'][r][0]])))
        #         #print(results[0]['masks'][:,:,r].shape)
                
                # #print('I am points',polished_results[0][3])
        #         contours, hierarchy = cv2.findContours(results[0]['masks'][:,:,r], cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # r = results[0]
            # visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'], class_names, r['scores'])
            #########################################################################
            del image
            img = cv2.imread(framepath, cv2.IMREAD_COLOR)
            img = img[:,-img.shape[0]+400:,:]
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

            for m in polished_results:
                template = img[m[0][0]-PADDING:m[0][2]+PADDING, m[0][1]-PADDING:m[0][3]+PADDING].copy()
                w = template.shape[-2]
                h = template.shape[-3]
                #print(w,h)
                #print(template.shape)

                try:
                    res = cv2.matchTemplate(pano,template,cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                    top_left = max_loc
                    # bottom_right = (top_left[0] + w, top_left[1] + h)

                    if (top_left[1] < pano.shape[0]/2):
                        continue
                    #pano[top_left[1]:top_left[1] + h, top_left[0]:top_left[0]+w][m[1]] = cv2.GaussianBlur(pano[top_left[1]:top_left[1] + h, top_left[0]:top_left[0]+w],(55, 55),0)[m[1]]
                    #print('hurrah',m[3])
                    tmp = []
                    if (len(m[3]) >= 2):        #variable
                        for q in range(len(m[3])-1):
                            ttmmpp = m[3][q]+top_left
                            tmp.append([(ttmmpp[0]/pano.shape[1]*360+heading) % 360 - 180, (ttmmpp[1] - pano.shape[0]/2)/pano.shape[0]*180])
                            # tmp.append((m[3][q]+top_left-2).tolist())
                            pano = cv2.line(pano, tuple(m[3][q]+top_left), tuple(m[3][q+1]+top_left), (255,0,0), 12)

                        # tmp.append(np.round((m[3][q+1]+top_left)/ZOOM_FACTOR).astype(int).tolist())
                        ttmmpp = m[3][q+1]+top_left

                        tmp.append([(ttmmpp[0]/pano.shape[1]*360+heading) % 360 - 180, (ttmmpp[1] - pano.shape[0]/2)/pano.shape[0]*180])
                        pano = cv2.line(pano, tuple(m[3][q+1]+top_left), tuple(m[3][0]+top_left), (255,0,0), 12)


                        panoY = top_left[1] + h/2
                        print('panoY is ', panoY)
                        x = np.roots([-0.201727, 9.53632, -160.789, 3219.23 - panoY])
                        # x = np.roots([-0.662782, 19.3473, -218.717, 3299.7])
                        # x = np.roots([-0.618881, 19.0704, -217.857, 3257.17 - panoY])
                        # x = np.roots([-0.15472, 4.76761, -54.4643, 814.292 - panoY])
                        angle = ((top_left[0] + w/2) /pano.shape[1]*360+heading) % 360
                        print('angle is ',angle)
                        dist = x[x.imag == 0][0].real + 0.5

                        # dist = np.sqrt(dist ** 2 - CAR_HEIGHT ** 2) # ROAD SURFACE


                        print('Estimated ',dist,' m from the centre.')

                        polygonLat = lat - dist * np.sin(angle * np.pi/180)
                        polygonLng = lng - dist * np.cos(angle * np.pi/180)
                        print(polygonLat, polygonLng)

                        # plt.text(polygonLat, polygonLng,f'{cnt}',color='orange' if m[2] == 'sewer' else 'green' if m[2] == 'road_sewer' else 'midnightblue')#, alpha=0.6)
                        plt.plot(polygonLat, polygonLng, alpha=0.6)
                        bufferedObjs.append([polygonLat, polygonLng])
                        bufferedLbls.append(m[2])
                        buffered.append({'t': basename(panopath), 'title': m[2], 'xy': tmp})
                        #TODO TODO TODO 

                        # myac.fit([[polygonLat, polygonLng]])

                    verticesInPano.append({'xy': tmp, 'title': m[2]})
                except Exception as ee:
                    print(ee)
                    pass


        print('************************************************************')
        allElements.append({'t':t,'polygon':verticesInPano})
        pprint(allElements)
        print('************************************************************')

        pano = cv2.resize(pano, (int(round(pano.shape[1]/ZOOM_FACTOR)), int(round(pano.shape[0]/ZOOM_FACTOR))))

        cv2.imwrite("res2.png", pano)

    t += 0.2

    # Updates every 1.4 seconds or the whole set has been processed
    if t % 5 >= 2.0 and t % 5 < 2.2 or cnt == imgslen:
        if os.path.exists('C:/temp.sddraft'):
          os.remove('C:/temp.sddraft')

        if os.path.exists('C:/temp.sd'):
          os.remove('C:/temp.sd')

        coordinates = []

        ###################################################################

        print('Buffered:')
        print(bufferedObjs)
        myms = ms(bandwidth=0.5) #(distance_threshold=0.5, n_clusters=None)

        myms.fit(bufferedObjs)
        print(myms.labels_)
        print(myms.cluster_centers_)

        for x in bufferedObjs:
            plt.plot(x[0],x[1],'x',color='silver')

        for x in range(len(myms.cluster_centers_)):
            if np.argmax(myms.labels_ == x) not in ignore and np.count_nonzero(myms.labels_ == x) >= 0: #>= 3: 
                ignore.append(np.argmax(myms.labels_ == x))

                lbls = np.array(bufferedLbls)[myms.labels_ == x]
                (values,counts) = np.unique(lbls,return_counts=True)
                realLbl = values[counts.argmax()]

                tally[realLbl] += 1

                objs = dumps(np.array(buffered)[myms.labels_ == x].tolist()) #.toarray()

                # print('String rep: ',objs)

                plt.plot(myms.cluster_centers_[x][0],myms.cluster_centers_[x][1],'o', color='orange' if realLbl == 'sewer' else 'green' if realLbl == 'road_sewer' else 'midnightblue')
                # plt.text(polygonLat, polygonLng,f'{cnt}',color='orange' if realLbl == 'sewer' else 'green' if realLbl == 'road_sewer' else 'midnightblue')#, alpha=0.6)
                coordinates.append(((myms.cluster_centers_[x][0],myms.cluster_centers_[x][1]),realLbl,objs))

        # if initial
        if t >= 2.0 and t < 2.2:
            ###########################################################
            #           INIT
            ###########################################################
            # Create a feature class with a spatial reference of GCS WGS 1984
            result = arcpy.management.CreateFeatureclass(
                "C:/temp.gdb", 
                "esri_square" + str(randint(0,10000)), "POINT", spatial_reference=3857)
            feature_class = result[0]

            copy2('C:/Template/Template.aprx', 'C:/temp.aprx')
            copy2('C:/Template/Template.tbx', 'C:/temp.tbx')

            aprx = arcpy.mp.ArcGISProject('C:/temp.aprx')

            map = aprx.listMaps()[0]
            for l in map.listLayers():
                map.removeLayer(l)


            arcpy.management.AddField(feature_class, 'ImgUrn', 'TEXT')
            arcpy.management.AddField(feature_class, 'ImgGeom', 'TEXT', field_length=999999)

            layer = map.addDataFromPath(feature_class)

            # layer.metadata.description = "[['pavement', 12], ['clearwater', 12], ['large', 12], ['circular', 12], ['wastewater', 12], ['small', 12], ['gas', 12], ['grid', 12], ['striped', 12]]"
            # layer.metadata.save()
        else:
            # Override the old web feature layer
            print('Remove/override old feature layer online')
            gis = GIS(portalUrl, username=_u, password=_p)
            gis.content.search(webFeatureLayerName, item_type='Feature Layer',max_items=1)[0].delete()

            aprx = arcpy.mp.ArcGISProject('C:/temp.aprx')
            map = aprx.listMaps()[0]
            layer = map.listLayers()[0]

        # Write feature to new feature class
        print('Coordinates: ',coordinates)
        for c in coordinates:
            print('Row inserted: ', [c[0], c[1], 'placeholder'])
            with arcpy.da.InsertCursor(layer, ['SHAPE@', 'ImgUrn', 'ImgGeom']) as cursor:
                cursor.insertRow([c[0], c[1], c[2]])


        aprx.save()


        webFeatureLayerName = featureLayerName + str(randint(0,10000))
        draft=map.getWebLayerSharingDraft("HOSTING_SERVER", "FEATURE", webFeatureLayerName)
        bugfix = str(randint(0,10000))
        draft.description = str(tally) # "Automatically generated using customized Preprocessing Tool by Esri China (Hong Kong)"
        draft.summary = str(tally) # "Automatically generated using customized Preprocessing Tool by Esri China (Hong Kong)"
        draft.exportToSDDraft('C:/temp'+bugfix+'.sddraft')

        arcpy.StageService_server('C:/temp'+bugfix+'.sddraft','C:/temp'+bugfix+'.sd') 
        arcpy.UploadServiceDefinition_server('C:/temp'+bugfix+'.sd','My Hosted Services', in_override="OVERRIDE_DEFINITION", in_organization="SHARE_ORGANIZATION")


        plt.savefig('ffffff___.png')

                # if True:
                #     feature_layer_online = gis.content.search(webFeatureLayerName,item_type='Feature Layer',max_items=1000)[0]
                #     webScenes[-1].add_layer(feature_layer_online) #, options={'title':'Liberia facilities and hospitals'})
    return_dict['tally'] = tally
    return_dict['t'] = t
    return_dict['allElements'] = allElements
    return_dict['bufferedObjs'] = bufferedObjs
    return_dict['bufferedLbls'] = bufferedLbls
    return_dict['buffered'] = buffered
    return_dict['ignore'] = ignore
    return_dict['webFeatureLayerName'] = webFeatureLayerName

    device = cuda.get_current_device()
    device.reset()
    cuda.select_device(0)
    cuda.close()


class DetectionWorker(QtCore.QRunnable):
    def __init__(self, objtype, imgRoot):
        super(DetectionWorker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.objtype = objtype
        self.imgRoot = imgRoot

    @QtCore.pyqtSlot()
    def run(self):
        worker = OldDetectionWorker(self.imgRoot, self.objtype, form.ui.prefix_label.text() + sub("[^0-9a-zA-Z]+", "_", form.ui.nameFeatureLayer.text()))
        form.threadpool.start(worker)


class OldDetectionWorker(QtCore.QRunnable):
    def __init__(self, imgRoot, preset, featureLayerName):
        super(OldDetectionWorker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.imgRoot = imgRoot
        self.preset = preset
        self.featureLayerName = featureLayerName

    @QtCore.pyqtSlot()
    def run(self):
        _translate = QtCore.QCoreApplication.translate

        import cv2
        from imantics import Mask
        from matplotlib import pyplot as plt
        import numpy as np
        import skimage.io
        from sklearn.cluster import MeanShift as ms
        from numba import cuda

        from collections import Counter
        from glob import glob
        from os.path import basename
        from pprint import pprint
        from json import dumps
        from shutil import copy2

        from PIL import Image
        from pyproj import Proj
        from pyproj.transformer import Transformer#, AreaOfInterest
        from shapely.geometry import Polygon

        import arcpy
        import os
        from random import randint
        
        #################################################################
        #
        #
        #
        #
        #   Search for the last feature layer and remove it
        #
        #
        #
        #
        #################################################################


        device = cuda.get_current_device()
        device.reset()
        cuda.select_device(0)
        cuda.close()


        tally = Counter()

        arcpy.SignInToPortal(portalUrl, _u, _p)

        if os.path.exists('C:/temp.sddraft'):
          os.remove('C:/temp.sddraft')

        if os.path.exists('C:/temp.sd'):
          os.remove('C:/temp.sd')

        CAR_HEIGHT = 2.9

        transformer = Transformer.from_crs(
            "epsg:4326",
            "epsg:3857",
            # area_of_interest=AreaOfInterest(114.200322, 22.312877, 114.215299, 22.329041),
        )

        import sys
        # import keras

        # Root directory of the project
        ROOT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + r"\Mask_RCNN-tensorflowone_sewer")# OIC imagery\Mask_RCNN-master")

        # Import Mask RCNN
        sys.path.append(ROOT_DIR)  # To find local version of the library
        import mrcnn.model as modellib
        # from mrcnn import visualize
        # Import COCO config
        sys.path.append(os.path.join(ROOT_DIR, "samples/coco/"))  # To find local version
        import coco

        myms = ms(bandwidth=0.5) #(distance_threshold=0.5, n_clusters=None)

        # Directory to save logs and trained model
        MODEL_DIR = os.path.join(ROOT_DIR, "logs")

        # Local path to trained weights file
        if self.preset == 'sewer':
            COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco_0119.h5") #"mask_rcnn_coco_0080.h5") # 53.h5") #"mask_rcnn_coco_0040.h5")
        else:
            COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco_0087.h5")

        class InferenceConfig(coco.CocoConfig):
            # Set batch size to 1 since we'll be running inference on
            # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
            GPU_COUNT = 1
            IMAGES_PER_GPU = 1
            if self.preset == 'sewer':
                NUM_CLASSES = 1 + 8
            else:
                NUM_CLASSES = 1 + 4
            IMAGE_MAX_DIM = 2496 + 64 * 6

        config = InferenceConfig()
        

        # Create model object in inference mode.
        model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

        #print(COCO_MODEL_PATH)
        # Load weights trained on MS-COCO
        model.load_weights(COCO_MODEL_PATH, by_name=True)

        if self.preset == 'sewer':
            class_names = ['BG', 'pavement', 'clearwater', 'small', 'circular', 'wastewater', 'gas', 'grid', 'striped']
            allowed_tags = ['BG', 'pavement', 'clearwater', 'small', 'circular', 'wastewater', 'gas', 'grid', 'striped']
        else:
            class_names = ['BG', 'cone', 'fire_hydrant', 'orange_bin', 'parking_meter']
            allowed_tags = [self.preset]

        panolist = glob(self.imgRoot+'/*/Imagery/JPG/*/Panorama/*.jpg')
        imgslen = len(panolist)

        PADDING = 12
        ZOOM_FACTOR = 4

        t = 0.0001
        allElements = []

        bufferedObjs = []
        bufferedLbls = []
        buffered = []
        ignore = []


        def dms2decdeg(grad,min,sec):
            return grad + (min * 1/60) + (sec * 1/3600)
        cnt = 0
        for panopath in panolist:#glob(os.path.dirname(os.path.realpath(__file__)) + r'\WingHong\*.jpg'):#panolist:
            cnt += 1

            # Invoke slot
            form.signal.updateProgressDetectSig.emit(panopath,cnt,imgslen,self.preset)
            # QtCore.QMetaObject.invokeMethod(form, 'updateProgress', QtCore.Qt.AutoConnection, Qt.Q_ARG(str, 'beep'))


            verticesInPano = []

            testopen = Image.open(panopath)
            widthToTest = testopen.size[0]
            exif = testopen._getexif()
            try:
                # print('Hi')
                lat = exif[34853][2]
                lng = exif[34853][4]

                #############################
                # lat = dms2decdeg(lat[0], lat[1], lat[2])
                # lng = dms2decdeg(lng[0], lng[1], lng[2])

                # lat,lng = transformer.transform(lat,lng)
                # print(lat,lng)
                # # plt.text(lat, lng, f'{cnt}', c='cornflowerblue')
                # heading = exif[34853][24]

                # print(lat[0][0], lat[1][0], lat[2][0] / lat[2][1])
                lat = dms2decdeg(lat[0][0], lat[1][0], lat[2][0] / lat[2][1])
                lng = dms2decdeg(lng[0][0], lng[1][0], lng[2][0] / lng[2][1])

                lat,lng = transformer.transform(lat,lng)
                print(lat,lng)
                # plt.text(lat, lng, f'{cnt}', c='cornflowerblue')
                try:
                    heading = exif[34853][24][0]/exif[34853][24][1]
                except:
                    heading = 0
            except Exception as e:
                print(e)
                continue
                pass


            '''
            Check pano size. If pano is large enough (or frames not available, like in Google Street View), directly detect on the pano image. 
            '''
            if widthToTest >= 3999: #> 6000:
                image = skimage.io.imread(panopath)
                results = model.detect([image], verbose=0)

                for r in range(len(results[0]['class_ids'])):
                    # if results[0]['scores'][r] < 0.9:
                    #     print('skip1')
                    #     continue
                    #print(results[0]['rois'][r][1],results[0]['rois'][r][3])
                    mask = Mask(results[0]['masks'][:,:,r])
                    print('Area: ',mask.area())
                    if mask.area() < 700:
                        continue
                    print(image.shape)
                    # if len(mask.polygons().points) > 1 or mask.polygons().points[0][0][1] < image.shape[1]/2:
                    #     print('skip3')
                    #     continue



                    classname = class_names[results[0]['class_ids'][r]]
                    tmp = []

                    if len(mask.polygons().points) > 1:
                        manholes = []
                        for pts in mask.polygons().points:
                            for p in pts:
                                manholes.append(p)
                            manholes.append(pts[0])
                        manholes = np.asarray(manholes)
                    else:
                        polygon = Polygon(mask.polygons().points[0])
                        polygon = polygon.simplify(1) #0.1


                        manholes = np.asarray(polygon.exterior.coords)[:-1]

                    for ttmmpp in manholes:
                        if 'Highways' in self.imgRoot:
                            heading = ttmmpp[0]/image.shape[1]*108.32469177 - 108.32469177/2

                            heading = (heading + 360) if heading < 0 else heading

                            tmp.append([heading, ttmmpp[1]/image.shape[0]*85.41877747 - 85.41877747/2])
                        else:
                            tmp.append([(ttmmpp[0]/image.shape[1]*360+heading) % 360 - 180, (ttmmpp[1] - image.shape[0]/2)/image.shape[0]*180])

                    #################################################################
                    #                                                               #
                    #################################################################

                    # The formula / 1024, then * ImageHeight.
                    # print('!!!!!!!!!!!!!!',mask.polygons().points[0], mask.bbox())
                    # TODO: centroid
                    panoY = (mask.bbox()[1] + mask.bbox()[3])/2 /image.shape[0] * (1024 * ZOOM_FACTOR)
                    print('panoY is ', panoY)
                    x = np.roots([-0.201727, 9.53632, -160.789, 3219.23 - panoY])

                    angle = ((mask.bbox()[0] + mask.bbox()[2])/2 /image.shape[1]*360+heading) % 360
                    print('angle is ',angle)
                    dist = x[x.imag == 0][0].real + 0.5

                    print('Estimated ',dist,' m from the centre.')

                    polygonLat = lat - dist * np.sin(angle * np.pi/180)
                    polygonLng = lng - dist * np.cos(angle * np.pi/180)

                    bufferedObjs.append([polygonLat, polygonLng])
                    bufferedLbls.append(classname)
                    buffered.append({'t': basename(panopath), 'title': classname, 'xy': tmp})
                    #################################################################
                    #################################################################
                    #################################################################

                    verticesInPano.append({'xy': tmp, 'title': classname})

                allElements.append({'t':t, 'polygon':verticesInPano})
                print(allElements)
            else:

                '''
                If pano is too small, use frames for detection.
                '''

                pano = cv2.imread(panopath, cv2.IMREAD_COLOR)


                pano = cv2.resize(pano, (pano.shape[1]*ZOOM_FACTOR, pano.shape[0]*ZOOM_FACTOR))

                pano2 = pano.copy()
                #img = cv2.flip(img, 1)


                outpanopath = 'D:/MMS/' + basename(panopath)


                for p in range(5):
                     #0,1,2,3,4 only; 5 is skywards
                    framepath = panopath.replace('Panorama','Camera_'+str(p)).replace('.jpg','_Camera_'+str(p)+'.jpg')


                    #print(framepath)
                    
                    polished_results = []

                    image = skimage.io.imread(framepath)
                    image = image[:,-image.shape[0]+400:,:]
                    image = np.rot90(image,3)
                    results = model.detect([image], verbose=0)

                    for r in range(len(results[0]['class_ids'])):
                        if results[0]['scores'][r] < 0.9:
                            continue
                        #print(results[0]['rois'][r][1],results[0]['rois'][r][3])
                        mask = Mask(results[0]['masks'][:,:,r])
                        print('Area: ',mask.area())
                        if mask.area() < 900 or mask.area() > 80000:#50000:
                            continue
                        print(image.shape)
                        if len(mask.polygons().points) > 1 or mask.polygons().points[0][0][1] < image.shape[1]/2:
                            continue
                        classname = class_names[results[0]['class_ids'][r]]

                        polygon = Polygon(mask.polygons().points[0])
                        polygon = polygon.simplify(1)
                        polygon = np.asarray(polygon.exterior.coords, dtype=np.int32)[:-1]

                        # polished_results.append((results[0]['rois'][r],
                        #                          results[0]['masks'][:,:,r][results[0]['rois'][r][0]-PADDING:results[0]['rois'][r][2]+PADDING,
                        #                                                     results[0]['rois'][r][1]-PADDING:results[0]['rois'][r][3]+PADDING],
                        #                          classname,
                        #                          mask.polygons().points[0] - np.array([results[0]['rois'][r][1], results[0]['rois'][r][0]])))

                        
                        polished_results.append((results[0]['rois'][r],
                                                 None,# polygon[results[0]['rois'][r][0]-PADDING:results[0]['rois'][r][2]+PADDING,
                                                 #                            results[0]['rois'][r][1]-PADDING:results[0]['rois'][r][3]+PADDING],
                                                 classname,
                                                 polygon - np.array([results[0]['rois'][r][1], results[0]['rois'][r][0]])))
                #         #print(results[0]['masks'][:,:,r].shape)
                        
                        # #print('I am points',polished_results[0][3])
                #         contours, hierarchy = cv2.findContours(results[0]['masks'][:,:,r], cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    
                    # r = results[0]
                    # visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'], class_names, r['scores'])
                    #########################################################################
                    del image
                    img = cv2.imread(framepath, cv2.IMREAD_COLOR)
                    img = img[:,-img.shape[0]+400:,:]
                    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

                    for m in polished_results:
                        template = img[m[0][0]-PADDING:m[0][2]+PADDING, m[0][1]-PADDING:m[0][3]+PADDING].copy()
                        w = template.shape[-2]
                        h = template.shape[-3]
                        #print(w,h)
                        #print(template.shape)

                        try:
                            res = cv2.matchTemplate(pano,template,cv2.TM_CCOEFF_NORMED)
                            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                            top_left = max_loc
                            # bottom_right = (top_left[0] + w, top_left[1] + h)

                            if (top_left[1] < pano.shape[0]/2):
                                continue
                            #pano[top_left[1]:top_left[1] + h, top_left[0]:top_left[0]+w][m[1]] = cv2.GaussianBlur(pano[top_left[1]:top_left[1] + h, top_left[0]:top_left[0]+w],(55, 55),0)[m[1]]
                            #print('hurrah',m[3])
                            tmp = []
                            if (len(m[3]) >= 2):        #variable
                                for q in range(len(m[3])-1):
                                    ttmmpp = m[3][q]+top_left
                                    tmp.append([(ttmmpp[0]/pano.shape[1]*360+heading) % 360 - 180, (ttmmpp[1] - pano.shape[0]/2)/pano.shape[0]*180])
                                    # tmp.append((m[3][q]+top_left-2).tolist())
                                    pano = cv2.line(pano, tuple(m[3][q]+top_left), tuple(m[3][q+1]+top_left), (255,0,0), 12)

                                # tmp.append(np.round((m[3][q+1]+top_left)/ZOOM_FACTOR).astype(int).tolist())
                                ttmmpp = m[3][q+1]+top_left

                                tmp.append([(ttmmpp[0]/pano.shape[1]*360+heading) % 360 - 180, (ttmmpp[1] - pano.shape[0]/2)/pano.shape[0]*180])
                                pano = cv2.line(pano, tuple(m[3][q+1]+top_left), tuple(m[3][0]+top_left), (255,0,0), 12)


                                panoY = top_left[1] + h/2
                                print('panoY is ', panoY)
                                x = np.roots([-0.201727, 9.53632, -160.789, 3219.23 - panoY])
                                # x = np.roots([-0.662782, 19.3473, -218.717, 3299.7])
                                # x = np.roots([-0.618881, 19.0704, -217.857, 3257.17 - panoY])
                                # x = np.roots([-0.15472, 4.76761, -54.4643, 814.292 - panoY])
                                angle = ((top_left[0] + w/2) /pano.shape[1]*360+heading) % 360
                                print('angle is ',angle)
                                dist = x[x.imag == 0][0].real + 0.5

                                # dist = np.sqrt(dist ** 2 - CAR_HEIGHT ** 2) # ROAD SURFACE


                                print('Estimated ',dist,' m from the centre.')

                                polygonLat = lat - dist * np.sin(angle * np.pi/180)
                                polygonLng = lng - dist * np.cos(angle * np.pi/180)
                                print(polygonLat, polygonLng)

                                # plt.text(polygonLat, polygonLng,f'{cnt}',color='orange' if m[2] == 'sewer' else 'green' if m[2] == 'road_sewer' else 'midnightblue')#, alpha=0.6)
                                plt.plot(polygonLat, polygonLng, alpha=0.6)
                                bufferedObjs.append([polygonLat, polygonLng])
                                bufferedLbls.append(m[2])
                                buffered.append({'t': basename(panopath), 'title': m[2], 'xy': tmp})
                                #TODO TODO TODO 

                                # myac.fit([[polygonLat, polygonLng]])

                            verticesInPano.append({'xy': tmp, 'title': m[2]})
                        except Exception as ee:
                            print(ee)
                            pass


                print('************************************************************')
                allElements.append({'t':t,'polygon':verticesInPano})
                pprint(allElements)
                print('************************************************************')

                pano = cv2.resize(pano, (int(round(pano.shape[1]/ZOOM_FACTOR)), int(round(pano.shape[0]/ZOOM_FACTOR))))

                cv2.imwrite("res2.png", pano)

            t += 0.2

            # Updates every 1.4 seconds or the whole set has been processed
            if t % 5 >= 2.0 and t % 5 < 2.2 or cnt == imgslen:
                if os.path.exists('C:/temp.sddraft'):
                  os.remove('C:/temp.sddraft')

                if os.path.exists('C:/temp.sd'):
                  os.remove('C:/temp.sd')

                coordinates = []

                ###################################################################

                print('Buffered:')
                print(bufferedObjs)
                myms.fit(bufferedObjs)
                print(myms.labels_)
                print(myms.cluster_centers_)

                for x in bufferedObjs:
                    plt.plot(x[0],x[1],'x',color='silver')

                for x in range(len(myms.cluster_centers_)):
                    if np.argmax(myms.labels_ == x) not in ignore and np.count_nonzero(myms.labels_ == x) >= 0: #>= 3: 
                        ignore.append(np.argmax(myms.labels_ == x))

                        lbls = np.array(bufferedLbls)[myms.labels_ == x]
                        (values,counts) = np.unique(lbls,return_counts=True)
                        realLbl = values[counts.argmax()]

                        tally[realLbl] += 1

                        objs = dumps(np.array(buffered)[myms.labels_ == x].tolist()) #.toarray()

                        # print('String rep: ',objs)

                        plt.plot(myms.cluster_centers_[x][0],myms.cluster_centers_[x][1],'o', color='orange' if realLbl == 'sewer' else 'green' if realLbl == 'road_sewer' else 'midnightblue')
                        # plt.text(polygonLat, polygonLng,f'{cnt}',color='orange' if realLbl == 'sewer' else 'green' if realLbl == 'road_sewer' else 'midnightblue')#, alpha=0.6)
                        coordinates.append(((myms.cluster_centers_[x][0],myms.cluster_centers_[x][1]),realLbl,objs))

                # if initial
                if t >= 2.0 and t < 2.2:
                    ###########################################################
                    #           INIT
                    ###########################################################
                    # Create a feature class with a spatial reference of GCS WGS 1984
                    result = arcpy.management.CreateFeatureclass(
                        "C:/temp.gdb", 
                        "esri_square" + str(randint(0,10000)), "POINT", spatial_reference=3857)
                    feature_class = result[0]

                    copy2('C:/Template/Template.aprx', 'C:/temp.aprx')
                    copy2('C:/Template/Template.tbx', 'C:/temp.tbx')

                    aprx = arcpy.mp.ArcGISProject('C:/temp.aprx')

                    map = aprx.listMaps()[0]
                    for l in map.listLayers():
                        map.removeLayer(l)


                    arcpy.management.AddField(feature_class, 'ImgUrn', 'TEXT')
                    arcpy.management.AddField(feature_class, 'ImgGeom', 'TEXT', field_length=999999)

                    layer = map.addDataFromPath(feature_class)

                    # layer.metadata.description = "[['pavement', 12], ['clearwater', 12], ['large', 12], ['circular', 12], ['wastewater', 12], ['small', 12], ['gas', 12], ['grid', 12], ['striped', 12]]"
                    # layer.metadata.save()
                else:
                    # Override the old web feature layer
                    print('Remove/override old feature layer online')
                    gis.content.search(webFeatureLayerName, item_type='Feature Layer',max_items=1)[0].delete()
                # Write feature to new feature class
                print('Coordinates: ',coordinates)
                for c in coordinates:
                    print('Row inserted: ', [c[0], c[1], 'placeholder'])
                    with arcpy.da.InsertCursor(layer, ['SHAPE@', 'ImgUrn', 'ImgGeom']) as cursor:
                        cursor.insertRow([c[0], c[1], c[2]])


                aprx.save()


                webFeatureLayerName = self.featureLayerName + str(randint(0,10000))
                draft=map.getWebLayerSharingDraft("HOSTING_SERVER", "FEATURE", webFeatureLayerName)
                bugfix = str(randint(0,10000))
                draft.description = str(tally) # "Automatically generated using customized Preprocessing Tool by Esri China (Hong Kong)"
                draft.summary = str(tally) # "Automatically generated using customized Preprocessing Tool by Esri China (Hong Kong)"
                draft.exportToSDDraft('C:/temp'+bugfix+'.sddraft')

                arcpy.StageService_server('C:/temp'+bugfix+'.sddraft','C:/temp'+bugfix+'.sd') 
                arcpy.UploadServiceDefinition_server('C:/temp'+bugfix+'.sd','My Hosted Services', in_override="OVERRIDE_DEFINITION", in_organization="SHARE_ORGANIZATION")


                plt.savefig('ffffff___.png')

                    # if True:
                    #     feature_layer_online = gis.content.search(webFeatureLayerName,item_type='Feature Layer',max_items=1000)[0]
                    #     webScenes[-1].add_layer(feature_layer_online) #, options={'title':'Liberia facilities and hospitals'})
        form.signal.threadReturnSig.emit('')

class LoginDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.pwdEdit.returnPressed.connect(self.accept)
        self.ui.dialogStandardButtonBox.accepted.connect(self.accept)
        self.ui.dialogStandardButtonBox.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def accept(self):
        # print(self.ui.usrnameEdit.text())
        # print(self.ui.pwdEdit.text())
        try:
            global gis
            global webScenes
            global portalUrl
            global _u
            global _p

            portalUrl = self.ui.portalUrlEdit.text()
            _u = self.ui.usrnameEdit.text()
            _p = self.ui.pwdEdit.text()
            gis = GIS(portalUrl, username=_u, password=_p)
            print(gis)
            # print(gis.content.search('',item_type='Scene',max_item=100))
            self.hide()
            form.show()

            webScenes = gis.content.search('Scene',item_type='Web Scene',max_items=1000)
            self.allScenes = [x.title for x in webScenes]
            for y in self.allScenes:
                form.ui.sceneComboBox.addItem(y)
            if len(self.allScenes) >= 1:
                form.ui.sceneComboBox.setCurrentIndex(len(self.allScenes)-1)

            oics = gis.content.search('Oriented',item_type='Oriented Imagery Catalog',max_items=1000)
            self.allOics = [x.title for x in oics]
            for y in self.allOics:
                form.ui.oicComboBox.addItem(y)
            if len(self.allOics) >= 2:
                form.ui.oicComboBox.setCurrentIndex(len(self.allOics)-2)
        except Exception as e:
            # self.hide()
            # form.show()
            print(e)
            if 'Expecting value' in str(e):
                err = 'Cannot find the specified server. Please check the URL and try again.'
            else:
                err = str(e)
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)

            msg.setText(err)
            # msg.setInformativeText("This is additional information")
            msg.setWindowTitle("Error")
            # msg.setDetailedText("The details are as follows:")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()
            # msg.buttonClicked.connect(msgbtn)
            pass

    def reject(self):
        sys.exit(0)

if __name__ == '__main__':

    import sys
    from os import environ

    # environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('fusion')
    # app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    ui = LoginDialog()
    ui.setAttribute(QtCore.Qt.WA_StyledBackground, True)
    ui.show()
    form = Form()
    sys.exit(app.exec_())