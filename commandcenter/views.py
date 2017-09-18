from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from yellowant import YellowAnt
import json

# Send the users to this view to access this application
from commandcenter.commands import AppCommands
from commandcenter.models import AdminUsers


def redirect_to_auth(request):
    return HttpResponseRedirect(
        "https://www.yellowant.com/api/oauth2/authorize/?client_id=" + settings.YA_CLIENT_ID
        + "&response_type=code&redirect_url=" + settings.YELLOWANT_REDIRECT_URL)


#Redirect URL logic
def redirect_url(request):
    #YellowAnt redirects to this view with code and state values
    code = request.GET.get("code", False)
    #state = request.GET.get("state", False)

    #Exchange code with permanent token
    y = YellowAnt(app_key=settings.YA_CLIENT_ID, app_secret=settings.YA_CLIENT_SECRET,
                  access_token=None,
                  redirect_uri=settings.YELLOWANT_REDIRECT_URL)
    access_token_dict = y.get_access_token(code)
    access_token = access_token_dict['access_token']

    #List of emails of users allowed access to this application
    users_allowed_emails = ['vishwa@yellowant.com', 'ankur@yellowant.com', 'nitin@yellowant.com', 'rohan@yellowant.com']

    #Using token to fetch user details
    x = YellowAnt(access_token=access_token)
    profile = x.get_user_profile()

    if profile['email'] in users_allowed_emails:
        q = x.create_user_integration()
        user_application = q['user_application']
        ti = AdminUsers.objects.create(yellowant_user_id=profile['id'],
                                            yellowant_integration_id=user_application,
                                            yellowant_integration_user_invoke_name=q[
                                                'user_invoke_name'],
                                            yellowant_user_token=access_token
                                            )
        return HttpResponse("You are now authenticated!")
    else:
        return HttpResponse("You are not allowed to access this application!")

#Handle Commands in api_url
def api_url(request):
    data = json.loads(request.POST["data"])
    command = data["function"]
    service_application = data["application"]
    args = data["args"]
    function_name = data['function_name']
    verification_token = data['verification_token']

    #Check if verification_token matches that in the Developer console
    if verification_token == settings.YA_VERIFICATION_TOKEN:
        #Send command string with user details to Command Center(AppCommands)
        message = AppCommands(command, service_application, args, function_name).parse()
        #Returning JSON response
        return HttpResponse(message, status=200)
    else:
        return HttpResponse({"error":"incorrect verification token"}, status=401)
