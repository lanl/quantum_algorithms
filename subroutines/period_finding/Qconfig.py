# Before you can use the jobs API, you need to set up an access token.
# Log in to the Quantum Experience. Under "Account", generate a personal 
# access token. Replace "None" below with the quoted token string.
# Uncomment the APItoken variable, and you will be ready to go.

APItoken = "23e4f817e1807d8ae3c466d7a8760d4dd4dbb0b036e7e151787214a4a3b97b491628b9d9038557a8b3cfef58816a44a7572aceacaf881d34b5092818baba0ce4"

config = {
  "url": 'https://quantumexperience.ng.bluemix.net/api'
}

if 'APItoken' not in locals():
  raise Exception("Please set up your access token. See Qconfig.py.")
