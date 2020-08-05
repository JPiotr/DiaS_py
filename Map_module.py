from PyQt5 import QtWidgets, QtGui, Qt, QtCore, QtSvg
import ipaddress as ips
import threading
import Interfaces_module
import Scanner_module
import datetime


class PC(QtSvg.QGraphicsSvgItem):
    def __init__(self, id: int, name: str):
        super(PC, self).__init__()
        # logika
        self.item_id = id
        self.item_name = name
        self.type_id = 0
        self.type_str = ['pc_disconneted', 'pc_connected', 'pc_off']
        self.connected_to = []
        # -^ list of ids
        self.pos_x = 0
        self.pos_y = 0
        self.size_h = 0
        self.size_w = 0
        # qt

    def set_svg_type(self, typ: int):
        self.setElementId(self.type_str[typ])

    def set_item_name(self, name: str):
        self.item_name = name


class Mapa(QtWidgets.QWidget):
    def __init__(self, interface: Interfaces_module.Interfaces, skaner: Scanner_module.Scanner):
        super(Mapa, self).__init__()
        # logika
        self.items = []
        self.skaner = skaner
        self.connected_interface = interface
        # qt
        self.image = QtGui.QImage()
        self.ui = QtWidgets.QWidget()
        self.pc_renderer = QtSvg.QSvgRenderer("pc_svgs.svg")
        self.painter = QtGui.QPainter(self.image)
        self.pen = QtGui.QPen()

    @QtCore.pyqtSlot(list)
    def make_items(self, adresy):
        for i in adresy:
            item = PC(i.id, i.company)
            if i.active:
                item.set_svg_type(2)
                self.update()
            else:
                item.set_svg_type(1)
            self.items.append(item)
    
    def paintEvent(self, event) -> None:
        painter_canvas = QtGui.QPainter(self)
        cos = PC(0,"Nie wiem")
        cos.set_svg_type(2)
        cos.setSharedRenderer(self.pc_renderer)
        self.pc_renderer.render(painter_canvas)
        # painter_canvas.drawImage(self.rect(), self.image, self.image.rect())
        
    def stworz_ui(self):
        self.setWindowTitle(f"Map: {self.connected_interface.name}")
        self.resize(600, 500)
        
        self.pen.setWidth(10)
        self.painter.setPen(self.pen)
        
        self.skaner.sygnal_do_mapy.connect(self.make_items)
        self.show()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # generuj_plik_interfesow()
    w = Interfaces_module.odczyt_bezposrednio_windows_configuration()
    w.windowsconfig_all()
    w.stworz_ui()
    i = Interfaces_module.odczytaj_nazwy_interfejsow()
    for n in i:
        print('')
        print(n.name)
        print(n.dhcp)
        print(n.ipaddress)
        print(n.mask)
        print(n.def_gateway)
        print(n.subnet)
        n.stworz_ui()
        if n.name.lower().find("loopback") == -1:
            skaner = Scanner_module.Scanner(n)
            skaner.stworz_ui()
            mapa = Mapa(n, skaner)
            mapa.stworz_ui()
        else:
            pass
    sys.exit(app.exec_())
