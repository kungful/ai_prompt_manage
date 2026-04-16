from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(807, 613)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_main = QVBoxLayout(self.centralwidget)
        self.verticalLayout_main.setObjectName("verticalLayout_main")

        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName("widget")

        self.navBarLayout = QHBoxLayout(self.widget)
        self.navBarLayout.setObjectName("navBarLayout")

        self.pushButton_6 = QPushButton(self.widget)
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.setText("\u9996\u9875")
        self.navBarLayout.addWidget(self.pushButton_6)

        self.pushButton_7 = QPushButton(self.widget)
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_7.setText("\u8f7d\u5165")
        self.navBarLayout.addWidget(self.pushButton_7)

        self.pushButton_5 = QPushButton(self.widget)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setText("\u8bbe\u7f6e")
        self.navBarLayout.addWidget(self.pushButton_5)

        self.pushButton_8 = QPushButton(self.widget)
        self.pushButton_8.setObjectName("pushButton_8")
        self.pushButton_8.setText("\u5e2e\u52a9")
        self.navBarLayout.addWidget(self.pushButton_8)

        self.label_star = QLabel(self.widget)
        self.label_star.setObjectName("label_star")
        self.label_star.setText("\u2b50")
        self.navBarLayout.addWidget(self.label_star)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.navBarLayout.addWidget(spacer)

        self.verticalLayout_main.addWidget(self.widget)

        self.searchBarLayout = QHBoxLayout()
        self.searchBarLayout.setObjectName("searchBarLayout")

        self.searchLineEdit = QLineEdit(self.centralwidget)
        self.searchLineEdit.setObjectName("searchLineEdit")
        self.searchBarLayout.addWidget(self.searchLineEdit)

        self.searchButton = QPushButton(self.centralwidget)
        self.searchButton.setObjectName("searchButton")
        self.searchButton.setText("\u641c\u7d22")
        self.searchBarLayout.addWidget(self.searchButton)

        self.verticalLayout_main.addLayout(self.searchBarLayout)

        self.iconBarLayout = QHBoxLayout()
        self.iconBarLayout.setObjectName("iconBarLayout")

        self.icon_1 = QFrame(self.centralwidget)
        self.icon_1.setObjectName("icon_1")
        self.icon_1.setFrameShape(QFrame.Shape.Box)
        self.iconBarLayout.addWidget(self.icon_1)

        self.icon_2 = QFrame(self.centralwidget)
        self.icon_2.setObjectName("icon_2")
        self.icon_2.setFrameShape(QFrame.Shape.Box)
        self.iconBarLayout.addWidget(self.icon_2)

        self.icon_3 = QFrame(self.centralwidget)
        self.icon_3.setObjectName("icon_3")
        self.icon_3.setFrameShape(QFrame.Shape.Box)
        self.iconBarLayout.addWidget(self.icon_3)

        self.icon_4 = QFrame(self.centralwidget)
        self.icon_4.setObjectName("icon_4")
        self.icon_4.setFrameShape(QFrame.Shape.Box)
        self.iconBarLayout.addWidget(self.icon_4)

        self.icon_5 = QFrame(self.centralwidget)
        self.icon_5.setObjectName("icon_5")
        self.icon_5.setFrameShape(QFrame.Shape.Box)
        self.iconBarLayout.addWidget(self.icon_5)

        self.icon_6 = QFrame(self.centralwidget)
        self.icon_6.setObjectName("icon_6")
        self.icon_6.setFrameShape(QFrame.Shape.Box)
        self.iconBarLayout.addWidget(self.icon_6)

        self.verticalLayout_main.addLayout(self.iconBarLayout)

        self.contentLayout = QHBoxLayout()
        self.contentLayout.setObjectName("contentLayout")

        self.leftColumn = QVBoxLayout()
        self.leftColumn.setObjectName("leftColumn")

        self.leftBottomFrame = QFrame(self.centralwidget)
        self.leftBottomFrame.setObjectName("leftBottomFrame")
        self.leftBottomFrame.setStyleSheet("border: 1px solid gray;")
        self.leftColumn.addWidget(self.leftBottomFrame)

        self.contentLayout.addLayout(self.leftColumn)

        self.rightColumn = QVBoxLayout()
        self.rightColumn.setObjectName("rightColumn")
        self.rightColumn.setStretch(0, 0)
        self.rightColumn.setStretch(1, 0)

        self.rightTopFrame = QFrame(self.centralwidget)
        self.rightTopFrame.setObjectName("rightTopFrame")
        self.rightTopFrame.setStyleSheet("border: 1px solid gray;")
        self.rightColumn.addWidget(self.rightTopFrame)

        self.rightBottomFrame = QFrame(self.centralwidget)
        self.rightBottomFrame.setObjectName("rightBottomFrame")
        self.rightBottomFrame.setStyleSheet("border: 1px solid gray;")
        self.rightColumn.addWidget(self.rightBottomFrame)

        self.contentLayout.addLayout(self.rightColumn)

        self.verticalLayout_main.addLayout(self.contentLayout)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "Prompt Manager", None)
        )

    # retranslateUi
