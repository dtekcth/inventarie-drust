#!/usr/bin/env python3

import json
import time
import cmd

def main():
    InventarieShell().cmdloop()

###################
# Main class
###################

class InventarieShell(cmd.Cmd):
    intro = 'Inventariesystem.   Type help or ? to list commands.\n'
    prompt = 'λ '
    doc_header = "Alla kommandon (Se \"help <kommando>\" för hjälp)"
    undoc_header = "Kortkommandon för avancerade användare"
    ruler = "="
    inventoryFile = None
    userFile = None
    transactionFile = None
    itemFile = None

    # Startup
    def preloop(self):
        open("inventory.json", "a").close()
        self.inventoryFile = open("inventory.json", "r+")
        self.currInventory = json.load(self.inventoryFile)

        open("users.json", "a").close()
        self.userFile = open("users.json", "r+")
        self.allUsers = json.load(self.userFile)

        open("transactions.json", "a").close()
        self.transactionFile = open("transactions.json", "r+")
        self.allTransactions = json.load(self.transactionFile)

        open("items.json", "a").close()
        self.itemFile = open("items.json", "r+")
        self.allItems = json.load(self.itemFile)

    # ----- commands -----
    def do_test(self, arg):
        'Test:  TEST'
        print(type(arg))

    # > lånaut
    # Vad ska lånas ut?
    # > skanna
    # Skanna fler saker eller skriv q för att vara klar
    # > skanna
    # Skanna fler saker eller skriv q för att vara klar
    # > q
    # Vem lånar du ut till?
    # > skanna/skriv
    # Lån registrerat
    def do_lanaut(self, arg):
        'Låna ut verktyg: (L)anaut'
        print("Vad ska lånas ut?")
        barcode = input("λ ")
        tools = {}
        while barcode != "q" and barcode != "quit":
            if barcode not in self.allItems:
                print("Verktyg finns inte, skapa nu?")
                if input("Y/N? ").lower() == "y":
                    self.do_skapaverktyg(barcode)
                else:
                    print("Verktyg skapades inte, avbryter utlåning.")
                    return
            print(self.allItems[barcode]["description"])
            tools.setdefault(barcode, 0)
            if int(self.currInventory[barcode]) < 1:
                print("Detta ska inte finnas i förrådet, något är fel.")
                print("Fortsätt ändå?")
                if input("Y/N? ").lower() == "n":
                    return
            tools[barcode] = int(tools[barcode]) - 1
            print("Skanna fler saker eller skriv q för att gå vidare")
            barcode = input("λ ")
        print("Vem lånar du ut till?")
        user = input("λ ")
        if user not in self.allUsers:
            print("Användare finns inte, skapa nu?")
            if input("Y/N? ").lower() == "y":
                self.do_skapaanvandare(user)
            else:
                print("Användare skapades inte, avbryter utlåning.")
                return
        print(self.allUsers[user])
        self.addTransaction(tools, user)
        print("Verktyg utlånade")

    # > lamnain
    # Vad lämnas tillbaka?
    # > skanna
    # Skanna fler saker eller skriv q för att vara klar
    # > skanna
    # Skanna fler saker eller skriv q för att vara klar
    # > q
    # Vem lämnar tillbaka?
    # > skanna
    # Verktyg tillbakalämnade
    def do_lamnain(self, arg):
        "Lämna tillbaka verktyg: lamna(I)n"
        print("Vad ska lämnas tillbaka?")
        barcode = input("λ ")
        tools = {}
        while barcode != "q" and barcode != "quit":
            print(self.allItems[barcode]["description"] + " ska finnas på hylla" + self.allItems[barcode]["place"])
            tools.setdefault(barcode, 0)
            tools[barcode] += 1
            print("Skanna fler saker eller skriv q för gå vidare")
            barcode = input("λ ")
        print("Vem lämnar tillbaka?")
        user = input("λ ")
        if user not in self.allUsers:
            print("Användare finns inte, skapa en ny?")
            if input("Y/N? ").lower() == "y":
                self.do_skapaanvandare(user)
            else:
                print("Användare skapades inte, avbryter utlåning.")
                return
        print(self.allUsers[user])
        self.addTransaction(tools, user)
        print("Verktyg tillbakalämnade")

            
    # > skapaanvandare
    # Vad heter personen?
    # > Erik
    # Vad är personens unika streckkod?
    # > skanna
    # Användare skapad
    def do_skapaanvandare(self, arg):
        "Skapa en användare:  skapa(A)nvandare"
        print("Vad heter personen?")
        name = input("λ ")
        if arg == "":
            print("Vad är personens streckkod?")
            barcode = input("λ ")
            self.addUser(name, barcode)
        else: 
            self.addUser(name, arg)
        print("Användare skapad")

    # > skapaverktyg
    # Vad är det för grej?
    # > En grön sax
    # Hur många vill du lägga till?
    # > 2
    # Vad har den för streckkod?
    # > skanna
    # Verktyg inlagt
    def do_skapaverktyg(self, arg):
        "Lägg in ett nytt verktyg:  (S)kapaverktyg"
        print("Vad är det för verktyg?")
        name = input("λ ")
        print("Hur många vill du lägga till?")
        amount = input("λ ")
        print("Var finns " + name + "?")
        place = input("λ ")
        if arg == "":
            print("Vad har den för streckkod?")
            barcode = input("λ ")
            self.addItem(name, barcode, amount, place)
        else: 
            self.addItem(name, arg, amount, place) 
        print("Verktyg inlagt")

    def do_utlanat(self, arg):
        "Se allt utlånat just nu:  (U)tlanat"
        print("Utlånat just nu:")
        state = {}
        for (t, a) in [list(t["tools"].items())[0] for t in self.allTransactions]:
            state.setdefault(t, 0)
            state[t] -= a
        for (t, a) in state.items():
            print(self.allItems[t]["description"] + " - " + str(a) + " st")

    def do_forrad(self, arg):
        "Se vad som ska vara i förrådet just nu:  (F)orrad\nAnvänd alternativ -a för att se alla saker, även de med 0 balans."
        for t in [t for t in self.currInventory.items() if "-a" in arg or t[1] != 0]:
            print(self.allItems[t[0]]["description"] + " - " + str(t[1]) + " st")

    def do_anvandarinfo(self, arg):
        "Se info om en användare:  (A)nvandarinfo\nAnvänd kommandot (U)tlanat för att se vad en person har utlånat just nu."
        print("Vilken användare vill du se info om?")
        user = input("λ ")
        if user not in self.allUsers:
            print("Användaren finns inte")
            return
        print("Namn: " + self.allUsers[user])
        print("Allt utlånat till: " + self.allUsers[user])
        state = {}
        for (tool, amount) in [list(t["tools"].items())[0] for t in self.allTransactions if t["user"] == user]:
            state.setdefault(tool, 0)
            state[tool] -= amount
        for d in [d for d in list(state.items()) if d[1] != 0]:
            print(self.allItems[d[0]]["description"] + " - " + str(d[1]) + " st")

    def do_verktygsinfo(self, arg):
        "Se info om ett verktyg:  (V)erktygsinfo"
        print("Vilket verktyg vill du se info om?")
        tool = input("λ ")
        print(self.allItems[tool]["description"] + " - " + str(self.currInventory[tool]) + " inne just nu")
        print("Finns på hylla " + self.allItems[tool]["place"])
        currMax = ("", 0)
        for (u, d) in [(t["user"], t["date"]) for t in self.allTransactions]:
            if d > currMax[1]:
                currMax = (u, d)
        print("Lånades senast av " + self.allUsers[u])

    def do_quit(self, arg):
        'Exit the program:  (Q)uit'
        print('Stänger ner...')
        self.closeAllFiles()
        return True

    # aliases
    def do_l(self, arg):
        return self.do_lanaut(arg)
    def do_q(self, arg):
        return self.do_quit(arg)
    def do_u(self, arg):
        return self.do_utlanat(arg)
    def do_f(self, arg):
        return self.do_forrad(arg)
    def do_h(self, arg):
        self.onecmd("help")
    def do_a(self, arg):
        return self.do_anvandarinfo(arg)
    def do_v(self, arg):
        return self.do_verktygsinfo(arg)
    def do_s(self, arg):
        return self.do_skapaverktyg(arg)
    def do_i(self, arg):
        return self.do_lamnain(arg)

    # Helper functions

    def closeAllFiles(self):
        if self.inventoryFile:
            self.inventoryFile.close()
            self.inventoryFile = None
        if self.userFile:
            self.userFile.close()
            self.userFile = None
        if self.transactionFile:
            self.transactionFile.close()
            self.transactionFile = None

    def addTransaction(self, tools, user):
        "Adds a transaction to the class variable and writes that through to the file. Also updates the current inventory."
        self.allTransactions.append({"tools": tools, "user": user, "date": time.time()})
        self.emptyFile(self.transactionFile)
        self.writeJson(self.allTransactions, self.transactionFile)
        for tool, amount in tools.items():
            if tool not in self.allItems:
                print("Verktyg " + self.allItems[tool]["description"] + " finns inte, skapa det nu?")
                if input("Y/N? ").lower() == "y":
                    self.do_skapaverktyg(tool)
                else:
                    print("Verktyg skapades inte, avbryter utlåning.")
                    return
            self.currInventory[tool] = int(self.currInventory[tool]) + int(amount)
            
        self.emptyFile(self.inventoryFile)
        self.writeJson(self.currInventory, self.inventoryFile)
        self.inventoryFile.flush()       

    def addUser(self, name, barcode):
        "Adds a user to the class variable and writes that through to the file."
        self.allUsers[barcode] = name
        self.emptyFile(self.userFile)
        self.writeJson(self.allUsers, self.userFile)

    def addItem(self, desc, barcode, amount, place):
        "Adds a user to the class variable and writes that through to the file. Also updates inventory."
        self.allItems[barcode] = {"description": desc, "place": place}
        self.emptyFile(self.itemFile)
        self.writeJson(self.allItems, self.itemFile)

        self.emptyFile(self.inventoryFile)
        self.currInventory.setdefault(barcode, 0)
        self.currInventory[barcode] = amount
        self.writeJson(self.currInventory, self.inventoryFile)

    def emptyFile(self, fp):
        fp.seek(0)
        fp.truncate()

    def writeJson(self, obj, fp):
        json.dump(obj, fp, separators=(",", ":"))
        fp.flush()

main()
