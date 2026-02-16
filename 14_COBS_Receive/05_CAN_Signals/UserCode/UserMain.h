#ifndef   __USERMAIN_H // Header-Guard
	#define __USERMAIN_H
	
	#include "main.h"
	void  Task1(float T);
	void  Task2(float T);
	
	#ifdef __cplusplus
	 extern "C" { // Kompiliert die C++-Funktionen setup,loop so,
							  // sodass diese aus einem C-Programm aufrufbar sind
	#endif
		void  setup();// Deklaration der Funktion setup()
		void  loop();
	#ifdef __cplusplus
	 }
	#endif

#endif

	 