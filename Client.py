#Imports
import logging
from argparse import ArgumentParser
import slixmpp 
from slixmpp.exceptions import IqError, IqTimeout
from aioconsole import ainput


logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")

#Main class
class Client(slixmpp.ClientXMPP):

    #Init app
    def __init__(self, user, password):
        slixmpp.ClientXMPP.__init__(self, user, password)
        self.user = user
        self.password = password
        self.add_event_handler("session_start", self.Start)
        self.add_event_handler("register", self.register)
        self.add_event_handler("message", self.Messageto)
        
    async def Start(self, event):
        
        #Presence
        self.send_presence() 
        
        #List of contacts
        await self.get_roster()
        
        #Notifications
        def notification(to, state):
            self.register_plugin("xep_0085")
            message = self.Message()
            message["state"] = state
            message["to"] = to
            message.send()
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
                  
        #AddUsers          
        def AddUsers():
            new_user = input("Ingrese nuevo usuario: ")
            self.send_presence_subscription(pto=new_user)
            message="Hi new friend!"
            self.send_message(mto=new_user, mbody=message, mtype="chat", mfrom=self.boundjid.bare)
            print("---- Agregado exitosamente ----")
            
        #Show user info
        def user_info():
            self.get_roster()

            contact_user = input("Contact username: ")

            name = self.client_roster[contact_user]['name']
            print('\n %s (%s)' % (name, contact_user))

            connections = self.client_roster.presence(contact_user)

            if connections == {}:
                print("           xa")
                print("    No recent session")
    
            for res, pres in connections.items():
                show = 'available'
                if pres['show']:
                    show = pres['show']
                print('   - ', res, ' - ', show)
                print('       ',  pres['status'])
            
        #Send message
        async def Privatemessage():
            self.register_plugin("xep_0085")

            recipient = str(await ainput("Recipient: "))
            notification(recipient, "composing")
            message = str(await ainput("Message: "))

            self.send_message(mto=recipient, mbody=message, mtype="chat")
            notification(recipient, "paused")
            print("Message sent!")
            
        #Receive message
        async def Groupmessage():
            #self.register_plugin('xep_0030')
            self.register_plugin('xep_0045') #Implements XEP-0045 Multi-User Chat
            #self.register_plugin('xep_0199')

            room = str(await ainput("Nombre de la sala: "))
            nickname = input("Nickname: ")
            message = input('Mensaje: ')
            self.plugin['xep_0045'].join_muc(room, nickname)
            self.send_message(mto=room, mbody=message, mtype='groupchat')
            
        #Show state
        def state():
            estado = input("Indica el estado que desees (chat, desconectado): ")
            informacion = input("Indica la informacion a mostar: (ej.: disponible, ocupado): ")
            self.send_presence(pshow=informacion, pstatus=estado)

    
        
        #Close sesion  
        def closeSesion():
            self.disconnect()
           
            print("Ha cerrado sesion exitosamente")
         
        #delete   
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
            print("7. Notification")
            print("8. Log out") 
            print("9. Delete account") 
            
           
            
            options = int(input("Elige una opcion: "))
            
            if options == 1:
                AllUsers()
            elif options == 2:
                AddUsers()
            elif options == 3:
                user_info()
            elif options == 4:
                await Privatemessage()  
            elif options == 5:
                await Groupmessage()
            elif options == 6:
                state()
            elif options == 7:
                print("opcion no disponible")
                #await self.upload_fileee()
            elif options == 8:
                closeSesion()
                menu = False
            elif options == 9:
                delete()
                
            else:
                print("Opcion invalida")

            await self.get_roster()
            
            
    async def register(self, iq):
        self.send_presence()
        self.get_roster()
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            await resp.send()
            print("Se ha creado una cuenta")
        except:
            print("no se ha podido conectar")
            self.disconnect()
            
        
            
    def Messageto(self, message):
        print(str(message["from"]), ":  ", message["body"])

    async def send_file(self):
        recipient = input("A quien va dirigido: ")
        filename = input("Archivo: ")

        logging.info('Uploading file %s...', filename)
        try:
            url = await self['xep_0363'].upload_file(filename, domain=None, timeout=10)
        except IqTimeout:
            raise TimeoutError('Could not send message in time')
        except IqError as e:
            print(e)

        logging.info('Upload success!')
        logging.info('Sending file to %s', recipient)

        message = self.make_message(mto=recipient, mbody=url)
        message.send()
        
    
def signup(username, password):
    
    
    xmpp = Client(username, password)

    xmpp.register_plugin("xep_0030")
    xmpp.register_plugin("xep_0004")
    xmpp.register_plugin("xep_0199")
    xmpp.register_plugin("xep_0066")
    xmpp.register_plugin("xep_0045")
    xmpp.register_plugin("xep_0085")
    xmpp.register_plugin("xep_0096")
    xmpp.register_plugin("xep_0059")
    xmpp.register_plugin("xep_0060")
    xmpp.register_plugin("xep_0071")
    xmpp.register_plugin("xep_0128")
    xmpp.register_plugin("xep_0363")


    #xmpp["xep_0077"].force_registration = True

    xmpp.connect()
    xmpp.process()

def login(username, password):
    xmpp = Client(username, password)
    xmpp.register_plugin("xep_0030")
    xmpp.register_plugin("xep_0199")
    xmpp.register_plugin('xep_0363')
    xmpp.connect()
    xmpp.process(forever=False)


Menu2 = True
while Menu2:
    print("""
            \r1 Sign Up
            \r2 Log In
            \r3 Exit    
        """)
    opcion = int(input("Eliga una opcion: "))
    
    if opcion == 1:
        user = input("Username: ")
        password = input("Password: ")
        signup(user, password)

    elif opcion == 2:
        user = input("Username: ")
        password = input("Password: ")
        login(user, password)
        
    elif opcion == 3:
        Menu2 = False
    else:
        print("Opcion Invalida")