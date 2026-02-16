#ifndef __CAN_MESSAGE_H
	#define __CAN_MESSAGE_H
	
	#ifdef __cplusplus
	extern "C" {
	#endif
		
	#include "stdint.h"
  #include "main.h"

	class CAN_Message
	{
		private:
			
		
		public:
			
		  bool     ID_isExtended;
			uint32_t ID;
			uint8_t  Length;
			uint8_t  Data[8];
			uint64_t timestamp_ns=0;
			
		void Parse_FDCAN_RxHeader(FDCAN_RxHeaderTypeDef& RxHeader)
		{
			ID_isExtended = RxHeader.IdType == FDCAN_EXTENDED_ID;
			ID            = RxHeader.Identifier;
			Length        = RxHeader.DataLength / FDCAN_DLC_BYTES_1;
		}
		
		//FDCAN_TxHeaderTypeDef
		FDCAN_TxHeaderTypeDef Get_TxHeader()
		{
			FDCAN_TxHeaderTypeDef TxHeader = {0};
			TxHeader.Identifier = ID;
			TxHeader.IdType = ID_isExtended?FDCAN_EXTENDED_ID:FDCAN_STANDARD_ID;
			TxHeader.TxFrameType = FDCAN_DATA_FRAME;
			TxHeader.DataLength = FDCAN_DLC_BYTES_1 * Length;
			TxHeader.ErrorStateIndicator = FDCAN_ESI_ACTIVE;
			TxHeader.BitRateSwitch = FDCAN_BRS_OFF;
			TxHeader.FDFormat = FDCAN_CLASSIC_CAN;
			TxHeader.TxEventFifoControl = FDCAN_NO_TX_EVENTS;
			TxHeader.MessageMarker = 0;
			return TxHeader;
		}
		
			
	};

	#ifdef __cplusplus
	}
	#endif

#endif
