import logging
from getpass import getpass
from argparse import ArgumentParser
import slixmpp


class Client(slixmpp.ClientXMPP):


    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.jid = jid
        self.password = password
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.registration)
        self.add_event_handler("message", self.message)
        
    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        
        def Privatemessage():
            recipient = input("Nombre de usuario a quien va el mensaje: ")
            msg = input("Escriba el mensaje: ")
            self.send_message(mto=recipient, mbody=msg, mtype='chat')
            print("Se ha enviado el mensaje correctamente")
            
        def PublicRoom():
            pass
            
        def closeSesion():
            self.disconnect()
            print("Ha cerrado sesion exitosamente")
            
        def NewContact():
            pass
            
        