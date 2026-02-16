#include "UserMain.h"
#include "stdlib.h"
#include "tim.h"
#include "math.h"
#include "HTLWYSerial.h"
#include "HTLWYCAN.h"
#include "stdlib.h"
#include <inttypes.h>
#include "magic_enum.hpp"
#include "HTLWY_Signals.h"
#include <string.h>

static constexpr float sec = 1;
static constexpr float ms  = sec*0.001f;
static constexpr float us  = ms*0.001f;
static constexpr float ns  = us*0.001f;

HTLWYSerial serial;
HTLWYCAN can;

// struct
// [GENERATED_STRUCT_START]
struct __attribute__((packed)) CanFrame {
    int32_t TestInt;
};
// [GENERATED_STRUCT_END]

//Eingehender Frame
CanFrame inputFrame;

static uint8_t rxBuffer[64]; 
static uint8_t rxIndex = 0;

static uint8_t decodedBuffer[64];


SignalLinkedList canSignals = SignalLinkedList(&can);

BoolSignal buttonSignal = BoolSignal(&canSignals,  true, 1000);

Int32Signal counterSignal  = Int32Signal(&canSignals, true, 2000);


void setup(){ //Definition

	serial.Init();
	can.Init();
	
	htim3.PeriodElapsedCallback = [](TIM_HandleTypeDef* htim)
	{
		serial.computeReceive();
		serial.computeTransmit();
		
		can.computeTransmit();
		can.computeReceive();	
	};
	
	htim17.PeriodElapsedCallback = [](TIM_HandleTypeDef* htim)
	{
		canSignals.cyclic(1.0f/f_Task1);
		Task1(1.0f/f_Task1);
	};
	HAL_TIM_Base_Start_IT(&htim3);
	HAL_TIM_Base_Start_IT(&htim17);

}
class BinarySignal{
	public:
	bool val;
	bool posEdge;
	bool negEdge;
	uint64_t t_pos_cyc = 0;
	uint64_t t_neg_cyc = 0;
	float t_pos;
	float t_neg;
	bool mval;
	bool iniOk=false;
	void compute(float T)
	{
		if(!iniOk) 	posEdge = false;
		else				posEdge = val && !mval;
		if(!iniOk) 	negEdge = false;
		else				negEdge = !val && mval;
		if(!iniOk) 				t_pos_cyc = 0;
		else if(posEdge)	t_pos_cyc = 0;
		else if(val)			t_pos_cyc ++;
		if(!iniOk) 				t_neg_cyc = 0;
		else if(negEdge)	t_neg_cyc = 0;
		else if(!val)			t_neg_cyc ++;
		t_pos= (t_pos_cyc + 0.5f) *T;
		t_neg= (t_neg_cyc + 0.5f) *T;
		mval = val;
		iniOk = true;
	}
};


class DoubleClick{
	public:
			float T_maxPause = 0.25f;
	
			enum class State{ready,click,doubleClick}S;
			enum class Event{None, init, doubleClickEdge, clickEdge,buttonPressed_Edge} E;
			
			bool iniOK = false;
			
			uint64_t btnCnt;
			
			uint64_t t_cyc = 0;
			float t = 0;
			
			//input
			bool buttonPressed_Edge	= false;
			//output
			bool click_Edge				= false;
			bool doubleclick_Edge	= false;

			
			void compute(float T)
			{
				if(!iniOK) 							t_cyc=0;
				else if(E==Event::None) t_cyc++;
				else 										t_cyc =0;
				
				t=(t_cyc+0.5f)*T;
				
				//States/Events calculation
				if			(!iniOK)																		{E = Event::init;								S=State::ready;}
				else if	(S == State::ready && buttonPressed_Edge)		{E = Event::buttonPressed_Edge;	S=State::click;}
				else if	(S == State::click && t	>	T_maxPause)				{E = Event::clickEdge;					S=State::ready;}
				else if	(S == State::click && buttonPressed_Edge)		{E = Event::doubleClickEdge;		S=State::ready;}
				else																								{E = Event::None;}	 	  			/*S = S;*/
				
				click_Edge 				= E == Event::clickEdge;
				doubleclick_Edge 	= E == Event::doubleClickEdge;

				
				iniOK=true;
			}
};
DoubleClick HMI_Button;
BinarySignal button;

void Task1(float T)
{	
	/*bool rawInput = (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_SET);
	
	button.val = rawInput;
	button.compute(T);
	
	buttonSignal = button.val;
	
	
	static float timeAccumulator = 0.0f;
	timeAccumulator += T;
	
	if(timeAccumulator >= 1.0f)
	{
		timeAccumulator -= 1.0f;
		counterSignal.increment(1);
	}*/
	
}


size_t COBS_Decode(const uint8_t* input, size_t length, uint8_t* output) {
    size_t read_index = 0;
    size_t write_index = 0;
    uint8_t code = 0;
    uint8_t i = 0;

    while (read_index < length) {
        code = input[read_index];

        // Fehlererkennung
        if (read_index + code > length && code != 1) return 0;

        read_index++;

        for (i = 1; i < code; i++) {
            output[write_index++] = input[read_index++];
        }
        if (code != 0xFF && read_index != length) {
            output[write_index++] = 0;
        }
    }
    return write_index;
}

void loop()
{
    // Byte-fuer-Byte Auslesen aus dem Ring-Buffer
    while(serial.RxBuffer.GetDataCount() > 0) 
    {
        char c;
        if(serial.RxBuffer.pop(&c)) //
        {
            uint8_t byte = (uint8_t)c;
            
            if (byte == 0x00) { // Code 0 empfangen
                if (rxIndex > 0) {
                    size_t len = COBS_Decode(rxBuffer, rxIndex, decodedBuffer);

                    if (len == sizeof(CanFrame)) { 
                        // Dekodierte Daten in die Struct kopieren
                        memcpy(&inputFrame, decodedBuffer, sizeof(CanFrame));
                    }
                }
                rxIndex = 0;
            } 
            else {
                if (rxIndex < sizeof(rxBuffer)) {
                    rxBuffer[rxIndex++] = byte;
                } else {
                    rxIndex = 0; 
                }
            }
        }
    }
}