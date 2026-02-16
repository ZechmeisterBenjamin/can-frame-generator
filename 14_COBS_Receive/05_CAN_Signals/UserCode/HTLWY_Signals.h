#pragma once

#include "HTLWYCAN.h"
#include "string.h"
#include "usart.h" 
#include "fdcan.h"
#include "main.h"
#include "HTLWYSerial.h"

extern "C" uint64_t GetTimestamp_ns(void);
class SignalLinkedList;  

class SignalInterface
{
	public:
		SignalInterface(SignalLinkedList *list, bool transmit, uint32_t id);
	
		SignalLinkedList *list;
	
		uint32_t				 ID						= 0b11111111111111111111111111111uL;
		SignalInterface *next    			= nullptr;
		
	  float t_lastUpdate = 0;
		bool 						 transmit			= false;
	
	  // This Interface Methods must be implemented
		virtual void cyclic(float T);	
		virtual void parseFromCanMessage(uint8_t* data, uint8_t length){}
		virtual void TransmitInCanMessage(){}

		// Signal2Signal assignment is prohibited
		SignalInterface& operator=(SignalInterface const&) = delete;
		
};

class SignalLinkedList
{
	private:
		UART_HandleTypeDef *monitorUart; // Pointer auf das UART Handle

		uint64_t GetTimestamp_ns() {
			return (uint64_t)HAL_GetTick() * 1000000ULL;
		}
	
		uint32_t calculateCRC32(const uint8_t* data, size_t length) {
			uint32_t crc = 0xFFFFFFFF;
			for (size_t i = 0; i < length; i++) {
				crc ^= data[i];
				for (int j = 0; j < 8; j++) {
					if (crc & 1) crc = (crc >> 1) ^ 0xEDB88320;
					else crc >>= 1;
				}
			}
			return ~crc;
		}

		/**
		 * @brief Kodiert Daten mittels Consistent Overhead Byte Stuffing (COBS).
		 * @param input Pointer auf die Rohdaten.
		 * @param length Länge der Rohdaten.
		 * @param output Pointer auf den Zielbuffer (Muss groß genug sein: len + len/254 + 1).
		 * @return Größe des kodierten Pakets (ohne abschließendes 0x00, das muss extern angefügt werden).
		 */
		size_t COBS_Encode(const uint8_t* input, size_t length, uint8_t* output) {
			size_t read_index = 0;
			size_t write_index = 1;
			size_t code_index = 0;
			uint8_t code = 1;

			while (read_index < length) {
				if (input[read_index] == 0) {
					output[code_index] = code;
					code = 1;
					code_index = write_index++;
					read_index++;
				} else {
					output[write_index++] = input[read_index++];
					code++;
					if (code == 0xFF) {
						output[code_index] = code;
						code = 1;
						code_index = write_index++;
					}
				}
			}
			output[code_index] = code;
			return write_index;
		}

	
	public:
		HTLWYCAN *can;
		
		// Konstruktor erweitert um UART Handle
SignalLinkedList(HTLWYCAN *can, UART_HandleTypeDef *huart = &huart3) { 
			this->can = can;
			this->monitorUart = huart;
		}
	
		SignalInterface *first 					= nullptr;
		SignalInterface *last  					= nullptr;
		uint32_t 				 Signalcount 		= 0;
	
		void appendSignal(SignalInterface &signal);

		/**
		 * @brief Serialisiert, kodiert und sendet einen CAN Frame über UART.
		 * Format vor Encoding: [ID 4B][Len 1B][Payload nB][Time 8B][CRC 4B]
		 */
		void ForwardCANFrameToSerial(uint32_t canId, bool isExtended, uint8_t* data, uint8_t len) {
			if (monitorUart == nullptr) return;

			// Max Buffer Berechnung:
			// Header(4) + Len(1) + MaxData(8) + Time(8) + CRC(4) = 25 Bytes Raw
			// COBS Overhead ~ 1 Byte. Puffergröße 40 ist sicher.
			uint8_t rawBuffer[32];
			uint8_t encodedBuffer[40];
			size_t idx = 0;

			// 1. Identifier (Bit 31 = Extended Flag)
			uint32_t id_proc = canId;
			if (isExtended) id_proc |= (1UL << 31);
			memcpy(&rawBuffer[idx], &id_proc, 4); idx += 4;

			// 2. Data Length
			rawBuffer[idx++] = len;

			// 3. Payload (Variable Länge!)
			if (len > 0 && data != nullptr) {
				memcpy(&rawBuffer[idx], data, len); 
				idx += len;
			}

			// 4. Timestamp (64 Bit ns)
			uint64_t timestamp = GetTimestamp_ns();
			memcpy(&rawBuffer[idx], &timestamp, 8); idx += 8;

			// 5. Checksum (CRC32 über alles bisherige)
			uint32_t crc = calculateCRC32(rawBuffer, idx);
			memcpy(&rawBuffer[idx], &crc, 4); idx += 4;

			// 6. COBS Encoding
			size_t encodedLen = COBS_Encode(rawBuffer, idx, encodedBuffer);

			// 7. Frame Delimiter
			encodedBuffer[encodedLen++] = 0x00;

			
			HAL_UART_Transmit(monitorUart, encodedBuffer, (uint16_t)encodedLen, 2); 
		}
	
		void cyclic(float T){
			// Check for new CAN Messages and parse if Identifier is known
			static CAN_Message msg;
			while(can->RxBuffer.pop(&msg)){
				
				// Empfangene Nachricht an PC senden
				ForwardCANFrameToSerial(msg.ID, msg.ID_isExtended, msg.Data, msg.Length);
				
				SignalInterface* act = first;
				while(act != nullptr) {
					if(act->ID == msg.ID) act->parseFromCanMessage(msg.Data, msg.Length);
					act = act->next;
				}
			}
			
			// Call cyclic from all LinkedList-Members
			SignalInterface* act = first;
			while(act != nullptr){
				act->cyclic(T);
				act = act->next;
			}
		}
};

class BoolSignal : public SignalInterface
{
	public:
		// Constructors
		BoolSignal(SignalLinkedList *list, bool transmit, uint32_t id) : SignalInterface(list, transmit, id){}
		BoolSignal(SignalLinkedList *list, uint32_t id) : BoolSignal(list, false, id){}
		
		// BoolSignal Specific Member
		bool 	 Digital = false;
		bool   PositiveEdge;
		bool   NegativeEdge;

		bool 	 mDigital = Digital;
		
		// BoolSignal Specific Operators
		void operator = (const bool val) { 
			Digital = val;
		}
		
		void operator = (const BoolSignal DSig) { 
			Digital = DSig.Digital;
		}
		
		operator bool(){return Digital;}

		inline void toggle() { Digital = !Digital;}
		
		// Interface overrides
		virtual void cyclic(float T) override
		{
			this->SignalInterface::cyclic(T);
			
			if(Digital != mDigital) TransmitInCanMessage();
			
			PositiveEdge = Digital && !mDigital;
			NegativeEdge = !Digital && mDigital;
			
			mDigital = Digital;
		}		
		
		virtual void parseFromCanMessage(uint8_t* data, uint8_t length)  override{
			if(data[0] == 0){ // MessageTypeIdentifier is data[0] -> 0..Bool
				Digital = data[1];
				t_lastUpdate = 0;
			}
		}	
		
		virtual void TransmitInCanMessage() override
		{
			if(!transmit) return;
			static CAN_Message message;
			
			message.ID_isExtended =	true;
			message.ID = this->ID;
			message.Length = 2; // MessageTypeIdentifier is data[0] -> 0..Bool, 1.. int32
			message.Data[0] = 0;
			message.Data[1] = Digital?0x01:0x00;
			
			this->list->can->TxBuffer.push(message);
			
			this->list->ForwardCANFrameToSerial(message.ID, message.ID_isExtended, message.Data, message.Length);		}
		
};


class Int32Signal : public SignalInterface
{
	public:
		// Constructors
		Int32Signal(SignalLinkedList *list, bool transmit, uint32_t id) : SignalInterface(list, transmit, id){}
		Int32Signal(SignalLinkedList *list, uint32_t id) : Int32Signal(list, false, id){}
		
		// BoolSignal Specific Member
		int32_t 	 Value = false;

		int32_t 	 mValue = Value;
		
		// BoolSignal Specific Operators
		void operator = (const int32_t val) { 
			Value = val;
		}
		
		void operator = (const Int32Signal ISig) { 
			Value = ISig.Value;
		}
		
		operator int32_t(){return Value;}

		
		// Interface overrides
		virtual void cyclic(float T) override
		{
			this->SignalInterface::cyclic(T);
			
			if(Value != mValue) TransmitInCanMessage();
			
			mValue = Value;
		}		
		
		
		inline void increment(int8_t amount){
			Value += amount;
		}
		
		virtual void parseFromCanMessage(uint8_t* data, uint8_t length)  override{
			if(data[0] == 1 && length == 5){ // MessageTypeIdentifier is data[0] -> 1..Integer
				Value  = (uint32_t)data[1] << 24;
        Value |= (uint32_t)data[2] << 16;
        Value |= (uint32_t)data[3] << 8;
        Value |= (uint32_t)data[4];
				t_lastUpdate = 0;
			}
		}	
		
		virtual void TransmitInCanMessage() override
		{
			if(!transmit) return;
			static CAN_Message message;
			
			message.ID_isExtended =	true;
			message.ID = this->ID;
			message.Length = 5; 
			message.Data[0] = 1;	// MessageTypeIdentifier is data[0] -> 0..Bool, 1.. int32
			message.Data[1] = (Value >> 24) & 0xFF;
			message.Data[2] = (Value >> 16) & 0xFF;
			message.Data[3] = (Value >> 8)  & 0xFF;
			message.Data[4] = (Value)       & 0xFF;
			
			this->list->can->TxBuffer.push(message);
			
			this->list->ForwardCANFrameToSerial(message.ID, message.ID_isExtended, message.Data, message.Length);		}
		
};


class MessageBuffer : public SignalInterface
{
	public:
		// Constructors
		MessageBuffer(SignalLinkedList *list, uint32_t id) : SignalInterface(list, false, id){}
		
		// MessageBuffer Specific Member
			RingBuffer<CAN_Message, 8> messages;

		// Interface overrides
		
		virtual void cyclic(float T) override {}
		
		virtual void parseFromCanMessage(uint8_t* data, uint8_t length)  override 
		{
			static CAN_Message msg;
			msg.ID = this->ID;
			msg.ID_isExtended = true;
			msg.Length = length;
			memcpy(msg.Data, data, length);
			this->messages.push(msg);
		}
		virtual void TransmitInCanMessage() override {}
		
		
};



