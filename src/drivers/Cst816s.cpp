#include "Cst816s.h"
#include <FreeRTOS.h>
#include <legacy/nrf_drv_gpiote.h>
#include <nrfx_log.h>
#include <task.h>
#include <SEGGER_RTT.h>

using namespace Pinetime::Drivers;

/* References :
 * This implementation is based on this article :
 * https://medium.com/@ly.lee/building-a-rust-driver-for-pinetimes-touch-controller-cbc1a5d5d3e9 Touch panel datasheet (weird chinese
 * translation) : https://wiki.pine64.org/images/5/51/CST816S%E6%95%B0%E6%8D%AE%E6%89%8B%E5%86%8CV1.1.en.pdf
 *
 * TODO : we need a complete datasheet and protocol reference!
 * */

Cst816S::Cst816S() {}

bool Cst816S::Init() {
//  nrf_gpio_cfg_output(PinMap::Cst816sReset);
//  nrf_gpio_pin_set(PinMap::Cst816sReset);
//  vTaskDelay(50);
//  nrf_gpio_pin_clear(PinMap::Cst816sReset);
//  vTaskDelay(5);
//  nrf_gpio_pin_set(PinMap::Cst816sReset);
//  vTaskDelay(50);

  // Wake the touchpanel up
//  uint8_t dummy;
//  twiMaster.Read(twiAddress, 0x15, &dummy, 1);
//  vTaskDelay(5);
//  twiMaster.Read(twiAddress, 0xa7, &dummy, 1);
//  vTaskDelay(5);

  /*
  [2] EnConLR - Continuous operation can slide around
  [1] EnConUD - Slide up and down to enable continuous operation
  [0] EnDClick - Enable Double-click action
  */
//  static constexpr uint8_t motionMask = 0b00000101;
//  twiMaster.Write(twiAddress, 0xEC, &motionMask, 1);

  /*
  [7] EnTest - Interrupt pin to test, enable automatic periodic issued after a low pulse.
  [6] EnTouch - When a touch is detected, a periodic pulsed Low.
  [5] EnChange - Upon detecting a touch state changes, pulsed Low.
  [4] EnMotion - When the detected gesture is pulsed Low.
  [0] OnceWLP - Press gesture only issue a pulse signal is low.
  */
//  static constexpr uint8_t irqCtl = 0b01110000;
//  twiMaster.Write(twiAddress, 0xFA, &irqCtl, 1);

  // There's mixed information about which register contains which information
//  if (twiMaster.Read(twiAddress, 0xA7, &chipId, 1) == TwiMaster::ErrorCodes::TransactionFailed) {
//    chipId = 0xFF;
//    return false;
//  }
//  if (twiMaster.Read(twiAddress, 0xA8, &vendorId, 1) == TwiMaster::ErrorCodes::TransactionFailed) {
//    vendorId = 0xFF;
//    return false;
//  }
//  if (twiMaster.Read(twiAddress, 0xA9, &fwVersion, 1) == TwiMaster::ErrorCodes::TransactionFailed) {
//    fwVersion = 0xFF;
//    return false;
//  }
//
//  return chipId == 0xb4 && vendorId == 0 && fwVersion == 1;
  return true;
}

void Cst816S::RecvTouchInfo(bool touching){

  uint8_t buf[3];
  size_t bytes_read = SEGGER_RTT_Read(0, buf, 3);
  if (bytes_read != 3){
    info.isValid = false;
    return;
  }

//  info.gesture = static_cast<Gestures>(touchData[gestureIndex]);
  info.gesture = static_cast<Gestures>((buf[0] >> 1));
  info.touching = touching;

  info.x = buf[1];//<<4;
  info.y = buf[2];//<<4;
  SEGGER_RTT_printf(0, "recvd %u: x=%u, y=%u, g=%u\r\n", info.touching, info.x, info.y, info.gesture);
}

Cst816S::TouchInfos Cst816S::GetTouchInfo() {
  return info;
}

void Cst816S::Sleep() {
//  nrf_gpio_pin_clear(PinMap::Cst816sReset);
//  vTaskDelay(5);
//  nrf_gpio_pin_set(PinMap::Cst816sReset);
//  vTaskDelay(50);
  static constexpr uint8_t sleepValue = 0x03;
//  twiMaster.Write(twiAddress, 0xA5, &sleepValue, 1);
  NRF_LOG_INFO("[TOUCHPANEL] Sleep");
}

void Cst816S::Wakeup() {
  Init();
  NRF_LOG_INFO("[TOUCHPANEL] Wakeup");
}
