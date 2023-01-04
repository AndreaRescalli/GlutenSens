/**
 * 
 * \file  Commands.c
 * \brief Source file that includes Cmd functions.
 *
 * \author Andrea Rescalli
 * \date   04/01/2023
 *
 */


// =============================================
//                   INCLUDES
// =============================================

#include "Commands.h"



/**
*   \brief Send connection string.
*
*   This function sends the string required 
*   to connect the PSoC to the GUI.
*/
void Cmd_SendConnString(void) {
    UART_PutString("Gluten $$$\r\n");
}



/**
*   \brief Start measurement.
*
*   This function starts a measurement
*   on demand.
*/
void Cmd_StartMeasure(void) {
    // User requested resistance computation
    Reset_TIMER();                     
    state = SENSING;
}



/**
*   \brief Stop measurement.
*
*   This function stops a measurement 
*   on demand.
*/
void Cmd_StopMeasure(void) {
    state = IDLE;
}



/**
*   \brief Toggle on-board blue LED.
*
*   This function toggles the on-board blue LED 
*   on demand.
*/
void Cmd_LEDTest(void) {
    uint8_t status = Debug_LED_Read();
    Debug_LED_Write(!status);
}



/**
*   \brief Print commands help.
*
*   This function prints all the commands available to the user 
*   on demand.
*/
void Cmd_PrintHelp(void) {
    unsigned int i = 0;
    while(commands[i].name != ' ') {
        UART_PutString(commands[i].help);
        i++;
    }
}



/**
*   \brief Invoke the command.
*
*   This function invokes the command called by
*   the user.
*/
void Cmd_InvokeCommand(char rx, const struct commandStruct *cmd) {
    unsigned int i = 0;
    while(cmd[i].name != ' ') {
        if (cmd[i].name == rx) {
            cmd[i].execute();
            break;
        }
        i++;
    }
}

/* [] END OF FILE */
