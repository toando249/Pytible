import requests
import os
r = requests.delete('https://graph.facebook.com/v2.6/me/messenger_profile?access_token='+os.getenv("FACEBOOK_TOKEN"))
return str(r.status_code)
