#include "HTLWYSerial.h"



void HTLWYSerial::Init()
{

}


void HTLWYSerial::computeReceive()
{
	while(USART3->ISR & USART_ISR_RXNE_RXFNE) // Überprüfung ob Bit "RXNE (RX-not-empty) in ISR-Register gesetzt ist
	{
		RxBuffer.push(USART3->RDR); //Einfügen des "RDR"-Inhalts(Receiver-DataRegister) (1 Byte -> 1 Char) in das RX-FIFO
	}
}

void HTLWYSerial::computeTransmit()
{
	while(TxBuffer.GetDataCount() > 0 && (USART3->ISR & USART_ISR_TXE_TXFNF))
	{
		TxBuffer.pop((char*)(&USART3->TDR));
	}
}


