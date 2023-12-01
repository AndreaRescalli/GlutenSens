/**
 *
 * \file  R_driver.h
 * \brief Header file in charge of handling resistance measurements.
 *
 * \author Andrea Rescalli
 * \date   01/12/2023
 *
 */

/*****************************************************************************************
 * DESIGN CONSIDERATIONS: 
 * - Four wire sensing config --> R_wires (+ internal R_rout from pin to ADC) neglected 
 *                                thanks to high input impedance of ADC.
 * 
 * - Implementation of reference resistor to overcome gain and offset errors due to IDAC
 *   and ADC; flexibility on the choice of the sensing reference, very important since we 
 *   want it to be close to the sensing resistor value.
 *   In fact, If the reference resistor and sensor are in the same part of the ADC transfer 
 *   function, non-linearities in the ADC are canceled out.
 * 
 * - IDAC indications: the higher the current the higher the accuracy, but it can induce 
 *   self heating --> IDAC off when not measuring to mitigate it
 *   N.B: Voltage at IDAC cannot exceed compliance voltage Vc = Vdd - 1V. In this case: 
 *               [w/ R_rout = 600 ohm | R_ref = 10010 ohm]
 *   Vc_sense  = I*(R_rout+(3*R_wires)+R_ref+R_sense)
 *   Being Vdd = 5V --> R_sense_MAX = (5V-1V)/I-(R_rout+(3*R_wires)+R_ref) 
 *               if we choose I = 50uA we can accept up to 69k ohm of load (of course 
 *               R_ref, the reference, will be sensibly off with respect to the sensor)

 * - Calibration flow: [performed regularly to cancel out offset drifts]
 * 1. set IDAC to 0mA and measure V = V0 across each resistor
 * 2. set IDAC to 50uA and measure V across each resistor
 * 3. R_unkwn = R_kwn*(V_R_unkwn-V0)/(V_R_kwn-V0)
 *    N and D are affected by ADC and IDAC gain errors but division cancels them out
 ****************************************************************************************/


#ifndef __R_DRIVER_H_
    #define __R_DRIVER_H_
    
    // =============================================
    //                   INCLUDES
    // =============================================
    
    #include "cytypes.h"
    #include "project.h"
    
    
    
    // =============================================
    //                  ADC MACROS
    // =============================================
    
    /**
    *   \brief Mux channel for measuring voltage across reference R.
    */
    #define REF_CH             0
    
    
    /**
    *   \brief Mux channel for measuring voltage across the sensor.
    */    
    #define SENSE_CH           1
    
    
    
    // =============================================
    //                  IDAC MACROS
    // =============================================    
    
    /**
    *   \brief Value of output IDAC current. 8bit hex codification for uA value.
    */
    #define IDAC_CURRENT       50 // 50 uA
    
    
    
    // =============================================
    //               AUXILIARY MACROS
    // =============================================    
    
    /**
    *   \brief Ohm value of the reference resistor.
    */    
    #define REFERENCE_RESISTOR 10010
    

    
    // =============================================
    //                   FUNCTIONS
    // =============================================    
    
    /** 
     * \brief This function compute V across a resistor.
     *
     * \param[in] ADC_channel ADC channel for voltage measurement.
     *      Possible values are:
     *          - #REF_CH
     *          - #SENSE_CH 
     * \return Voltage across selected resistor
    */
    int32_t measure_Voltage(uint8_t ADC_channel);    
    
    
    /** 
     * \brief This function computes Voffset across a resistor when I = 0 mA.
     * 
     * N.B: this function is used inside measure_Voltage to provide a single V that
     * accounts for the offset.    
     *
     * \param[in]  void
     * \return Voltage offset across a resistor  
    */    
    int32_t measure_Voffset(void);
    
    
#endif

/* [] END OF FILE */
