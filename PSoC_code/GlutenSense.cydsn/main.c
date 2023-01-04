/**
 *
 * \file  main.c
 * \brief Main source file for GlutenSense PhD project.
 *
 * This project requires the implementation of an R measurement circuit that can interface with the
 * user through a GUI. The final goal is to monitor the variation of resistance of a polymeric gas
 * sensor when exposed to NH3 derived from the digestion of gluten content in food samples.
 *
 * \author: Andrea Rescalli
 * \date:   04/01/2023
 *
 */

// =============================================
//                   INCLUDES
// =============================================

#include "project.h"
#include "Interrupts.h"
#include "Commands.h"



// =============================================
//                    MACROS
// =============================================

/**
*   \brief LED state ON.
*/
#define LED_ON  1

/**
*   \brief LED state OFF.
*/
#define LED_OFF 0



// =============================================
//                    GLOBALS
// =============================================




int main(void) {
    
    CyGlobalIntEnable; /* Enable global interrupts. */
    
    
    // Init components
    CyDelay(100);
    
    ADC_MUX_Start();
    ADC_Start();
    UART_Start();
    Timer_Start();
   
    CyDelay(1000);
    
    
    // Init flags and variables
    state           = IDLE;   
    flag_rx         = 0;
    char rx         = 0;
    flag_timer_5    = 0;
    count_100Hz     = 0;    
    flag_100Hz      = 0;
    
    
    // Init ISRs
    ISR_RX_StartEx(Custom_ISR_RX);
    ISR_TIMER_StartEx(Custom_ISR_TIMER);


    for(;;) {
        
        if(flag_rx) {
            flag_rx = 0;
            rx = UART_ReadRxData();
            
            // Handle possible user requested commands
            Cmd_InvokeCommand(rx, commands);
            
        }
        
    } // end for loop
    
} // end main

/* [] END OF FILE */
