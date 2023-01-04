/**
 * 
 * \file  UART_COM.h
 * \brief Header file in charge of handling UART operations.
 *
 * \author Andrea Rescalli
 * \date   04/01/2023
 *
 */


#ifndef __UART_COM_H__
    #define __UART_COM_H__
    
    // =============================================
    //                   INCLUDES
    // =============================================
    
    #include "Interrupts.h"
    #include "project.h"
    #include <stdio.h>
    
    
    
    // =============================================
    //                    MACROS
    // =============================================
    
    #define IDLE                0              ///< Idle state, no operation needed, wait for user
    #define SENSING             1              ///< Measure resistance of sensor
    
    #define DATA_SIZE           1+32/8+16/8+1  ///< Size of the measurement buffer that will be sent to the GUI
    #define RESET_SIZE          1+3+1          ///< Size of the reset buffer sent to GUI. header+sr_info+tail
    #define RESIST_SIZE         1+32/8+16/8+1  ///< Size of resistance buffer (load value)
    
    #define HEADER_RESET        0x00   ///< Header for reset packet
    #define HEADER_PSOC_R_MEAS  0x0A   ///< Header for PSoC res measurements
    
    #define TAIL_RESET          0x0F   ///< Identifier tail for reset packet    
    #define TAIL_MEAS_PACKETS   0xFF   ///< Identifier tail for measurements
    
    
    
    // =============================================
    //                  FUNCTIONS
    // =============================================
    
    /**
     * \brief Function that checks incoming characters.
     *
     * \param[in] void
     * \return void
    */
    void get_rx(void);
    
    
#endif

/* [] END OF FILE */
