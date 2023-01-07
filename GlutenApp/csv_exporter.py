import pandas as pd

import os

from datetime import datetime

from loguru import logger

import serial_workers as wrk



############
#  MACROS  #
############
EXPORT = False
"""
If the user want to export or not.
"""



##################
#  DICTIONARIES  #
##################
PSoC_res_dict = {
    'Resistance': []
}
"""
Dictionary storing measured resistance data.
"""


# Global
id = ''
"""
Global variable containing .csv identifier chosen by the user.
"""


##################
#  EXPORT FUNCS  #
##################
def export_psoc_res_data():
    """
    This function creates a ``.csv`` file with information on sampling frequency and resistance data.
    """
    if EXPORT:

        if not os.path.exists("Data"):
            os.mkdir("Data")
            logger.success("Data directory created.")
            
        file_name = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")+'_'+id
        path = os.path.join('Data',file_name+'.csv')

        sample_rate = str(wrk.PSOC_RES_SAMPLE_RATE)

        with open(path, 'w') as file1:
            file1.write('#Identifier: '+id+'\n')
            file1.write('#Sample rate: '+sample_rate+' Hz\n')
            file1.write('#Units: Ohm'+'\n')
            file1.write('\n')

        df = pd.DataFrame(PSoC_res_dict)
        df.to_csv(
            path,
            mode='a', 
            index=False,
            encoding='utf-8',
            float_format='%.3f',
            decimal=',',
            sep=';'
        )

        logger.info("PSoC resistance data exported into csv")
