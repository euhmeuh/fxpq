"""
Package configuration

Every dictionary declared here is a configuration entry.
"""

from fxpq.config import DropdownChoice


inputs = {
    'home': {
        'model': DropdownChoice()
    }
}


images = {
    'home': """
                
                
  ### ####      
  # ##  # #     
  # #  # # #    
  ##  # # # #   
  #  # # # # #  
 ############## 
  #          #  
  #    ###   #  
  #   #   #  #  
  #   #   #  #  
  #   #  ##  #  
  #   #   #  #  
  ############  
                
"""  # nopep8
}
