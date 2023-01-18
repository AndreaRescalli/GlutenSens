/**
 * 
 * \file  Commands.h
 * \brief Header file that includes Cmd functions.
 *
 * \author Andrea Rescalli
 * \date   04/01/2023
 *
 */


#ifndef __COMMANDS_H__
    #define __COMMANDS_H__
    
    // =============================================
    //                   INCLUDES
    // =============================================
    
    #include "cytypes.h"
    #include "Commands_Defines.h"
    #include "Interrupts.h"
    #include <stdio.h>
    #include "project.h"
    
    
    
    // =============================================
    //                  FUNCTIONS
    // =============================================
    
    /**
    *   \brief Send connection string.
    *
    *   This function sends the string required 
    *   to connect the PSoC to the GUI.
    */
    void Cmd_SendConnString(void);
    
    
    /**
    *   \brief Start measurement.
    *
    *   This function starts a measurement
    *   on demand.
    */
    void Cmd_StartMeasure(void);
    
    
    /**
    *   \brief Stop measurement.
    *
    *   This function stops a measurement 
    *   on demand.
    */
    void Cmd_StopMeasure(void);
    
    
    /**
    *   \brief Send reset buffer.
    *
    *   This function sends the reset buffer 
    *   to inform the GUI on sampling frequency.
    */
    void Cmd_SendResetBuffer(void);
    
    
    /**
    *   \brief Send data stored in union object.
    *
    *   This function sends the data buffer 
    *   to the GUI.
    */    
    void Cmd_SendUnion(void);
    
    
       
    /**
    *   \brief Print commands help.
    *
    *   This function prints all the commands available to the user 
    *   on demand.
    */
    void Cmd_PrintHelp(void);
    
    
    /**
    *   \brief Invoke the command.
    *
    *   This function invokes the command called by
    *   the user.
    */
    void Cmd_InvokeCommand(char rx, const struct commandStruct commands[]);
    
    
    /**
    *   \brief Possible commands.
    *
    *   Definition of different commands that can be requested
    *   by the user via serial communication.
    */
    static const struct commandStruct commands[] = {
        {'c', &Cmd_SendConnString, "Enter c to send connection string.\r\n"},
        {'m', &Cmd_StartMeasure, "Enter m to start measurement.\r\n"},
        {'s', &Cmd_StopMeasure, "Enter s to stop measurement.\r\n"},
        {'r', &Cmd_SendResetBuffer, "Enter r to send reset info.\r\n"},
        {'u', &Cmd_SendUnion, "Enter u to send test union data buffer.\r\n"},
        {'h', &Cmd_PrintHelp, "Enter h to list commands.\r\n"},
        {' ',0,""} // End of table indicator
    };  
    
    
    /**
    *   \brief Union object to store data.
    *
    *   Definition of data union structure to simply 
    *   transmission of data.
    */
    union {
        float f;
        struct {
            uint8_t byte[4];
        };
    } union_data;
          
#endif

/* [] END OF FILE */
