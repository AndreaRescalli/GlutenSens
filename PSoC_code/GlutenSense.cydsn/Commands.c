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

#define TEST_HEADER 0x11
#define TEST_TAIL   0x0f




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
*   \brief Send reset buffer.
*
*   This function sends the reset buffer 
*   to inform the GUI on sampling frequency.
*/
void Cmd_SendResetBuffer(void) {
    uint8_t reset_buffer[RESET_SIZE] = {0};
    reset_buffer[0]                  = HEADER_RESET;
    reset_buffer[1]                  = FS;
    reset_buffer[RESET_SIZE-1]       = TAIL_RESET;
    
    UART_PutArray(reset_buffer, RESET_SIZE);
}



/**
*   \brief Send data stored in union object.
*
*   This function sends the data buffer 
*   to the GUI.
*/    
void Cmd_SendUnion(void) {
    union_data.f = -5648.365;
    uint8_t u_buffer[6] = {0};
    
    u_buffer[0]         = 0x11;
    u_buffer[1]         = union_data.byte[0];
    u_buffer[2]         = union_data.byte[1];
    u_buffer[3]         = union_data.byte[2];
    u_buffer[4]         = union_data.byte[3];
    u_buffer[6-1]       = 0x0F;
    
    UART_PutArray(u_buffer, 6);     
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
