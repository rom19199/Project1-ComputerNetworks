import logging
from getpass import getpass
from argparse import ArgumentParser
import slixmpp 
from slixmpp.exceptions import IqError, IqTimeout

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")


class Client(slixmpp.ClientXMPP):


    def __init__(self, user, password):
        slixmpp.ClientXMPP.__init__(self, user, password)
        self.user = user
        self.password = password
        self.add_event_handler("session_start", self.Start)
        self.add_event_handler("register", self.register)
        self.add_event_handler("message", self.Message)
        
    async def Start(self, event):
        
        self.send_presence() 
        await self.get_roster()
        
        #Show all users
        def AllUsers():
            print('------ Lista de Contactos ------')
            print()
            contacts = self.client_roster.groups()
            for contact in contacts:
                print(contact)
                for jid in contacts[contact]:
                    name = self.client_roster[jid]['name']
                    if self.client_roster[jid]['name']:
                        print('\n', name, ' (',jid,')')
                    else:
                        print('\n', jid)

                    connections = self.client_roster.presence(jid)
                    for res, pres in connections.items():
                        show = 'available'
                        if pres['show']:
                            show = pres['show']
                        print('   - ',res, '(',show,')')
                        if pres['status']:
                            print('       ', pres['status'])
                            
        def AddUsers():
            new_user = input("Ingrese nuevo usuario: ")
            self.send_presence_subscription(pto=new_user)
            print("---- Agregado exitosamente ----")
            
            
        def user_info():
            self.get_roster()
            usuario = input("Ingrese el usuario: ")
            name = self.client_roster[usuario]['name']
            print('\n %s (%s)' % (name, usuario))

            usuarios = self.client_roster.presence(usuario)
            for res, pres in usuarios.items():
                show = 'chat'
                if pres['show']:
                    show = pres['show']
                print("     INFO:")
                print('   - ', res, ' - ', show)
                print('        ', show)
                print('     Estado: ', pres['status'])
            
        
        def Privatemessage():
            self.register_plugin("xep_0085")
            recipient = input("Usuario destinatario: ")
            msg = input("Escriba el mensaje: ")
            self.send_message(mto=recipient, mbody=msg, mtype='chat')
            #notification(recipient, "paused")
            print("Se ha enviado el mensaje correctamente") 
            
        def Groupmessage():
            self.register_plugin('xep_0030')
            self.register_plugin('xep_0045') #Implements XEP-0045 Multi-User Chat
            self.register_plugin('xep_0199')

            room = input("Nombre de la sala: ")
            nickname = input("Nickname: ")
            message = input('Mensaje: ')
            self.plugin['xep_0045'].join_muc(room+"@conference.alumchat.fun", nickname)
            self.send_message(mto=room+"@room.alumchat.fun", mbody=message, mtype='groupchat')
            
        def state():
            estado = input("Indica el estado que desees (chat, desconectado): ")
            informacion = input("Indica la informacion a mostar: (ej.: disponible, ocupado): ")
            self.send_presence(pshow=informacion, pstatus=estado)

    
        def notification(to, state):
            self.register_plugin("xep_0085")
            message = self.Message()
            message["state"] = state
            message["to"] = to
            message.send()
            
        def closeSesion():
            self.disconnect()
            loginloop = False
            print("Ha cerrado sesion exitosamente")
            
        def delete():
            self.register_plugin('xep_0030') 
            self.register_plugin('xep_0004')
            self.register_plugin('xep_0077')
            self.register_plugin('xep_0199')
            self.register_plugin('xep_0066')

            eliminar = self.Iq()
            eliminar['type'] = 'set'
            eliminar['from'] = self.boundjid.user
            eliminar['register']['remove'] = True
            eliminar.send()
            print("Cuenta eliminada")
            self.disconnect()
            
        menu = True
        while menu:
            print("1. Show contacts") 
            print("2. Add user") 
            print("3. Show contact details of a user") 
            print("4. Private message") 
            print("5. Chat room")
            print("6. Status") 
            print("7. Files")
            print("8. Log out") 
            print("9. Delete account") 
            print("------")
            
            options = int(input("Elige una opcion: "))
            
            if options == 1:
                AllUsers()
            elif options == 2:
                AddUsers()
            elif options == 3:
                user_info()
            elif options == 4:
                Privatemessage()  
            elif options == 5:
                Groupmessage()
            elif options == 6:
                state()
            elif options == 7:
                print("faltante")
                #await self.upload_fileee()
            elif options == 8:
                closeSesion()
            elif options == 9:
                delete()
                
            else:
                print("Opcion invalida")

            await self.get_roster()
            
            
    