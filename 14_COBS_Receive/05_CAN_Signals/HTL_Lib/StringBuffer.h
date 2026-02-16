#ifndef __STRINGBUFFER_H
#define __STRINGBUFFER_H

#include "Ring_Buffer.h"

#include "stdio.h"
#include "string.h"
#include <stdarg.h>

template <unsigned int TSize = 256> class StringBuffer :  public RingBuffer<char, TSize>
{
	public:

	  StringBuffer() : RingBuffer<char, TSize>(){} 
			
		bool print(char* txt)
		{
			return this->pushBlock(txt, strlen(txt));
		}
		
		bool printf(const char* format, ...)
		{
			va_list arglist;

			va_start( arglist, format );
			
			char text[256];
			int writtenBytes = vsnprintf(text,256, format, arglist);
				
			va_end( arglist );
			
			return this->pushBlock(text, writtenBytes);
		}
		int ReadAllText(char* buffer, int bufferSize)
		{
			return this->popBlock(buffer, bufferSize);
		}
		
};


#endif
