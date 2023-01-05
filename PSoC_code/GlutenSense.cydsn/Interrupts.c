/**
 *
 * \file  Interrupts.c
 * \brief Source file in charge of handling interrupt routines.
 *
 * \author Andrea Rescalli
 * \date   04/01/2023
 *
 */


// =============================================
//                   INCLUDES
// =============================================

#include "Interrupts.h"
#include <stdio.h>


char msg[50] = {};


/**
 * \brief UART ISR.
 * 
 * ISR of the UART that is used to pilot remotely the device based on commands recieved.
*/
CY_ISR(Custom_ISR_RX) {
    
    // Check UART status
    if(UART_ReadRxStatus() == UART_RX_STS_FIFO_NOTEMPTY) {
        // If we have recieved a byte, communicate it
        flag_rx = 1;
        state = IDLE;
    }    
    
} // end ISR_RX



/**
 * \brief Timer ISR triggered every 5 ms.
*/
CY_ISR(Custom_ISR_TIMER) {
    
    // Read timer status to bring interrupt line low
    Timer_ReadStatusRegister();
    
    flag_timer  = 1;
    count_fs   += 1;
            
    if((count_fs%5) == 0) {
        flag_fs  = 1;
        count_fs = 0;
    }    
    
} // end ISR_TIMER



/**
 * \brief Function that resets the timer.
 *
 * \param[in] void
 * \return void
*/
void Reset_TIMER(void) {
    
    // Reset the timer
    Timer_Stop();
    Timer_WriteCounter(TIMER_PERIOD-1);
    Timer_Enable();
    flag_timer  = 0;
    flag_fs     = 0;
    count_fs    = 0;
    
} // end Reset_TIMER

/* [] END OF FILE */
