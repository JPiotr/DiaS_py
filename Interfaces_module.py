"""
Module for Interface recognizing instance
                  GUI
       |DONE| 20.07.2020r. |DONE|
       POTRZEBNY UPDATE!!!!
       /todo UPDATE
"""
import os
import subprocess
import ipaddress
from PyQt5 import QtWidgets, QtGui, QtCore


class WindowsInterfacesConfi:
    def __init__(self, windowskeys: [], windowsbase: []):
        self.keys = windowskeys
        self.information = windowsbase
        self.created = True
        self.ui = QtWidgets.QWidget()
        self.ui_vbox_layout = QtWidgets.QVBoxLayout()
        self.ui_label_list = []

    def windowsconfig_all(self):
        x = self.keys.__len__()
        for i in range(x):
            print(f"{self.keys[i]}:{self.information[i]}")

    def czy_stworzony(self):
        return self.created

    def stworz_ui(self):
        self.ui.setWindowTitle("Windows Interface Configuration")
        self.ui.resize(350, 200)
        self.ui.setLayout(self.ui_vbox_layout)
        x = self.keys.__len__()
        for i in range(x):
            keys_label = QtWidgets.QLabel(parent=self.ui, text=f"{self.keys[i]}: {self.information[i]}")
            keys_label.setFrameShape(QtWidgets.QFrame.Shape(1))
            keys_label.setFrameShadow(QtWidgets.QFrame.Shadow(1))
            keys_label.setMargin(2)
            keys_label.setFont(QtGui.QFont("Arial", 9))
            keys_label.setStyleSheet("background-color:#222;color:white")
            # keys_label.setAlignment()
            self.ui_vbox_layout.addWidget(keys_label)
            self.ui_label_list.append(keys_label)
        self.ui.show()


class Interfaces(QtWidgets.QWidget):
    def __init__(self, dane_o_interfejsie: []):
        self.nazwy_danych_o_interfejsach = ['IDx', 'Met', 'MTU', 'State', 'Name']
        self.dane_o_interfejsie = dane_o_interfejsie
        self.idx = self.dane_o_interfejsie[0]
        self.met = self.dane_o_interfejsie[1]
        self.mtu = self.dane_o_interfejsie[2]
        self.state = self.dane_o_interfejsie[3]
        self.name = self.dane_o_interfejsie[4]
        self.config_base = []
        self.config_keys = []
        self.dhcp = False
        self.ipaddress = ''
        self.mask = ''
        self.def_gateway = ''
        self.subnet = ''
        self.zapisano_stan = False
        self.macbase = ["Connection Name", "Network Adapter", "Physical Address", "Transport Name"]
        self.mackeys = []
        self.mac = ''
        self.desc = ''
        # ====================
        self.ui = QtWidgets.QWidget()
        self.form_layout = QtWidgets.QFormLayout()
        self.labels = []
        self.hlayout = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton("Zapisz")
        self.restore_btn = QtWidgets.QPushButton("Przywróć")
        self.change_btn = QtWidgets.QPushButton("Wprowadź zmiany")
        # ====================
        self.uzupelnij_dane()
        self.get_dhcp()
        self.dhcp_first = self.dhcp
        self.get_subnet()
        self.get_mask()
        self.get_def_gateway()
        self.get_ipaddress()
        self.odczytaj_mac_i_opis()
        self.get_mac()
        self.get_desc()

    def uzupelnij_dane(self):
        interfaces_keys = []
        interfaces_base = []
        command = f'cmd /c netsh interface ipv4 show config "{self.name}"'
        from subprocess import Popen, PIPE
        p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate(b"stdin")
        out_str = str(output)
        # ====================
        out_str = out_str[6:]
        out_str = out_str[:-9]
        out_str = out_str.replace('    ', '')
        out_str = out_str.replace(':   ', ':')
        out_str = out_str.replace(':  ', ':')
        out_str = out_str.replace(': ', ':')
        lista = out_str.split('\\r\\n')
        # ====================
        print("")
        for h in range(1, lista.__len__()):
            str_lista = lista[h]
            print(str_lista)
            if str_lista.find("Subnet Prefix:") != -1:
                interfaces_base.append(str_lista[:str_lista.find(':')])
                interfaces_keys.append(str_lista[str_lista.find(':')+1:str_lista.find('/')])
                interfaces_base.append("Mask")
                interfaces_keys.append(str_lista[str_lista.find('k ')+2:str_lista.find(')')])
            else:
                interfaces_base.append(str_lista[:str_lista.find(':')])
                interfaces_keys.append(str_lista[str_lista.find(':')+1:])
        self.config_base = interfaces_base
        self.config_keys = interfaces_keys
        # print(self.config_keys)
        # print(self.config_base)

    def get_dhcp(self):
        for i in range(self.config_base.__len__()):
            if self.config_base[i].find('DHCP enabled') != -1:
                if self.config_keys[i].find('Yes') != -1:
                    self.dhcp = True
                    break
                else:
                    self.dhcp = False
                    break
            else:
                pass

    def get_ipaddress(self):
        for i in range(self.config_base.__len__()):
            if self.config_base[i] == 'IP Address':
                self.ipaddress = self.config_keys[i]
                break
            else:
                pass

    def get_subnet(self):
        for i in range(self.config_base.__len__()):
            if self.config_base[i] == 'Subnet Prefix':
                self.subnet = self.config_keys[i]
                break
            else:
                pass

    def get_mask(self):
        for i in range(self.config_base.__len__()):
            if self.config_base[i] == 'Mask':
                self.mask = self.config_keys[i]
                break
            else:
                pass

    def get_def_gateway(self):
        for i in range(self.config_base.__len__()):
            if self.config_base[i] == 'Default Gateway':
                self.def_gateway = self.config_keys[i]
                break
            else:
                pass

    def get_mac(self):
        if self.name.lower().find("loopback") == -1:
            for i in range(self.macbase.__len__()):
                if self.macbase[i] == 'Physical Address':
                    self.mac = self.mackeys[i]
                    break
                else:
                    pass
        else:
            pass

    def get_desc(self):
        if self.name.lower().find("loopback") == -1:
            for i in range(self.macbase.__len__()):
                if self.macbase[i] == 'Network Adapter':
                    self.desc = self.mackeys[i]
                    break
                else:
                    pass
        else:
            pass

    def stworz_ui(self):
        self.ui.setWindowTitle(f"Interface: {self.name}")
        self.ui.resize(500, 600)
        self.ui.setLayout(self.form_layout)
        for k in range(self.nazwy_danych_o_interfejsach.__len__()):
            label = QtWidgets.QLabel(parent=self.ui, text=f"{self.dane_o_interfejsie[k]}")
            label.setFrameShape(QtWidgets.QFrame.Shape(1))
            label.setFrameShadow(QtWidgets.QFrame.Shadow(1))
            label.setMargin(2)
            label.setFont(QtGui.QFont("Arial", 9))
            if self.dane_o_interfejsie[k] == "connected   ":
                label.setStyleSheet("background-color:#0C0;color:black")
            elif self.dane_o_interfejsie[k] == "disconnected":
                label.setStyleSheet("background-color:#C00;color:black")
            else:
                label.setStyleSheet("background-color:#222;color:white")
            self.labels.append(label)
        for j in range(self.nazwy_danych_o_interfejsach.__len__()):
            self.form_layout.addRow(self.nazwy_danych_o_interfejsach[j], self.labels[j])
        for j in range(self.config_keys.__len__()):
            if self.config_base[j] == "InterfaceMetric":
                pass
            elif j < 5 and self.name.lower().find("loopback") == -1:
                lineedit = QtWidgets.QLineEdit(self.config_keys[j])
                lineedit.setFont(QtGui.QFont("Arial", 9))
                lineedit.setTextMargins(2, 2, 2, 2)
                lineedit.setStyleSheet("background-color:#222;color:white")
                self.labels.append(lineedit)
                self.form_layout.addRow(str(self.config_base[j]), lineedit)
            else:
                label1 = QtWidgets.QLabel(self.config_keys[j])
                label1.setFrameShape(QtWidgets.QFrame.Shape(1))
                label1.setFrameShadow(QtWidgets.QFrame.Shadow(1))
                label1.setMargin(2)
                label1.setFont(QtGui.QFont("Arial", 9))
                label1.setStyleSheet("background-color:#222;color:white")
                self.labels.append(label1)
                self.form_layout.addRow(str(self.config_base[j]), label1)
        try:
            for j in range(1, self.macbase.__len__()):
                print(self.mackeys[j])
                label1 = QtWidgets.QLabel(self.mackeys[j])
                label1.setFrameShape(QtWidgets.QFrame.Shape(1))
                label1.setFrameShadow(QtWidgets.QFrame.Shadow(1))
                label1.setMargin(2)
                label1.setFont(QtGui.QFont("Arial", 9))
                label1.setStyleSheet("background-color:#222;color:white")
                self.labels.append(label1)
                self.form_layout.addRow(str(self.macbase[j]), label1)
        except IndexError:
            pass
        if self.name.lower().find("loopback") != -1:
            pass
        else:
            self.hlayout.addWidget(self.save_btn)
            self.hlayout.addWidget(self.restore_btn)
            self.hlayout.addWidget(self.change_btn)
            self.restore_btn.setEnabled(False)
            self.form_layout.addRow('', self.hlayout)
            self.save_btn.clicked.connect(self.zapisz_stan)
            self.restore_btn.clicked.connect(self.wczytaj_stan)
            self.change_btn.clicked.connect(self.zmien_ustawienia)
        self.ui.show()

    def zapisz_stan(self):
        if self.dhcp:
            command = f'cmd /c echo netsh interface ipv4 set address "{self.name}" source=dhcp > ' \
                      f'{self.name}_interface_save_dynamic.cmd'
        else:
            command = f'cmd /c echo netsh interface ipv4 set address "{self.name}" static {self.ipaddress} {self.mask} ' \
                      f'> {self.name}_interface_save_static.cmd'
        call = subprocess.call(command, stdout=open(os.devnull, 'wb'))
        if call == 0:
            print(f"Zapisano ustawienia {self.name}")
            self.zapisano_stan = True
            self.restore_btn.setEnabled(True)
            return True
        else:
           return False

    def zmien_ustawienia(self):
        for i in self.labels:
            if str(type(i)).find('PyQt5.QtWidgets.QLineEdit') != -1:
                if str(i.text).find("Yes") == -1:
                    command = f'cmd /c netsh interface ipv4 set address "{self.name}" static' \
                              f' {self.ipaddress} {self.mask} '
                else:
                    command = f'cmd /c netsh interface ipv4 set address "{self.name}" dhcp'
                break
        call = subprocess.call(command, stdout=open(os.devnull, 'wb'))
        if call == 0:
            print(f"Zmieniono ustawienia {self.name}")
            return True
        else:
            print(f"Nie zmieniono ustawien (admin persmissnion needed): {self.name}")
            return False

    def wczytaj_stan(self):
        if self.dhcp_first:
            command = f'cmd /c start {self.name}_interface_save_dynamic.cmd'
        else:
            command = f'cmd /c start {self.name}_interface_save_static.cmd'
        call = subprocess.call(command, stdout=open(os.devnull, 'wb'))
        if call == 0:
            print(f"Wczytano ustawienia {self.name}")
            self.zapisano_stan = False
            return True
        else:
            return False

    def odczytaj_mac_i_opis(self):
        mackeys = []
        from subprocess import Popen, PIPE
        p = Popen(f"cmd /c getmac /v /FO csv", stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate(b"stdin")
        out_str = str(output)
        out_str = out_str[2:-5]
        linie = out_str.split('\\r\\n')
        for s in range(1, linie.__len__()):
            dane = linie[s].split(',')
            for d in range(dane.__len__()):
                if dane[0][1:-1] == self.name:
                    mackeys.append(dane[d][1:-1])
        self.mackeys = mackeys



def generuj_plik_interfesow():
    call = subprocess.call("cmd /c ipconfig /all > interfejsy.ini", stdout=open(os.devnull, 'wb'))
    if call == 0:
        return True
    else:
        return False


def odczytaj_windows_configuration_z_pliku():
    windowsconfig_geted = True
    windowsconfigkeys = []
    windowsconfigbase = []
    plik = open('interfejsy.ini', 'r', encoding='latin-1') # ogarnij kodowanie znaków
    for line in plik.readlines():
        line = line.replace(' .', '')
        line = line.replace(' : ', ':')
        line = line.replace('.:', ':')
        if windowsconfig_geted:
            if line.find(':') != -1:
                if line.find("Ethernet") != -1:
                    windowsconfig_geted = False
                else:
                    windowsconfigkeys.append(line[3:line.find(':')])
                    windowsconfigbase.append(line[line.find(':')+1:-1])
        else:
            windowsipconfig = WindowsInterfacesConfi(windowsconfigkeys, windowsconfigbase)
            return windowsipconfig


def odczyt_bezposrednio_windows_configuration():
    windowsconfigkeys = []
    windowsconfigbase = []
    from subprocess import Popen, PIPE
    p = Popen(f"cmd /c ipconfig /all", stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate(b"stdin")
    # rc = p.returncode
    out_str = str(output)
    # ===================
    out_str = out_str.replace('\\r\\n', '')
    out_str = out_str.replace('b\'', '')
    out_str = out_str.replace(' .', '')
    out_str = out_str.replace(out_str[out_str.find('Ethernet'):], '')
    out_str = out_str.replace(' : ', ':')
    out_str = out_str.replace('.:', ':')
    out_str = out_str.replace('  ', '\\n')
    out_str = out_str.replace(out_str[0:out_str.find('\\n')+2], '')
    # ===================
    lista = out_str.split("\\n")
    for i in lista:
        windowsconfigkeys.append(i[0:i.find(':')])
        windowsconfigbase.append(i[i.find(':')+1:])
    windowsconfiguration = WindowsInterfacesConfi(windowsconfigkeys, windowsconfigbase)
    return windowsconfiguration


def odczytaj_nazwy_interfejsow():
    dane_o_interfejsie = []
    interfejsy = []
    from subprocess import Popen, PIPE
    p = Popen(f"cmd /c netsh interface ipv4 show interfaces", stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate(b"stdin")
    # rc = p.returncode
    # ===================
    out_str = str(output)
    out_str = out_str[6:]
    out_str = out_str[:-9]
    # ===================
    lista = out_str.split('\\r\\n')
    wyznacznik = lista[1]
    dlugosci = []
    lista_wyznacznika = wyznacznik.split(' ')

    for i in lista_wyznacznika:
        if i.__len__() != 0:
            dlugosci.append(i.__len__())

    for j in range(2, lista.__len__()):
        dane_o_interfejsie.append(int(str(lista[j])[:dlugosci[0]]))
        dane_o_interfejsie.append(int(str(lista[j])[dlugosci[0]+1:dlugosci[0]+1+dlugosci[1]+1]))
        dane_o_interfejsie.append(int(str(lista[j])[dlugosci[0]+1+dlugosci[1]+1:dlugosci[0]
                                                                                +1+dlugosci[1]+1+dlugosci[2]+2]))
        dane_o_interfejsie.append(str(lista[j][dlugosci[0]+1+dlugosci[1]+1+dlugosci[2]+4:dlugosci[0]
                                                                                         +1+dlugosci[1]
                                                                                         +1+dlugosci[2]
                                                                                         +4+dlugosci[3]]))
        dane_o_interfejsie.append(str(lista[j][dlugosci[0]+1+dlugosci[1]+1+dlugosci[2]+4+dlugosci[3]+2:]))
        interfejs = Interfaces(dane_o_interfejsie)
        interfejsy.append(interfejs)
        dane_o_interfejsie = []
    return interfejsy


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # generuj_plik_interfesow()
    w = odczyt_bezposrednio_windows_configuration()
    w.windowsconfig_all()
    w.stworz_ui()
    i = odczytaj_nazwy_interfejsow()
    for n in i:
        print('')
        print(n.name)
        print(n.dhcp)
        print(n.ipaddress)
        print(n.mask)
        print(n.def_gateway)
        print(n.subnet)
        n.stworz_ui()
    sys.exit(app.exec_())

