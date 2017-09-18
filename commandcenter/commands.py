from models import SiteUsers
from yellowant.messageformat import MessageClass, MessageAttachmentsClass, MessageButtonsClass, AttachmentFieldsClass
import datetime

class AppCommands(object):
    def __init__(self, function, user_integration, args, invoke_name):
        self.function = function
        self.user_integration = user_integration
        self.args = args
        self.invoke_name = invoke_name

    #A method that generates a generic YellowAnt message object
    def generate_simple_message(self, message_text=""):
        message = MessageClass()
        message.message_text = message_text
        return message.to_json()

    #Command parser method
    def parse(self):
        commands = {
            'list-users-today': self.list_users_today,
            'get-users': self.get_users,
            'get-user-details': self.get_user_details
        }


        if str(self.invoke_name) in commands:
            return commands[str(self.invoke_name)](self.args)
        else:
            message = MessageClass()
            message.message_text = "I could not find any command"
            return message.to_json()

    #Lists the details of the user
    def list_user_details(self, args):
        if 'id' not in args:
            return self.generate_simple_message("Please provide parameter 'id' in your command")
        else:
            #Check if Id is a number
            if args['id'].is_digit():
                user_id = int(args['id'])
            else:
                return self.generate_simple_message("Please provide an integer value for parameter 'id' in your command")

        try:
            #Searching for user with id
            user_object = SiteUsers.objects.get(id=user_id)
        except SiteUsers.DoesNotExist:
            #return error message if user does not exist
            return self.generate_simple_message("User with that id does not exist")

        user_details_message = MessageClass()
        user_details_message.message_text = "User Id - %d, Fullname - %s, Date joined - %s, Subscription - %s" % (user_id, user_object.full_name, user_object.date_joined, user_object.subscription)

        return user_details_message.to_json()

    #Lists the users that signed up in the last 24 hours
    def list_users_today(self, args):
        #Check if 'sort' param is present, else assign default as 'asc'
        if 'sort' in args:
            if args['sort'] in ['asc', 'dsc']:
                order = args['sort']
            else:
                #If invalid, fallback to default value
                order = 'asc'
        else:
            #setting default order 'asc'
            order = 'asc'

        if 'subscription' in args:
            subscription = args['subscription']
        else:
            subscription = None

        #Instantiate a Message Object
        message = MessageClass()
        message.message_text = ""

        #Create list to store the results
        users_list = []

        d_24 = datetime.datetime.now() - datetime.timedelta(days=1)
        if subscription is None:
            users_today = SiteUsers.objects.filter(date_joined__gte=d_24)
        else:
            users_today = SiteUsers.objects.filter(date_joined__gte=d_24, subscription=subscription)

        for user in users_today:
            message.message_text += user.id+"\t"+user.full_name+"\t"+user.date_joined

        return message.to_json()