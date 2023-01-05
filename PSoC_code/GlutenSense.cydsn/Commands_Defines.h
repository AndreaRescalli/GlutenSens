/**
 * 
 * \file  Commands_Defines.h
 * \brief Header file that includes typedefs and struct for Cmd functions.
 *
 * \author Andrea Rescalli
 * \date   04/01/2023
 *
 */


#ifndef __COMMANDS_DEFINES_H__
    #define __COMMANDS_DEFINES_H__ 
    
    // =============================================
    //                    MACROS
    // =============================================
    
    #define IDLE                0              ///< Idle state, no operation needed, wait for user
    #define SENSING             1              ///< Measure resistance of sensor
    
    #define TIMER_PERIOD        5              ///< Period of the timer, with a 1kHz clock [ms]
    #define FS                  40             ///< Desired sampling frequency [Hz]
    
    #define DATA_SIZE           1+32/8+16/8+1  ///< Size of the measurement buffer that will be sent to the GUI
    #define RESET_SIZE          1+1+1          ///< Size of the reset buffer sent to GUI. header+sr_info+tail
    #define RESIST_SIZE         1+32/8+16/8+1  ///< Size of resistance buffer (load value)
    
    #define HEADER_RESET        0x00   ///< Header for reset packet
    #define HEADER_PSOC_R_MEAS  0x0A   ///< Header for PSoC res measurements
    
    #define TAIL_RESET          0x0F   ///< Identifier tail for reset packet    
    #define TAIL_MEAS_PACKETS   0xFF   ///< Identifier tail for measurements  
    
    
    #define typename(x) _Generic((x),                                                 \
            _Bool: "_Bool",                  unsigned char: "unsigned char",          \
             char: "char",                     signed char: "signed char",            \
        short int: "short int",         unsigned short int: "unsigned short int",     \
              int: "int",                     unsigned int: "unsigned int",           \
         long int: "long int",           unsigned long int: "unsigned long int",      \
    long long int: "long long int", unsigned long long int: "unsigned long long int", \
            float: "float",                         double: "double",                 \
      long double: "long double",                   char *: "pointer to char",        \
     const char *: "constant pointer to char",                                        \
           void *: "pointer to void",                int *: "pointer to int",         \
          default: "other")
    
      
    /**
    *   \brief Function pointer.
    *
    *   General function pointer type.
    */
    typedef void(*functionPointerType)();
    
    
    /**
    *   \brief Command structure.
    *
    *   This structure defines the command's character identifier (name)
    *   that the user needs to access the command, the command function
    *   to be executed (execute) and finally a brief description of the
    *   command function (help).
    */
    struct commandStruct {
        char name;
        functionPointerType execute;
        const char* help;        
    };
                                  
#endif

/* [] END OF FILE */
