#include "HTLWYCAN.h"



void HTLWYCAN::Init()
{
	hfdcan1.Instance->TSCC = 2;
	HAL_FDCAN_ConfigGlobalFilter(&hfdcan1, FDCAN_ACCEPT_IN_RX_FIFO0, FDCAN_ACCEPT_IN_RX_FIFO0, FDCAN_REJECT_REMOTE, FDCAN_REJECT_REMOTE);
	HAL_FDCAN_Start(&hfdcan1);
	
}


void HTLWYCAN::computeReceive()
{  
	
	Overflows++;
	
	static FDCAN_RxHeaderTypeDef pRxHeader;
	CAN_Message message;
	if(HAL_OK == HAL_FDCAN_GetRxMessage(&hfdcan1, FDCAN_RX_FIFO0, &pRxHeader, message.Data))
	{
		int32_t timestamp = (pRxHeader.RxTimestamp < TIM3->ARR/2)?pRxHeader.RxTimestamp:pRxHeader.RxTimestamp - TIM3->ARR;
		message.timestamp_ns = (Overflows*(TIM3->ARR+1) + timestamp) * (1e9/170e6);
		message.Parse_FDCAN_RxHeader(pRxHeader);
		RxBuffer.push(message);
	}
	

}

void HTLWYCAN::computeTransmit()
{
	CAN_Message message;
	if(TxBuffer.pop(&message))
	{
		FDCAN_TxHeaderTypeDef TxHeader = message.Get_TxHeader();
		if(HAL_OK != HAL_FDCAN_AddMessageToTxFifoQ(&hfdcan1, &TxHeader, message.Data))
		{
			TxBuffer.push(message);
		}
		else 
		{
			message.timestamp_ns = (Overflows*(TIM3->ARR+1) + TIM3->CNT) * (1e9/170e6);
			RxBuffer.push(message);
		}
	}
}
