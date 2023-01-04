/**
 *
 * \file  Interrupts.h
 * \brief Header file in charge of handling interrupt routines.
 *
 * \author Andrea Rescalli
 * \date   04/01/2023
 *
 */


#ifndef __INTERRUPTS_H_
    #define __INTERRUPTS_H_
    
    // =============================================
    //                   INCLUDES
    // =============================================
    
    #include "cytypes.h"
    #include "Commands_Defines.h"
    #include "project.h"
    
    
    
    // =============================================
    //               GLOBALS & FLAGS
    // =============================================
    
    volatile uint8_t state;         ///< Keeps track of the state we're in
     
    volatile uint8_t flag_rx;       ///< Flag that tells a byte has been recieved
    
    volatile uint8_t flag_timer_5;      ///< Flag that tells 5ms have passed
    volatile uint8_t flag_100Hz;        ///< Flag that tells 1 sec have passed
    volatile uint8_t count_100Hz;       ///< Counter to keep track of each 10ms passed
    
    
    
    // =============================================
    //                  FUNCTIONS
    // =============================================  
    
    /**
     * \brief UART ISR.
     * 
     * ISR of the UART that is used to pilot remotely the device based on commands recieved
    */    
    CY_ISR_PROTO(Custom_ISR_RX);
    
    
    
    /**
     * \brief Timer ISR triggered every 5 ms.
    */    
    CY_ISR_PROTO(Custom_ISR_TIMER);
    
    

    /**
     * \brief Function that resets the timer.
     *
     * \param[in] void
     * \return void
    */
    void Reset_TIMER(void);
    
#endif

/* [] END OF FILE */
