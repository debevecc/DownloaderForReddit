# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DatabaseDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DatabaseDialog(object):
    def setupUi(self, DatabaseDialog):
        DatabaseDialog.setObjectName("DatabaseDialog")
        DatabaseDialog.resize(1698, 981)
        DatabaseDialog.setStyleSheet("")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(DatabaseDialog)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.model_focus_group_box = QtWidgets.QGroupBox(DatabaseDialog)
        self.model_focus_group_box.setMinimumSize(QtCore.QSize(0, 61))
        self.model_focus_group_box.setObjectName("model_focus_group_box")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.model_focus_group_box)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.download_session_focus_radio = QtWidgets.QRadioButton(self.model_focus_group_box)
        self.download_session_focus_radio.setObjectName("download_session_focus_radio")
        self.horizontalLayout_2.addWidget(self.download_session_focus_radio)
        self.reddit_object_focus_radio = QtWidgets.QRadioButton(self.model_focus_group_box)
        self.reddit_object_focus_radio.setObjectName("reddit_object_focus_radio")
        self.horizontalLayout_2.addWidget(self.reddit_object_focus_radio)
        self.post_focus_radio = QtWidgets.QRadioButton(self.model_focus_group_box)
        self.post_focus_radio.setObjectName("post_focus_radio")
        self.horizontalLayout_2.addWidget(self.post_focus_radio)
        self.content_focus_radio = QtWidgets.QRadioButton(self.model_focus_group_box)
        self.content_focus_radio.setObjectName("content_focus_radio")
        self.horizontalLayout_2.addWidget(self.content_focus_radio)
        self.comment_focus_radio = QtWidgets.QRadioButton(self.model_focus_group_box)
        self.comment_focus_radio.setObjectName("comment_focus_radio")
        self.horizontalLayout_2.addWidget(self.comment_focus_radio)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.show_download_sessions_checkbox = QtWidgets.QCheckBox(self.model_focus_group_box)
        self.show_download_sessions_checkbox.setObjectName("show_download_sessions_checkbox")
        self.horizontalLayout.addWidget(self.show_download_sessions_checkbox)
        self.show_reddit_objects_checkbox = QtWidgets.QCheckBox(self.model_focus_group_box)
        self.show_reddit_objects_checkbox.setObjectName("show_reddit_objects_checkbox")
        self.horizontalLayout.addWidget(self.show_reddit_objects_checkbox)
        self.show_posts_checkbox = QtWidgets.QCheckBox(self.model_focus_group_box)
        self.show_posts_checkbox.setObjectName("show_posts_checkbox")
        self.horizontalLayout.addWidget(self.show_posts_checkbox)
        self.show_content_checkbox = QtWidgets.QCheckBox(self.model_focus_group_box)
        self.show_content_checkbox.setObjectName("show_content_checkbox")
        self.horizontalLayout.addWidget(self.show_content_checkbox)
        self.show_comments_checkbox = QtWidgets.QCheckBox(self.model_focus_group_box)
        self.show_comments_checkbox.setObjectName("show_comments_checkbox")
        self.horizontalLayout.addWidget(self.show_comments_checkbox)
        self.horizontalLayout_4.addLayout(self.horizontalLayout)
        self.filter_button = QtWidgets.QPushButton(self.model_focus_group_box)
        self.filter_button.setCheckable(True)
        self.filter_button.setObjectName("filter_button")
        self.horizontalLayout_4.addWidget(self.filter_button)
        self.horizontalLayout_5.addWidget(self.model_focus_group_box)
        self.verticalLayout_6.addLayout(self.horizontalLayout_5)
        self.filter_layout = QtWidgets.QGridLayout()
        self.filter_layout.setObjectName("filter_layout")
        self.verticalLayout_6.addLayout(self.filter_layout)
        self.splitter = QtWidgets.QSplitter(DatabaseDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.download_session_widget = QtWidgets.QWidget(self.splitter)
        self.download_session_widget.setObjectName("download_session_widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.download_session_widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.download_session_sort_combo = QtWidgets.QComboBox(self.download_session_widget)
        self.download_session_sort_combo.setObjectName("download_session_sort_combo")
        self.verticalLayout.addWidget(self.download_session_sort_combo)
        self.download_session_list_view = QtWidgets.QListView(self.download_session_widget)
        self.download_session_list_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.download_session_list_view.setObjectName("download_session_list_view")
        self.verticalLayout.addWidget(self.download_session_list_view)
        self.reddit_object_widget = QtWidgets.QWidget(self.splitter)
        self.reddit_object_widget.setObjectName("reddit_object_widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.reddit_object_widget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.reddit_object_sort_combo = QtWidgets.QComboBox(self.reddit_object_widget)
        self.reddit_object_sort_combo.setObjectName("reddit_object_sort_combo")
        self.verticalLayout_2.addWidget(self.reddit_object_sort_combo)
        self.reddit_object_list_view = QtWidgets.QListView(self.reddit_object_widget)
        self.reddit_object_list_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.reddit_object_list_view.setObjectName("reddit_object_list_view")
        self.verticalLayout_2.addWidget(self.reddit_object_list_view)
        self.post_widget = QtWidgets.QWidget(self.splitter)
        self.post_widget.setObjectName("post_widget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.post_widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.post_sort_combo = QtWidgets.QComboBox(self.post_widget)
        self.post_sort_combo.setObjectName("post_sort_combo")
        self.verticalLayout_3.addWidget(self.post_sort_combo)
        self.post_splitter = QtWidgets.QSplitter(self.post_widget)
        self.post_splitter.setOrientation(QtCore.Qt.Vertical)
        self.post_splitter.setObjectName("post_splitter")
        self.post_table_view = QtWidgets.QTableView(self.post_splitter)
        self.post_table_view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.post_table_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.post_table_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.post_table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.post_table_view.setShowGrid(False)
        self.post_table_view.setGridStyle(QtCore.Qt.NoPen)
        self.post_table_view.setObjectName("post_table_view")
        self.post_table_view.horizontalHeader().setCascadingSectionResizes(False)
        self.post_text_browser = QtWidgets.QTextBrowser(self.post_splitter)
        self.post_text_browser.setOpenExternalLinks(True)
        self.post_text_browser.setObjectName("post_text_browser")
        self.verticalLayout_3.addWidget(self.post_splitter)
        self.content_widget = QtWidgets.QWidget(self.splitter)
        self.content_widget.setObjectName("content_widget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.content_widget)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.content_sort_combo = QtWidgets.QComboBox(self.content_widget)
        self.content_sort_combo.setObjectName("content_sort_combo")
        self.verticalLayout_4.addWidget(self.content_sort_combo)
        self.content_list_view = QtWidgets.QListView(self.content_widget)
        self.content_list_view.setStyleSheet("")
        self.content_list_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.content_list_view.setIconSize(QtCore.QSize(0, 0))
        self.content_list_view.setFlow(QtWidgets.QListView.LeftToRight)
        self.content_list_view.setResizeMode(QtWidgets.QListView.Adjust)
        self.content_list_view.setLayoutMode(QtWidgets.QListView.Batched)
        self.content_list_view.setGridSize(QtCore.QSize(0, 0))
        self.content_list_view.setViewMode(QtWidgets.QListView.IconMode)
        self.content_list_view.setBatchSize(10)
        self.content_list_view.setWordWrap(True)
        self.content_list_view.setSelectionRectVisible(True)
        self.content_list_view.setObjectName("content_list_view")
        self.verticalLayout_4.addWidget(self.content_list_view)
        self.comment_widget = QtWidgets.QWidget(self.splitter)
        self.comment_widget.setObjectName("comment_widget")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.comment_widget)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.comment_sort_combo = QtWidgets.QComboBox(self.comment_widget)
        self.comment_sort_combo.setObjectName("comment_sort_combo")
        self.verticalLayout_5.addWidget(self.comment_sort_combo)
        self.comment_tree_view = QtWidgets.QTreeView(self.comment_widget)
        self.comment_tree_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.comment_tree_view.setObjectName("comment_tree_view")
        self.verticalLayout_5.addWidget(self.comment_tree_view)
        self.verticalLayout_6.addWidget(self.splitter)
        self.verticalLayout_7.addLayout(self.verticalLayout_6)

        self.retranslateUi(DatabaseDialog)
        QtCore.QMetaObject.connectSlotsByName(DatabaseDialog)

    def retranslateUi(self, DatabaseDialog):
        _translate = QtCore.QCoreApplication.translate
        DatabaseDialog.setWindowTitle(_translate("DatabaseDialog", "Database"))
        self.model_focus_group_box.setTitle(_translate("DatabaseDialog", "Model Focus"))
        self.download_session_focus_radio.setText(_translate("DatabaseDialog", "Download Sessions"))
        self.reddit_object_focus_radio.setText(_translate("DatabaseDialog", "Reddit Objects"))
        self.post_focus_radio.setText(_translate("DatabaseDialog", "Posts"))
        self.content_focus_radio.setText(_translate("DatabaseDialog", "Content"))
        self.comment_focus_radio.setText(_translate("DatabaseDialog", "Comments"))
        self.show_download_sessions_checkbox.setText(_translate("DatabaseDialog", "Show download sessions"))
        self.show_reddit_objects_checkbox.setText(_translate("DatabaseDialog", "Show reddit objects"))
        self.show_posts_checkbox.setText(_translate("DatabaseDialog", "Show posts"))
        self.show_content_checkbox.setText(_translate("DatabaseDialog", "Show content"))
        self.show_comments_checkbox.setText(_translate("DatabaseDialog", "Show comments"))
        self.filter_button.setText(_translate("DatabaseDialog", "Filter"))

