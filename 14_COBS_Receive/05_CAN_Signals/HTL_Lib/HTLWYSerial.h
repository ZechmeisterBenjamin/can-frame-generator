#ifndef __HTLWYSERIAL_H
	#define __HTLWYSERIAL_H
	
		
	#include "stdint.h"
	#include "main.h"
		
	#include "StringBuffer.h"

	class HTLWYSerial
	{
		private:
			
		
		public:
			StringBuffer<256> TxBuffer;
			StringBuffer<256> RxBuffer;
		
		
		void Init();
		void computeReceive();
		void computeTransmit();
			
			
	};

#endif
