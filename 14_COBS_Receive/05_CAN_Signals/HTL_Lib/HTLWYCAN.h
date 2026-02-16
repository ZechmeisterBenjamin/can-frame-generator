#ifndef __HTLWYCAN_H
	#define __HTLWYCAN_H
	
		
	#include "stdint.h"
	#include "main.h"
		
	#include "fdcan.h"
	#include "CAN_Message.h"
	#include "Ring_Buffer.h"

	class HTLWYCAN
	{
		private:
			uint64_t Overflows = 0;
		
		public:
			RingBuffer<CAN_Message, 32> TxBuffer;
			RingBuffer<CAN_Message, 32> RxBuffer;
		
		
		void Init();
		void computeReceive();
		void computeTransmit();
				
	};

#endif
