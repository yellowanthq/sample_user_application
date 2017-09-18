### Sample YellowAnt application in Django

# Building a simple application with YellowAnt and Python for Slack

YellowAnt makes it insanely easy to convert your internal services into command
line applications which you can use within Slack and even create workflows by
“piping” your application with other applications. In this post we’ll show you
how you can setup a YellowAnt application in minutes. The following is an
example of a simple **User** application which will allow your team to query
information about the users of a your website that is built with Python(Django),
through YellowAnt(@yellowant) and Slack.

Project Repo —
[https://github.com/yellowanthq/sample_user_application](https://github.com/yellowanthq/sample_user_application)

### Steps

1.  Declare an Application in the YellowAnt Developer console
1.  Declare the application’s commands/functions
1.  For each application function, declare its arguments/inputs, their datatypes and
default values
1.  Create backend code to authenticate the user(your team members), handle the
command/input data, and respond to the command

### **Step 1: Create an application**

Head over to <your-team-domain>.yellowant.com/developers/ or click on
“Developers” in the top right corner of your Console screen.

![](https://cdn-images-1.medium.com/max/800/1*AoW4awYgGYo-zxBmP2gOZg.png)

![](https://cdn-images-1.medium.com/max/600/1*R6j39KS1gyUdMBWb1iVtcw.png)

Click on “Create new App”. Give a name and invoke name for your application.

![](https://cdn-images-1.medium.com/max/600/1*r_0lwN8oTbfBD92vE324ag.png)

We’ll go with “Users” and “users” respectively. Every command that is created
for this application will now start with **users**. Click on “Create App” to
register the User application.

**Authentication — **Unlike Hubot, Lita, Errbot etc. every YellowAnt user needs
to separately authenticate with every application. This creates a unique
user-application ‘id’ which helps the application identify the user that is
accessing the application command. The authentication is done via OAuth2. By
default the following are created when a new application is created:

a) **client_id** — The Client ID for the application

b) **client_secret** — The client secret for the application. Must be kept
secret

c) **verification_token** — The verification token that YellowAnt sends with the
user command data, so that your server knows that the request is coming from
YellowAnt servers.

Click on “Edit app” and set the following:

a) **redirect_url** — The url to redirect the user after successful
authentication. We can set this to
[http://localhost:8000/redirect_url/](http://localhost:8000/redirect_url/). To
authenticate, the user is sent to the authentication url —
[https://www.yellowant.com/api/oauth2/authorize/?state=<some-state-value>&client_id=<](https://www.yellowant.com/api/oauth2/authorize/?client_id=YTjgMWGbZD6yNIDHxWcgV59Xp43yaEPufk9jyuL2)your-app-client-id>&response_type=code&redirect_url=<your-app-redirect-url>/.
After the user authenticates the application, YellowAnt will send the user to
this redirect_url with GET parameters “code” and “state”. You use the **state**
to identify the user and the **code **to exchange for a permanent user token.

b) **api_url** — The url to send the command data(JSON) as a POST request. We
can set this to [http://localhost:8000/apiurl/](http://localhost:8000/redirect/)

We will use all of the above in Step 4 — Server-side implementation.

Also fill out the other information like description, privacy policy url etc. We
will also be setting the “Application Visibility” to “Team”, since we want only
the team members to be able to use and authenticate with the User application.

### Step 2: Define commands/functions

Let us add the following commands:

1.  List users that signed up today with some filter parameters
1.  List users that signed up between a date-range
1.  Get user details for a particular user with ‘id’ as input

Let’s define command 1, i.e list the users that signed up today with some
filters. In the application page, click on “Add Function”.

![](https://cdn-images-1.medium.com/max/800/1*Lu3nosVc0gHrRe1uulYNNQ.png)

Give you application an invoke_name and define the command type as “Command”,
request type as “GET” and return type as “JSON” since we will be returning some
data with the message, which we will use later. Click on “Save”

![](https://cdn-images-1.medium.com/max/800/1*XxtduXasPlS7nIl8tBEw3Q.png)

### Step 3: Define the function inputs/arguments

Let’s define the arguments for the “list-users-today” command

1.  **sort** — -The order to sort the user data(possible values —**asc **or **dsc**)
default ascending(asc)
1.  **subscription** — The type of subscription (possible values — **paid **or**
free**)

![](https://cdn-images-1.medium.com/max/600/1*jYHINYia6Lt96sCnHD1RBA.png)

Click on “Add argument” to add the argument and define the name of the
argument(**sort**), data type(**varchar**) and default values(**asc**).

![](https://cdn-images-1.medium.com/max/600/1*yhbNtiUiE6fZpq2VcbgLGg.png)

Similarly, define an argument for “subscription”. Both these parameters are
optional**(not required), **and therefore the YellowAnt parser will send the
values of these argument only if they are specified in the command.

Follow step 2 and 3 for defining functions and arguments for commands 2 and 3.
And you’re done!

### **Step 4: Backend Code**

It’s time to map the commands we defined in the YellowAnt Developer console to
the backend code. But first, let’s install the YellowAnt python library to our
virtual environment. In your terminal, type the following command

    pip install yellowant —-upgrade

#### 4.1 User Authentication

After you create the User application, every user that wants to use you “User”
application must authenticate with YellowAnt with OAuth2.

![](https://cdn-images-1.medium.com/max/800/1*IU20OuDFnOsO6hWmBPhEEw.png)

The following credentials are created when a new application is created on
YellowAnt:client_id, client_secret, verification_token

You also provided the redirect_url and the api_url for the User application.

Create a button in your website that redirects the user to
[https://www.yellowant.com/api/oauth2/authorize/?client_id=YTjgMWGbZD6yNIDHxWcgV59Xp43yaEPufk9jyuL2](https://www.yellowant.com/api/oauth2/authorize/?client_id=YTjgMWGbZD6yNIDHxWcgV59Xp43yaEPufk9jyuL2)&response_type=code&redirect_url=http://localhost:8000/redirect_url/

Define your redirect_url view in Django something like below(More in details in
API docs — [here](https://yellowant.com/api/#get-user-profile)):

    def
    (request):

        #User redirected to redirect_url with GET parameter 'code'
        code = request.GET.get("code", False)
        ya_obj = YellowAnt(app_key=settings.YA_CLIENT_ID,
                        app_secret=settings.YA_CLIENT_SECRET,
                        access_token='',
                        redirect_uri=settings.YELLOWANT_REDIRECT_URL)

        #Exchanging 'code' for a permanent access token
        access_token_dict = ya_obj.get_access_token(code)
        access_token = access_token_dict['access_token']

        #Initialize YellowAnt object with access token and get profile
        yellowant_user = YellowAnt(access_token=access_token)
        user_profile = yellowant_user.get_user_profile()
        ya_user_id = user_profile['id']

        #create a user application integration
        user_integration = yellowant_user.create_user_integration()
        integration_id = user_integration['user_application']
        invoke_name = user_integration['user_invoke_name']

        #Store user_application id, along with user token
        return HttpResponse("Authenticated!")

#### **4.2 Handling user commands**

When a user sends a command YellowAnt parses the command and converts its into a
representation of application, function and arguments and sends it to the
‘api_url’ that we declared when we created the **User **application.

Lets define the view for api_url

    #When a user enters a command, YellowAnt sends the api_url a POST request with the payload that looks something like this:

    34NaaVTgWhN3QIK74WJX8i1aSoBHMNnvgThygGxi8pPZtJ9OhaIeNlApO8vWkwMV3G0ujUxzrSHZowNoIrxZqa3DnHgi5FJBugjkhws8HaN8U6KkfPo33F1pHiBniYkn

    from yellowant.messageformat import MessageClass

    def api_url(request):
        data = json.loads(request.POST.get("data", "{}"))
        command = data["function"]
        service_application = data["application"]
        args = data["args"]
        function_name = data['function_name']
        verification_token = data['verification_token']

        #check verification_token from application page
        if verification_token == "34NaaVTgWhN3QIK74WJX8i1aSoBHMNnvgThygGxi8pPZtJ9OhaIeNlApO8vWkwMV3G0ujUxzrSHZowNoIrxZqa3DnHgi5FJBugjkhws8HaN8U6KkfPo33F1pHiBniYkn":
            try:
                #send the command string to the Command Parser class

              message = AppCommands(command, service_application, args, function_name).parse()
                return HttpResponse(message)
            except CommandException, e:
                message = MessageClass()
                message.message_text = e.message
                return HttpResponse(message.to_json())
        else:
            return HttpResponse(json.dumps({"error": "Incorrect credentials"}), status=403)

After the YellowAnt library is installed, go to the Django project and create a
file called user_command_center.py in our Django application(within one of your
apps) and define our User application command center. The MessageClass in the
yellowant python library takes care of message formatting. More on message
formatting [here](https://www.yellowant.com/api/#message-formatting). We will
not be dealing with advanced Message formatting like attachments or buttons in
this article.

    from application.models import SiteUsers
    from yellowant.messageformat import MessageClass, MessageAttachmentsClass, MessageButtonsClass, AttachmentFieldsClass
    import datetime

    (object):

    __init__(self, function, user_integration, args, invoke_name):
            self.function = function
            self.user_integration = user_integration
            self.args = args
            self.user = user
            self.invoke_name = invoke_name

        #Simple message generator

    (self, message_text=""):
            message = MessageClass()
            message.message_text = message_text

    message.to_json()

        #Message parser

    (self):
            commands = {
                'list-users-today': self.list_users_today,
                'get-users': self.get_users,
                'get-user-details': self.get_user_details
            }

    str(self.invoke_name)
    commands:

    commands[str(self.invoke_name)](self.args)

    :
                message = MessageClass()
                message.message_text = "I could not find any command"

    message.to_json()

    (self, args):

    'id'
    args:

    generate_simple_message("Please provide parameter 'id' in your command")

    :
                #Check if Id is a number

    args['id'].is_digit():
                    user_id = int(args['id'])

    :

    generate_simple_message("Please provide an integer value for parameter 'id' in your command")

    :
                #Searching for user with id
                user_object = SiteUsers.objects.get(id=user_id)

    SiteUsers.DoesNotExist:
                #return error message if user does not exist

    generate_simple_message("User with that id does not exist")
            user_details_message = MessageClass()
            user_details_message.message_text = "User Id - %d, Fullname - %s, Date joined - %s, Subscription - %s" % (user_id, user_object.full_name, user_object.date_joined, user_object.subscription)

            user_json = UserDetailsSerializer(user_object)

            #Adding JSON data to message for use in workflows
            user_details_message.data = user_json


    user_details_message.to_json()

    (self, args):
            #Check if 'sort' param is present, else assign default as 'asc'

    'sort'
    args:

    args['sort']
    ['asc', 'dsc']:
                    order = args['sort']

    :
                    #If invalid, fallback to default value
                    order = 'asc'

    :
                #setting default order 'asc'
                order = 'asc'

    'subscription'
    args:
                subscription = args['subscription']

    :
                subscription = None
            #Instantiate a Message Object
            message = MessageClass()
            message.message_text = ""
            #Create list to store the results
            users_list = []
            d_24 = datetime.datetime.now() - datetime.timedelta(days=1)

    subscription
    None:
                users_today = SiteUsers.objects.filter(date_joined__gte=d_24)

    :
                users_today = SiteUsers.objects.filter(date_joined__gte=d_24, subscription=subscription)

    user
    users_today:
                message.message_text += user.id+"\t"+user.full_name+"\t"+user.date_joined

            #Adding users data for workflows/crumbs
            message.data = {"users":UserDetailsSerializer(users_today), many=True}


    message.to_json()

### Time to test our new application!

Populate your site users table with some data. Redirect your team member(or
yourself) to
[https://www.yellowant.com/api/oauth2/authorize/?client_id=YTjgMWGbZD6yNIDHxWcgV59Xp43yaEPufk9jyuL2](https://www.yellowant.com/api/oauth2/authorize/?client_id=YTjgMWGbZD6yNIDHxWcgV59Xp43yaEPufk9jyuL2)&response_type=code&redirect_url=http://localhost:8000/redirect_url/

![](https://cdn-images-1.medium.com/max/800/1*SclGvXrfj2q5selTIu2iTA.png)

Authorize the application and then you’ll receive a successful authorization
message.

Head over to the YellowAnt console(or the Slack @yellowant DM) and try out the
following commands:

**1. users list-users-today**

![](https://cdn-images-1.medium.com/max/800/1*iRPV1GJ4ru3l06NT8ulqCA.png)

**2. users list-users-today order “dsc”**

![](https://cdn-images-1.medium.com/max/800/1*Ldwce0nz4Sw05R6piAWtOA.png)

**3. users list-users-today subscription “paid”**

![](https://cdn-images-1.medium.com/max/800/1*OefQ5q4_Sf_Jhs35tY3Ufg.png)

And we’re done! Drop us your feedback in your YellowAnt Slack community. You can
join [here](https://yellowant-community.herokuapp.com/)!

Here is the project repository —
[https://github.com/yellowanthq/sample_user_application](https://github.com/yellowanthq/sample_user_application)

* [Python](https://blog.yellowant.com/tagged/python?source=post)

Clapping shows how much you appreciated Vishwa Krishnakumar’s story.

### [Vishwa Krishnakumar](https://blog.yellowant.com/@VishwaKk)

Building YellowAnt - [http://www.yellowant.com](http://www.yellowant.com/) —
Your intelligent workplace assistant bot

### [YellowAnt](https://blog.yellowant.com/?source=footer_card)

Intelligent workplace assistant bot, connects to many applications and lets you
take quick actions and create workflows from within chat platforms like Slack.
