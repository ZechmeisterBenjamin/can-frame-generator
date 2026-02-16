#include "HTLWY_Signals.h"



/*--------------SIGNAL INTERFACE-------------------------*/


SignalInterface::SignalInterface(SignalLinkedList *list, bool transmit, uint32_t id)
{
	this->list = list;
	ID = id;
	this->transmit = transmit;
	list->appendSignal(*this);
}

void SignalInterface::cyclic(float T)
{
	t_lastUpdate += T;
	
	if(transmit && t_lastUpdate > 9.9f) TransmitInCanMessage();
}

/*--------------SIGNAL LINKED LIST-------------------------*/

void SignalLinkedList::appendSignal(SignalInterface &signal)
{
  if(first == nullptr)
  {
    first = last = &signal;
    Signalcount = 1;
  }
  else
  {
    last->next = &signal;
		last = &signal;
    Signalcount ++;
  }
}
/*--------------END-------------------------*/



