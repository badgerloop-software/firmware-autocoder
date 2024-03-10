
        /*
         * This is an auto-generated file which is automatically generated whenever the target is built
         */


        
#include "sofi.h"

Mutex mcu_hv_en_mutex;
Mutex mppt_overvoltage_fault_reset_mutex;
Mutex speed_target_mutex;
Mutex energy_target_mutex;

bool get_mcu_hv_en() {
  mcu_hv_en_mutex.lock();
  bool val = dfdata.mcu_hv_en;
  mcu_hv_en_mutex.unlock();
  return val;
}
void set_mcu_hv_en(bool val) {
  mcu_hv_en_mutex.lock();
  dfdata.mcu_hv_en = val;
  mcu_hv_en_mutex.unlock();
}

bool get_mppt_overvoltage_fault_reset() {
  mppt_overvoltage_fault_reset_mutex.lock();
  bool val = dfdata.mppt_overvoltage_fault_reset;
  mppt_overvoltage_fault_reset_mutex.unlock();
  return val;
}
void set_mppt_overvoltage_fault_reset(bool val) {
  mppt_overvoltage_fault_reset_mutex.lock();
  dfdata.mppt_overvoltage_fault_reset = val;
  mppt_overvoltage_fault_reset_mutex.unlock();
}

float get_speed_target() {
  speed_target_mutex.lock();
  float val = dfdata.speed_target;
  speed_target_mutex.unlock();
  return val;
}
void set_speed_target(float val) {
  speed_target_mutex.lock();
  dfdata.speed_target = val;
  speed_target_mutex.unlock();
}

float get_energy_target() {
  energy_target_mutex.lock();
  float val = dfdata.energy_target;
  energy_target_mutex.unlock();
  return val;
}
void set_energy_target(float val) {
  energy_target_mutex.lock();
  dfdata.energy_target = val;
  energy_target_mutex.unlock();
}
 /* Autogenerated Code Ends */


