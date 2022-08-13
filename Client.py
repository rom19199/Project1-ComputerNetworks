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
            print("1. Enviar mensajes directos") 
            print("2. Mostrar todos los usuarios/contactos y su estado") 
            print("3. Agregar un usuario a los contactos") 
            print("4. Mostrar detalles de contacto de un usuario") 
            print("5. participar en conversaciones grupales")
            print("6. Definir mensaje de presencia") 
            print("7. Enviar/recibir notificaciones")
            print("8. Enviar/recibir archivos")
            print("9. Eliminar la cuenta del servidor") 
            print("10. Cerrar sesion") 
            print("")
            op_menu = int(input("Que opcion quieres? "))
            
       
        
    async def register(self, iq):
        self.send_presence()
        # We get our contacts
        self.get_roster()
        
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            await resp.send()
            logging.info("Account created for %s!" % self.boundjid)
        except IqError as e:
            logging.error("Could not register account: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("No response from server.")
            self.disconnect()
                        
    def Message(self, message):
        print(str(message["from"]), ":  ", message["body"])
        
def register(user, password):
    client = Client(user, password)

    client.register_plugin("xep_0030")
    client.register_plugin("xep_0004")
    client.register_plugin("xep_0199")
    client.register_plugin("xep_0066")
    client.register_plugin("xep_0077")
    client["xep_0077"].force_registration = True
    client.connect()
    client.process()
    
loop = True
while loop:
    print("""
            \r-------------------------------
            \r1. Sign Up
            \r2. Log In
            \r3. Exit
            \r-------------------------------

        """)
    option = int(input("Choose an option to continue: "))
    if option == 1:
        user = input("Username: ")
        password = input("Password: ")
        register(user, password)

    elif option == 2:
        user = input("Username: ")
        password = input("Password: ")
        #login(user, password)
        
    elif option == 3:
        loop = False
    else:
        print("Invalid option")