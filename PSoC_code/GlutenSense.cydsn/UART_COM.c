/**
 * 
 * \file  UART_COM.c
 * \brief Source file in charge of handling UART operations.
 *
 * \author Andrea Rescalli
 * \date   04/01/2023
 *
 */


// =============================================
//                   INCLUDES
// =============================================

#include "UART_COM.h"



// =============================================
//                   VARIABLES
// =============================================

static uint8_t ch_rx = 0;   // Stores the recieved byte



/**
 * \brief Function that checks incoming characters.
 *
 * \param[in] void
 * \return void
*/
void get_rx(void) {
    if(flag_rx) {
        ch_rx = UART_ReadRxData();
        flag_rx = 0;
        
        if(ch_rx == 'v') {
            UART_PutString("Thesis $$$\r\n");
        }
        
        if(ch_rx == 's') {           
            state = IDLE;
        }
        
        if(ch_rx == 'r') {
            // User requested resistance computation
            Reset_TIMER();                     
            state = SENSING;
        }
    }
} // end measure_capacitance



/* [] END OF FILE */
