import requests
from ConstantsNFunctions import build_url
print(requests.post(build_url('/api/like/get'), data={'peer_id': 1}).text)