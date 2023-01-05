/**
 *
 * \file  R_driver.c
 * \brief Source file in charge of handling resistance measurements.
 *
 * \author Andrea Rescalli
 * \date   04/01/2023
 *
 */


// =============================================
//                   INCLUDES
// =============================================

#include "R_driver.h"




/** 
 * \brief This function compute V across a resistor.
 *
 * \param[in] ADC_channel ADC channel for voltage measurement.
 *      Possible values are:
 *          - #REF_CH
 *          - #SENSE_CH 
 * \return Voltage across selected resistor
*/
int32_t measure_Voltage(uint8_t ADC_channel) {
    
    // Variables
    int32_t Voltage = 0;
    int32_t Voffset = 0;
    
    // Selection of the appropriate channel for V measurement
    IDAC_Start();
    ADC_MUX_FastSelect(ADC_channel);
    
    // Initially the IDAC has 0 mA in output --> compute Voffset
    Voffset = measure_Voffset();
    
    // Now we can compute the voltage across the desired resistor
    // by setting IDAC current to 50 uA
    IDAC_SetValue(IDAC_CURRENT);
    
    ADC_StartConvert();
	ADC_IsEndConversion(ADC_WAIT_FOR_RESULT);
	Voltage = ADC_GetResult32();

    
    // Switch off IDAC to limit self-heating
    IDAC_Stop();
    
    // Account for the offset by subtracting Voffset from Voltage
    Voltage = Voltage - Voffset;
    

    return Voltage;

} // end measure_Voltage



/** 
 * \brief This function computes Voffset across a resistor when I = 0 mA.
 * 
 * N.B: this function is used inside measure_Voltage to provide a single V that
 * accounts for the offset.    
 *
 * \param[in]  void
 * \return Voltage offset across a resistor  
*/ 
int32_t measure_Voffset(void) {
    
    // Variables
    int32_t Voffset = 0;
    
    // Ensure IDAC current output is set to 0 mA
    IDAC_SetValue(0);
    
    // Compute voltage
    ADC_StartConvert();
    ADC_IsEndConversion(ADC_WAIT_FOR_RESULT);
    Voffset = ADC_GetResult32();

    
    return Voffset;
    
} // end measure_Voffset

/* [] END OF FILE */
