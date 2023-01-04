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
    *   \brief Toggle on-board blue LED.
    *
    *   This function toggles the on-board blue LED 
    *   on demand.
    */
    void Cmd_LEDTest(void);
    
    
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
        {'v', &Cmd_SendConnString, "Enter v to send connection string.\r\n"},
        {'r', &Cmd_StartMeasure, "Enter r to start measurement.\r\n"},
        {'s', &Cmd_StopMeasure, "Enter s to stop measurement.\r\n"},
        {'l', &Cmd_LEDTest, "Enter l to toggle built-in blue LED.\r\n"},
        {'h', &Cmd_PrintHelp, "Enter h to list commands.\r\n"},
        {' ',0,""} // End of table indicator
    };  
          
#endif

/* [] END OF FILE */
