#ifndef __dataFormat__h__
#define __dataFormat__h__

#include "mbed.h"

#pragma pack(push, 1)

#define BYTE_ARRAY_SIZE sizeof(data_format)

// Restart enable management
bool get_restart_enable();
void set_restart_enable(bool val);

// Clears data struct
void cleardfdata();

// To freeze telemetry readings for transmissions
void copyDataStructToWriteStruct();



/*!!AUTO-GENERATE HERE!!*/

#pragma pack(pop)
#endif
