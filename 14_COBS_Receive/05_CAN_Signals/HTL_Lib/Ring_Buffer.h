#ifndef __RING_BUFFER_H
#define __RING_BUFFER_H


#include <stdint.h>

//RingBuffer<float, 256> myFifo();
//RingBuffer<Fahrzeug, 256> myFifo1();
//RingBuffer<int, 256> myFifo2();

template <typename T, unsigned int TSize> class RingBuffer
{
	public:
	
		RingBuffer()
		{
			Size = TSize;
		}
	
		bool push(T InData)
		{
			uint32_t next = ((write + 1) % Size);
			if (read == next)
				return 0;
			data[write] = InData;
			write = next;
			return 1;
		}
		
		bool pushBlock(T* InData, uint16_t length)
		{
			if(GetFree() < length) return false;
			for(int i = 0; i < length; i++)
			{
				push(InData[i]);
			}
			return true;
		}
		
	    bool pop(T* pOutData)
		{
			if (read == write) return false;
			*pOutData = data[read];
			read = (read+1) % Size;
			return true;
		}
		
		uint16_t popBlock(T pOutData[], uint16_t length)
		{
			uint16_t dataCount = GetDataCount();
			if(dataCount == 0) return 0;
			if(dataCount < length) length = dataCount;
			for(int i = 0; i < length; i++)
			{
				pop(&pOutData[i]);
			}
			return length;
		}
		
		uint32_t GetFree()
		{
			int32_t x = write - read;

			if(x < 0) return Size  - (Size + x);
			else      return Size - x;
		}
		
		uint32_t GetDataCount()
		{
			int32_t x = write - read;

			if(x < 0) return Size + x;
			else      return x;
		}
		
		void clear()
		{
			this->read = this->write;
		}
		
	private: 
	    int32_t read; // zeigt auf das Feld mit dem ältesten Inhalt
		int32_t write; // zeigt immer auf leeres Feld
		uint16_t Size = 0;
		T data[TSize];
		
};
	 

#endif
