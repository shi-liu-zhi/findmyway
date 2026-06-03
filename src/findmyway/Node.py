#%% 
import requests
from IPython.display import display, Image
import qrcode
import hashlib
import urllib.parse
from typing import Dict, Any
import itertools
import time
from Amap_request import point_getcode, generate_signature


#%%
class Node():
    def __init__(self, address:str = '', city = '宁波'):
        self.address = address
        self.city = city
        self.latlon = point_getcode(address=address, city=city)
    
    def __call__(self):
        return {self.address: self.latlon}
    
    def __str__(self):
        return(f"{self.address} {self.latlon}")

    def __repr__(self):
        return(f"{self.address} {self.latlon}")

# %%
