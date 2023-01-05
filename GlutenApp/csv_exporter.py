import pandas as pd

import os

from datetime import datetime

from loguru import logger

import serial_workers as wrk



############
#  MACROS  #
############
"""!
@brief If the user want to export or not.
"""
EXPORT = False



##################
#  DICTIONARIES  #
##################
"""!
@brief Dict storing PSoC resistance data.
"""
PSoC_res_dict = {
    'Resistance': []
}



# Global
"""!
@brief Global variable containing .csv identifier.
"""
id = ''



##################
#  EXPORT FUNCS  #
##################
def export_psoc_res_data():
    """!
    @brief Create csv file with proper info and export PSoC resistance dict.
    """
    if EXPORT:

        if not os.path.exists("Data"):
            os.mkdir("Data")
            
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
