"""
oraz wprowadzenie nowych funkcjonalnosci
zapis logów oraz zapis skanu musi zawierać dane o interfejsie
Ogarnij formatowanie i wyglad
/todo !

"""
from PyQt5 import QtWidgets, QtGui, Qt, QtCore
import ipaddress as ips
import threading
import Interfaces_module
import datetime


class Adresses(QtCore.QObject):
    sygnal = QtCore.pyqtSignal()
    sygnal2 = QtCore.pyqtSignal(str, str)

    def __init__(self,parent: QtWidgets.QTreeWidget, id: int, ip: str, ttl: int, active=False, mac="unknown"
                 , company="unknown", types="static"):
        super(Adresses, self).__init__()
        self.parent = parent
        self.id = int(id)
        self.ip = ip
        self.mac = mac
        self.active = active
        self.company = company  # company must be from database XML.module
        self.ttl = ttl
        self.types = types
        self.treeitem_content = ['', str(self.ip), self.mac.upper()
                                                 , self.company
                                                 , str(self.active)
                                                 , str(self.ttl)
                                                 , self.types]
        self.qtreeitem = QtWidgets.QTreeWidgetItem(self.parent,
                                                   self.treeitem_content)
        self.qtreeitem.setCheckState(0, QtCore.Qt.Unchecked)
        # ===========================

    def ping_me(self):
        name = "PINGOWANIE "
        from subprocess import Popen, PIPE, SW_HIDE
        p = Popen(f"cmd /c ping -n 1 -l 1 -w 1000 {self.ip}", creationflags=SW_HIDE, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate(b"stdin")
        # rc = p.returncode
        out_str = str(output)
        out_str = out_str[52:-1]
        if out_str.find('timed out.') == -1 and out_str.find("Destination host unreachable.") == -1:
            ttl = out_str[(out_str.find("TTL=") + 4):out_str.find('\\r', (out_str.find("TTL=") + 4))]
            self.ttl = ttl
            self.active = True
            raport = f"Reply   :{self.ip}"
            self.sygnal2.emit(raport, name)
        else:
            self.ttl = -1
            self.active = False
            # print(f"No reply:{self.ip}")
        out_str = ''

    def check(self, root, interfacegateaway):
        interfacegateaway = interfacegateaway
        root = root
        self.ping_me()
        if self.ttl != -1:
            self.check_my_arp()
            self.check_my_type()
            self.find_prod(self.mac_convert())
        else:
            self.ttl = 0
        self.refreash_qtreeitem(root, interfacegateaway)

    def check2(self, root, interfacegateaway):
        interfacegateaway = interfacegateaway
        root = root
        self.ping_me()
        if self.ttl != -1:
            self.check_my_arp()
            self.check_my_type()
            self.find_prod(self.mac_convert())
        else:
            self.ttl = 0
        self.refreash_qtreeitem2(root, interfacegateaway)

    def refreash_qtreeitem2(self, root, interfacegateaway):
        interfacegateaway = interfacegateaway
        root = root
        self.treeitem_content = ['', str(self.ip), self.mac.upper()
                                   , self.company
                                   , str(self.active)
                                   , str(self.ttl)
                                   , self.types]

        for i in range(1, root.childCount()+1):
            if root.child(i-1).text(1) == str(self.ip):
                if self.active:
                    if self.ip == interfacegateaway:
                        color = QtGui.QColor(209, 152, 6)
                        for j in range(0, 7):
                            root.child(i-1).setBackground(j, color)
                            root.child(i-1).setText(j, self.treeitem_content[j])
                    else:
                        color = QtGui.QColor(9, 209, 6)
                        for j in range(0, 7):
                            root.child(i-1).setBackground(j, color)
                            root.child(i-1).setText(j, self.treeitem_content[j])
                    break
                else:
                    if self.ip == interfacegateaway:
                        color = QtGui.QColor(209, 152, 6)
                        for j in range(0, 7):
                            root.child(i-1).setBackground(j, color)
                            root.child(i-1).setText(j, self.treeitem_content[j])
                    else:
                        color = QtGui.QColor(209, 36, 6)
                        for j in range(0, 7):
                            root.child(i-1).setBackground(j, color)
                            root.child(i-1).setText(j, self.treeitem_content[j])
                    break
            else:
                pass
        self.sygnal.emit()

    def check_my_arp(self):
        if self.mac != 'unknown':
            pass
        else:
            from subprocess import Popen, PIPE, SW_HIDE
            p = Popen(f"cmd /c arp {self.ip} -a", creationflags=SW_HIDE, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate(b"stdin")
            # rc = p.returncode
            out_str = str(output)
            if out_str == "b'No ARP Entries Found.\\r\\n'":
                pass
            else:
                out_str = out_str[120:138]
                mac_pos = out_str.find('-')
                mac = out_str[(mac_pos - 2): mac_pos + 15].replace('-', ':', 5)
                self.mac = mac

    def check_my_type(self):
        if self.types != '':
            from subprocess import Popen, PIPE, SW_HIDE
            p = Popen(f"cmd /c arp {self.ip} -a", creationflags=SW_HIDE, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate(b"stdin")
            # rc = p.returncode
            out_str = str(output)
            if out_str.find("No") != -1 and out_str.find("static") == -1:
                self.types = "unknown"
            elif out_str.find("static") != -1:
                self.types = "static"
            else:
                self.types = "dynamic"
        else:
            pass

    def mac_convert(self):
        if self.mac != "unknown":
            convmac = self.mac[0:8].replace(':', '').upper()
            return convmac
        else:
            # print(f"Cannot convert mac because this {self.ip} is free")
            return "------"

    def find_prod(self, convmac):
        import xml.etree.ElementTree as Et
        xmlp = Et.XMLParser(encoding="utf-16")
        tree = Et.parse('baza_xml.xml', xmlp)
        root = tree.getroot()
        for mac in root.findall(f"./Producent/Mac/[@ADRES='{convmac}']..."):
            prod = mac.attrib["NAZWA"]
            self.company = prod

    def get_producent_name(self):
        return self.company

    def refreash_qtreeitem(self, root, interfacegateaway):
        interfacegateaway = interfacegateaway
        root = root
        self.qtreeitem.setCheckState(0, QtCore.Qt.Unchecked)
        self.treeitem_content = ['', str(self.ip), self.mac.upper()
                                   , self.company
                                   , str(self.active)
                                   , str(self.ttl)
                                   , self.types]

        if self.active:
            if self.ip == interfacegateaway:
                color = QtGui.QColor(209, 152, 6)
                for j in range(0, 7):
                    root.child(self.id - 1).setBackground(j, color)
                    root.child(self.id - 1).setText(j, self.treeitem_content[j])
            else:
                color = QtGui.QColor(9, 209, 6)
                for j in range(0, 7):
                    root.child(self.id - 1).setBackground(j, color)
                    root.child(self.id - 1).setText(j, self.treeitem_content[j])
        else:
            if self.ip == interfacegateaway:
                color = QtGui.QColor(209, 152, 6)
                for j in range(0, 7):
                    root.child(self.id - 1).setBackground(j, color)
                    root.child(self.id - 1).setText(j, self.treeitem_content[j])
            else:
                try:
                    color = QtGui.QColor(209, 36, 6)
                    for j in range(0, 7):
                        root.child(self.id - 1).setBackground(j, color)
                        root.child(self.id - 1).setText(j, self.treeitem_content[j])
                except AttributeError:
                    pass
        self.sygnal.emit()


class Scanner(QtWidgets.QWidget):
    sygnal_do_mapy = sygnal = QtCore.pyqtSignal(list)
    def __init__(self, interface: Interfaces_module.Interfaces):
        super(Scanner, self).__init__()
        # self.return_adr = return_adr
        self.connected_interface = interface
        self.logs_hidden = True
        self.siec = None
        self.ilosc_adresow = None
        # lista adresów w sieci (e.g. 192.168.0.1 -> )
        self.adresy = []
        # lista obiektów Adresy
        self.Adresy = []
        self.posortowane_adresy = []
        self.ile_scanowan = 0
        self.scan_stopped = True

        # ===================================

        self.treeWidget_addreses = QtWidgets.QTreeWidget()
        self.ui = QtWidgets.QWidget()
        self.log_widget = QtWidgets.QScrollArea()
        self.log_label = QtWidgets.QLabel(f'\t|Logs of: "{self.connected_interface.name}" scanner actions|')
        self.tree_root = None
        self.hboxlayout = QtWidgets.QHBoxLayout()
        self.vboxlayout = QtWidgets.QVBoxLayout()
        self.mainhboxlayout = QtWidgets.QHBoxLayout()
        self.scan_run_btn = QtWidgets.QPushButton("Skanuj")
        self.save_scan_btn = QtWidgets.QPushButton("Zapisz Skan")
        self.scan_one_btn = QtWidgets.QPushButton("Skanuj Wybrane")
        self.scan_inf_btn = QtWidgets.QPushButton("Ciągłe Skanowanie")
        self.load_scan_btn = QtWidgets.QPushButton("Wczytaj Skan")
        self.make_map_btn = QtWidgets.QPushButton("Stwórz mapę")
        # self.compare_scans_btn = QtWidgets.QPushButton("Porównaj Skany") # /todo
        self.log_btn = QtWidgets.QPushButton("Pokaż logi")
        self.statusbar = QtWidgets.QStatusBar(self.treeWidget_addreses)
        self.buttons = [self.scan_run_btn, self.scan_one_btn, self.load_scan_btn,
                        self.save_scan_btn, self.scan_inf_btn, self.make_map_btn]
        # ===================================
        self.siec_interfejsu()
        self.adresy_w_sieci()
        self.ilosc_adresow_w_sieci()

    @QtCore.pyqtSlot()
    def refreash(self):
        self.treeWidget_addreses.update()
        self.update()

    @QtCore.pyqtSlot(str, str)
    def refresh2(self, text, name):
        self.statusbar.showMessage(text, 1500)
        self.make_log_file(text, name)

    def make_log_file(self, text, name): # /todo !!!
        data = datetime.datetime.today().date()
        czas = datetime.datetime.now().strftime("%H:%M:%S")
        log = f"|{data}|{czas}|[{name}]=[{text}]"
        print(log)
        plik = open(f"{self.connected_interface.name}_scanner_logs.log", 'a')
        plik.write(f"{log}\n")
        plik.close()
        log2 = self.log_label.text() + "\n" + log
        self.log_label.setText(log2)
        self.log_label.adjustSize()
        log2 = log

    def siec_interfejsu(self):
        self.siec = ips.IPv4Network(self.connected_interface.subnet + "/" + self.connected_interface.mask)

    def adresy_w_sieci(self):
        for i in self.siec:
            self.adresy.append(i)

    def ilosc_adresow_w_sieci(self):
        self.ilosc_adresow = self.siec.num_addresses

    def pinguj(self):
        for i in range(0, self.ilosc_adresow - 2):
            if str(self.adresy[i+1]) == self.connected_interface.ipaddress:
                self.Adresy[i].refreash_qtreeitem(self.tree_root, self.connected_interface.def_gateway)
            else:
                mutex = threading.Lock()
                mutex.locked()
                t = threading.Thread(target=self.Adresy[i].check, args=[self.tree_root,
                                                                        self.connected_interface.def_gateway])
                t.start()
    # ///////////////////////

    def scan_(self):
        zaznaczone = []
        for x in range(self.Adresy.__len__()):
            if self.Adresy[x].qtreeitem.checkState(0) != 0:
                self.Adresy[x].check2(self.tree_root, self.connected_interface.def_gateway)
                zaznaczone.append(self.Adresy[x].ip)
        self.refresh2(f"Zeskanowano: {zaznaczone}", "SKANOWANIE ")

    def scan_one(self):
        self.buttons_enabled(self.scan_one_btn, False)
        self.scaner_thread = threading.Thread(target=self.scan_)
        self.scaner_thread.start()
        self.refresh2("Skanowanie zaznaczonych rozpoczęte..", "SKANOWANIE ")
        self.is_live = threading.Thread(target=self.is_scthr_live, args=[self.scan_one_btn])
        self.is_live.start()
    # ///////////////////////

    def connect_ping(self):
        self.buttons_enabled(self.scan_run_btn, False)
        self.ile_scanowan += 1
        self.scaner_thread = threading.Thread(target=self.pinguj)
        self.scaner_thread.start()
        self.refresh2("Skanowanie Rozpoczęte..", "SKANOWANIE ")
        self.is_live = threading.Thread(target=self.is_scthr_live, args=[self.scan_run_btn])
        self.is_live.start()
    # //////////////////////

    def inf_pinguj(self):
        while not self.scan_stopped:
            for i in range(0, self.ilosc_adresow - 2):
                if self.scan_stopped:
                    break
                else:
                    if str(self.adresy[i + 1]) == self.connected_interface.ipaddress:
                        self.Adresy[i].refreash_qtreeitem(self.tree_root, self.connected_interface.def_gateway)
                    else:
                        t = threading.Thread(target=self.Adresy[i].check, args=[self.tree_root,
                                                                                self.connected_interface.def_gateway])
                        t.start()

    def inf_scan(self):
        if self.scan_stopped:
            self.buttons_enabled(self.scan_inf_btn, False)
            self.scan_stopped = False
            self.scan_inf_btn.setText("Stop Scanning")
            self.scaner_thread = threading.Thread(target=self.inf_pinguj)
            self.scaner_thread.start()
            self.refresh2("Ciągłe Skanowanie Rozpoczęte..", "SKANOWANIE ")
            self.is_live = threading.Thread(target=self.is_scthr_live, args=[self.scan_inf_btn])
            self.is_live.start()
        else:
            self.scan_stopped = True
            self.scan_inf_btn.setText("Ciągłe Skanowanie")


    def is_scthr_live(self, button: QtWidgets.QPushButton): # rozwaz dodanie nazwy czynnosci /todo
        while True:
            if self.scaner_thread.is_alive():
                pass
            else:
                # self.treeWidget_addreses.repaint() /todo Ogarnij jak to zrobic
                self.refresh2("Skanowanie Zakończone.", "SKANOWANIE ")
                self.buttons_enabled(button, True)
                break
    # /////////////////////

    def sortujpolaczone(self, i):
        if i != 1:
            self.treeWidget_addreses.sortByColumn(i, 1)
        else:
            pass
    # /////////////////////

    def save_scanned(self):
        self.buttons_enabled(self.save_scan_btn, False)
        self.refresh2("Zapisywanie..", "ZAPISYWANIE")
        if self.ile_scanowan == 1:
            plik = open('zapis_skanu.txt', 'w')
            for i in range(1, self.tree_root.childCount()+1):
                plik.write(f'id={self.Adresy[i-1].id}!ip={self.Adresy[i-1].ip}!mac={self.Adresy[i-1].mac.upper()}!'
                           f'company={self.Adresy[i-1].company}!ttl={self.Adresy[i-1].active}!'
                           f'connected={self.Adresy[i-1].ttl}!'
                           f'types={self.Adresy[i-1].types}\n')
            self.refresh2("Zapisano Pomyślnie.", "ZAPISYWANIE")
            self.buttons_enabled(self.save_scan_btn, True)
            pass
        else:
            # jesli 0 wypisz ze potrzebne jest min jedno skanowanie
            # kolejne skany mniej wazne
            pass
        pass

    def load_scan(self):

        try:
            self.buttons_enabled(self.load_scan_btn, False)
            self.refresh2("Wczytywanie skanu z pliku..", "WCZYTYWANIE")
            plik = open('zapis_skanu.txt', 'r')
            for linia in plik:
                id = int('0')
                saved_treeitem_content = ['']
                dane = linia.split('!')
                for m in dane:
                    dana = m.split('=')
                    if dana[1].find('\\n') != -1:
                        dana[1] = dana[1][:-2]
                    else:
                        pass
                    if dana[0] == "id":
                        id = dana[1]
                        pass
                    else:
                        saved_treeitem_content.append(dana[1])

                for i in range(1, self.tree_root.childCount() + 1):
                    if i == int(id): # self.tree_root.child(i - 1).text(1) == saved_treeitem_content[1]: /todo <-- testowe
                        if saved_treeitem_content[4] == "True":
                            if saved_treeitem_content[1] == self.connected_interface.def_gateway:
                                color = QtGui.QColor(209, 152, 6)
                                for j in range(0, 7):
                                    self.tree_root.child(i - 1).setBackground(j, color)
                                    self.tree_root.child(i - 1).setText(j, saved_treeitem_content[j])
                            else:
                                color = QtGui.QColor(9, 209, 6)
                                for j in range(0, 7):
                                    self.tree_root.child(i - 1).setBackground(j, color)
                                    self.tree_root.child(i - 1).setText(j, saved_treeitem_content[j])
                            break
                        else:
                            if saved_treeitem_content[1] == self.connected_interface.def_gateway:
                                color = QtGui.QColor(209, 152, 6)
                                for j in range(0, 7):
                                    self.tree_root.child(i - 1).setBackground(j, color)
                                    self.tree_root.child(i - 1).setText(j, saved_treeitem_content[j])
                            else:
                                color = QtGui.QColor(209, 36, 6)
                                for j in range(0, 7):
                                    self.tree_root.child(i - 1).setBackground(j, color)
                                    self.tree_root.child(i - 1).setText(j, saved_treeitem_content[j])
                            break
                    else:
                        pass
            self.refresh2("Wczytywanie zakończono pomyślnie.", "WCZYTYWANIE")
            self.buttons_enabled(self.load_scan_btn, True)
        except FileNotFoundError:
            self.refresh2("ERROR: Brak pliku do wczytania." "WCZYTYWANIE")
            self.buttons_enabled(self.load_scan_btn, True)
        pass

    def buttons_enabled(self, caller: QtWidgets.QPushButton, bool: bool):
        for i in self.buttons:
            if i != caller:
                i.setEnabled(bool)
            else: 
                pass

    def showlogs(self):
        if self.logs_hidden:
            self.logs_hidden = False
            self.log_btn.setText("Ukryj Logi")
        else:
            self.logs_hidden = True
            self.log_btn.setText("Pokaż Logi")
        self.log_widget.setHidden(self.logs_hidden)
        self.statusbar.setHidden(not self.logs_hidden)

    def wyslij_sygnal(self):
        self.sygnal_do_mapy.emit(self.Adresy)

    def stworz_ui(self):
        self.ui.setWindowTitle(f"Scaner: {self.connected_interface.name}")
        self.ui.resize(500, 600)
        self.treeWidget_addreses.setHeaderLabels(["Selected", "IP", "MAC", "Company", "Connected", "TTL", "Type"])
        self.treeWidget_addreses.setMinimumWidth(675)
        header = self.treeWidget_addreses.header()

        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        header.setSortIndicator(4, 1)
        header.sectionClicked.connect(self.sortujpolaczone)

        self.ui.setLayout(self.mainhboxlayout)

        self.log_widget.setWindowTitle("Log")
        self.log_widget.setWidget(self.log_label)
        self.log_widget.setMaximumWidth(500)
        self.log_widget.setWidgetResizable(False)
        self.log_widget.setHidden(self.logs_hidden)

        self.hboxlayout.addWidget(self.save_scan_btn)
        self.hboxlayout.addWidget(self.load_scan_btn)
        self.hboxlayout.addWidget(self.scan_run_btn)
        self.hboxlayout.addWidget(self.scan_one_btn)
        self.hboxlayout.addWidget(self.scan_inf_btn)
        self.hboxlayout.addWidget(self.make_map_btn)
        self.hboxlayout.addWidget(self.log_btn)

        self.vboxlayout.addLayout(self.hboxlayout)
        self.vboxlayout.addWidget(self.treeWidget_addreses)
        self.vboxlayout.addWidget(self.statusbar)

        self.mainhboxlayout.addLayout(self.vboxlayout)
        self.mainhboxlayout.addWidget(self.log_widget)

        for s in range(1, self.adresy.__len__()-1):
            if str(self.adresy[s]) == self.connected_interface.ipaddress:
                adrr = Adresses(id=s, ip=str(self.adresy[s]), ttl=128, parent=self.treeWidget_addreses,
                                active=True, mac=self.connected_interface.mac.replace('-', ':'),
                                company=self.connected_interface.desc)
                adrr.sygnal.connect(self.refreash)
                self.Adresy.append(adrr)
            else:
                adrr = Adresses(id=s, ip=str(self.adresy[s]), ttl=-1, parent=self.treeWidget_addreses)
                adrr.sygnal.connect(self.refreash)
                adrr.sygnal2.connect(self.refresh2)
                self.Adresy.append(adrr)
        self.tree_root = self.treeWidget_addreses.invisibleRootItem()

        self.scan_run_btn.clicked.connect(self.connect_ping)
        self.scan_one_btn.clicked.connect(self.scan_one)
        self.save_scan_btn.clicked.connect(self.save_scanned)
        self.load_scan_btn.clicked.connect(self.load_scan)
        self.scan_inf_btn.clicked.connect(self.inf_scan)
        self.log_btn.clicked.connect(self.showlogs)
        self.make_map_btn.clicked.connect(self.wyslij_sygnal)
        self.ui.show()
        pass


if __name__ == '__main__':
    import sys
    import Interfaces_module
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
            skaner = Scanner(n)
            skaner.stworz_ui()
        else:
            pass
    sys.exit(app.exec_())
