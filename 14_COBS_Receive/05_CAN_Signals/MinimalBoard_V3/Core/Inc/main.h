/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32g4xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define f_Task1 10000
#define f_Task2 12500
#define PC13_CAN_disable_Pin GPIO_PIN_13
#define PC13_CAN_disable_GPIO_Port GPIOC
#define PC14_YellowLed_on_Pin GPIO_PIN_14
#define PC14_YellowLed_on_GPIO_Port GPIOC
#define PC15_Button_notPressed_Pin GPIO_PIN_15
#define PC15_Button_notPressed_GPIO_Port GPIOC
#define PF1_Osc_Enable_Pin GPIO_PIN_1
#define PF1_Osc_Enable_GPIO_Port GPIOF
#define PB1_GreenLed_on_Pin GPIO_PIN_1
#define PB1_GreenLed_on_GPIO_Port GPIOB
#define PB2_RedLed_on_Pin GPIO_PIN_2
#define PB2_RedLed_on_GPIO_Port GPIOB
#define PB10_Debug_UART3_TX_Pin GPIO_PIN_10
#define PB10_Debug_UART3_TX_GPIO_Port GPIOB
#define PB11_Debug_UART3_RX_Pin GPIO_PIN_11
#define PB11_Debug_UART3_RX_GPIO_Port GPIOB

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
