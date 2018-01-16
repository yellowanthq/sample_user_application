from models import SiteUsers
from yellowant.messageformat import MessageClass, MessageAttachmentsClass, MessageButtonsClass, AttachmentFieldsClass
import datetime
from django.core import serializers



class appCommands(object):
    def __init__(self, function, service_application, args, invoke_name):
        self.function = function
        self.service_application = service_application
        self.args = args
        self.invoke_name = invoke_name

    #Simple message generator
    def generate_simple_message(self, message_text=""):
        message = MessageClass()
        message.message_text = message_text
        return message.to_json()

    #Message parser
    def parse(self):
        commands = {
            'list-users-today': self.list_users_today,
            'get-users': self.get_users,
            'change_user_subcription':self.change_user_subcription,
            'get_user_details': self.get_user_details
        }

        #loop through commands, call the appropriate function with args from yellowant
        if str(self.invoke_name) in commands:
            return commands[str(self.invoke_name)](self.args)
        else:
            message = MessageClass()
            message.message_text = "I could not find any command"
            return message.to_json()

    #'list_user_details' function. Takes 'id'(user Id), required
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
        user_json = serializers.serialize("json", user_object)
        #Adding JSON data to message for use in workflows
        user_details_message.data = user_json
        return user_details_message.to_json()

    #'change_user_subcription' function. Takes 'id'(user Id) and 'subscription' as args, both required
    def change_user_subcription(self, args):
        if 'id' not in args or 'subscription' not in args:
            return self.generate_simple_message("Please provide parameter 'id' and 'subscription' in your command")
        else:
            #Check if Id is a number
            if args['id'].is_digit():
                user_id = int(args['id'])
            else:
                return self.generate_simple_message("Please provide an integer value for parameter 'id' in your command")

        try:
            #Searching for user with id
            user_object = SiteUsers.objects.get(id=user_id)
            #changing subscription value
            user_object.subscription = args['subscription']
        except SiteUsers.DoesNotExist:
            #return error message if user does not exist
            return self.generate_simple_message("User with that id does not exist")


        user_details_message = MessageClass()
        user_details_message.message_text = "User subscription changed"
        user_json = serializers.serialize("json", user_object)
        #Adding JSON data to message for use in workflows
        user_details_message.data = user_json
        return user_details_message.to_json()

    #'list_users_today' function. Takes 'sort' or 'subscription' as args, both optional
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

        #Creating User attachments with information of users with a button to fetch user details using the "list_user_details" command
        for user in users_today:
            user_attachment = MessageAttachmentsClass()
            user_attachment.title = user.full_name

            #Showing user data in a "Field"
            date_field = AttachmentFieldsClass()
            date_field.title = "Date Joined"
            date_field.value = user.date_joined
            date_field.short = 1 #Utilize two columns
            user_attachment.attach_field(date_field)

            #Adding a button which calls the "list_user_details" command
            get_user_details_button = MessageButtonsClass()
            get_user_details_button.value = "1" #Give some random value
            get_user_details_button.name = "1" #Give some random value
            get_user_details_button.text =  "Get user details"
            #Encoding command in button
            get_user_details_button.command = {
                "function_name": "list_user_details", "service_application": self.service_application,
                "data": {"id": user.id}
            }
            user_attachment.attach_button(get_user_details_button)

            #Adding a button which provides with a dialog to change the subscription for the user using "change_user_subcription" function
            change_user_sub_button = MessageButtonsClass()
            change_user_sub_button.value = "1" #Give some random value
            change_user_sub_button.name = "1" #Give some random value
            change_user_sub_button.text =  "Change subscription"
            #Encoding command in button
            change_user_sub_button.command = {
                "function_name": "change_user_subcription", "service_application": self.service_application,
                "data": {"id": user.id}, "inputs":['subscription']
            }
            user_attachment.attach_button(change_user_sub_button)

            #Add attachment to message
            message.attach(user_attachment)

        #Adding users data to be used in workflows
        message.data = {"users":serializers.serialize("json", users_today)}
        return message.to_json()