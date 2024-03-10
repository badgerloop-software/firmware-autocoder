#include "dataFormat.h"

// Two structs
// dfdata is continuously updated struct
// dfdata is periodically frozen in dfwrite for software transmission
Mutex dfwrite_mutex;
data_format dfwrite;
data_format dfdata;

// Restart enable variable and management
Mutex restart_enable_mutex;
bool restart_enable;

bool get_restart_enable() {
  restart_enable_mutex.lock();
  bool val = restart_enable;
  restart_enable_mutex.unlock();
  return val;
}

void set_restart_enable(bool val) {
  restart_enable_mutex.lock();
  restart_enable = val;
  restart_enable_mutex.unlock();
}

void cleardfdata() {
    memset(&dfdata, 0, BYTE_ARRAY_SIZE);

    // Restore headers and footers
    char header[6] = "<bsr>";
    char footer[7] = "</bsr>";

    // Copy headers and footers into spots, exclude null terminator
    for (int i = 0; i < 5; i++) {
        dfdata.header[i] = header[i];
    }

    for (int i = 0; i < 6; i++) {
        dfdata.footer[i] = footer[i];
    }
}



/*!!AUTO-GENERATE HERE!!*/