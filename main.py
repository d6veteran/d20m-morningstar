# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# main.py serves the Morningstar home page.
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
import models
import rules

from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import os
import logging

from django.utils import simplejson
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

############################# REQUEST HANDLERS ############################### 
##############################################################################   
class MainHandler(webapp.RequestHandler):
    def get(self):
        _trace = TRACE+'MainHandler:: get() '
        logging.info(_trace)        
        template_values = {
            'players': simplejson.dumps(DEATH_PINS),
            'monsters': simplejson.dumps(MONSTER_PINS),
            'battles': simplejson.dumps(BATTLE_PINS),
            'c_players': simplejson.dumps(C_DEATH_PINS),
            'c_monsters': simplejson.dumps(C_MONSTER_PINS),
            'c_battles': simplejson.dumps(C_BATTLE_PINS),
            'f_players': simplejson.dumps(F_DEATH_PINS),
            'f_monsters': simplejson.dumps(F_MONSTER_PINS),
            'f_battles': simplejson.dumps(F_BATTLE_PINS)                        
        }        
        generate(self, 'main.html', template_values)               

class PageHandler(webapp.RequestHandler):
    def get(self, page):
        _trace = TRACE+'StaticHandler:: get() '
        logging.info(_trace)
        _page = 'page_' + page + '.html'        
        template_values = {}        
        generate(self, _page, template_values)

######################## METHODS #############################################
##############################################################################
def generate(self, template_name, template_values):
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, 
                        os.path.join('templates', template_name))

    self.response.out.write(template.render(path, 
                                            template_values, 
                                            debug=DEBUG))

######################## DATA ################################################
##############################################################################
BATTLE_PINS = [
    {'lat':47.6, 'lon':-122.3, 'location': 'Seattle, Washington'},
    {'lat':38.651198, 'lon':-90.2362, 'location': 'St. Louis, Missouri'},
    {'lat':40.881852261133716, 'lon':-72.73434162139893, 'location': 'Long Island, New York'},
    {'lat':38.66, 'lon':-109.59, 'location': 'Arches National Park'}    
  ]
 
MONSTER_PINS = [
    {'lat':47.6355, 'lon':-122.2953, 'location': 'Seattle, Washington'},
    {'lat':32.7272, 'lon':-117.1692, 'location': 'San Diego, California'},
    {'lat':33.9616, 'lon':-117.4109, 'location': 'Riverside, California'},    
    {'lat':34.1755, 'lon':-118.8501, 'location': 'Thousand Oaks, California'},  
    {'lat':30.243006016254498, 'lon':-97.70562171936035, 'location': 'Austin, Texas'}, 
    {'lat':40.771831872647006, 'lon':-73.97254586219788, 'location': 'New York, New York'}, 
    {'lat':37.3204, 'lon':-113.0747, 'location': 'Zion National Park'}
  ]

DEATH_PINS = [
    {'lat':47.6621, 'lon':-122.1130, 'location': 'Redmond, Washington'},
    {'lat':41.8817, 'lon':-87.6227, 'location': 'Chicago, Illinois'},
    {'lat':41.88796, 'lon':-87.7859, 'location': 'Oak Park, Illinois'},
    {'lat':37.7707, 'lon':-122.4701, 'location': 'San Francisco, Washington'}
  ]

C_DEATH_PINS = [
    {'lat':37.77271618103960, 'lon':-122.45494365692139, 'location': 'custom'},
    {'lat':37.77363207735496, 'lon':-122.46073722839355, 'location': 'custom'},
    {'lat':37.776939386254625, 'lon':-122.44964361190796, 'location': 'custom'},
    {'lat':37.773767764733025, 'lon':-122.44773387908936, 'location': 'custom'},    
    {'lat':37.77337766284987, 'lon':-122.44743347167969, 'location': 'custom'}
  ]
 
C_MONSTER_PINS = [
    {'lat':37.77375080382439, 'lon':-122.45942831039429, 'location': 'custom'},
    {'lat':37.77473453009397, 'lon':-122.4490213394165, 'location': 'custom'},
    {'lat':37.775752164185256, 'lon':-122.45022296905518, 'location': 'custom'},    
    {'lat':37.77554863848759, 'lon':-122.45803356170654, 'location': 'custom'},  
    {'lat':37.77509070361927, 'lon':-122.45513677597046, 'location': 'custom'}, 
    {'lat':40.771831872647006, 'lon':-73.97254586219788, 'location': 'custom'}, 
    {'lat':37.3204, 'lon':-113.0747, 'location': 'custom'}
  ]

C_BATTLE_PINS = [
    {'lat':37.772733142185615, 'lon':-122.4582052230835, 'location': 'custom'},
    {'lat':37.7709522006134, 'lon':-122.45357036590576, 'location': 'custom'},
    {'lat':37.775582559476135, 'lon':-122.4526047706604, 'location': 'custom'}
  ]

F_DEATH_PINS = [
    {'lat':41.00771441111866, 'lon':-91.96130633354187, 'location': 'custom'},
    {'lat':41.008815486149224, 'lon':-91.97039365768433, 'location': 'custom'},
    {'lat':41.0212255960373, 'lon':-91.95745468139648, 'location': 'custom'},
    {'lat':40.993957518731996, 'lon':-91.9662094116211, 'location': 'custom'},    
    {'lat':41.01060469383153, 'lon':-91.96333408355713, 'location': 'custom'}
    ]

F_MONSTER_PINS = [
    {'lat':41.008434969653045, 'lon':-91.96101665496826, 'location': 'custom'},
    {'lat':41.00939840077537, 'lon':-91.95832371711731, 'location': 'custom'},
    {'lat':41.00827304707329, 'lon':-91.95197224617004, 'location': 'custom'},    
    {'lat':41.01487106992668, 'lon':-91.95832371711731, 'location': 'custom'},  
    {'lat':41.01538916889316, 'lon':-91.96074306964874, 'location': 'custom'}, 
    {'lat':41.017469619021014, 'lon':-91.96629524230957, 'location': 'custom'}, 
    {'lat':41.00817589333443, 'lon':-91.98054313659668, 'location': 'custom'}, 
    {'lat':41.009536032642885, 'lon':-91.94689750671387, 'location': 'custom'}
    ]

F_BATTLE_PINS = [
    {'lat':41.00351234541235, 'lon':-91.96075916290283, 'location': 'custom'},
    {'lat':41.02138748678339, 'lon':-91.95204734802246, 'location': 'custom'},
    {'lat':41.01526773981346, 'lon':-91.9529914855957, 'location': 'custom'},
    {'lat':41.01721057822843, 'lon':-91.96964263916016, 'location': 'custom'}
    ]
                                            
##############################################################################
##############################################################################
application = webapp.WSGIApplication([(r'/page/(.*)', PageHandler),
                                      (r'/.*', MainHandler)],
                                       debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()