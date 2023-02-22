#include <SPI.h>
#ifdef __AVR_ATmega2560__
  const byte CLOCKOUT = 11;  // Mega 2560
#else
  const byte CLOCKOUT = 9;   // Uno, Duemilanove, etc.
#endif

// Functions
void send(int channel, int V);
void useInternalRefVoltage();
void clearVoltages();
void triggerCam();
byte getInputNumber();
int getInputVar(int length);
void fastTransition(int start, int end, uint32_t* delayMus);
void slowTransition(int start, int end, int direction, int delayMs);
void setPosition();
void scan();
bool timeCalibration();
int findMaxPicPos();
int findMinPicPos();
int opticalTest();
int picRow(int maxPicPos, int minPicPos);

// Constants (only adjustable here)
int baudrate = 9600;
int state = 0;	// indicates the current state of the hardware controller
int nullPos = 1947; // 0.0V position of enhanced output, may be different with different setup
int galvoMeasurePin = 4;
int DACChannel = 0;	// DAC channel that is used for output (here 0 -> channel A)
long int tSingleSend = 24;	// time required in µs to use the send method once to change DAC output voltage
long int tInitial = 340;	// a fixed time interval that is used to start the galvanometer before the actual picture starts to minimize inertial effects
long int tInitialDelay = 10;	// fixed delay that for the use case above


// Variables (will be overwritten by input from serial port)
int mode; // 2 eq running, 3 eq calibration
int camTrigPin;	// pin that is used to trigger camera
int camTrigPolarity; // 1 eq trigger on rising curve, 2 eq trigger on falling curve
int maxSteps = 30;	// maximum step count until calibration will be cancelled, if not found

int highPos = 4000;	// galvanometer input that generates the maximum input voltage
int midPos = 1950;	// galvanometer input that generates the middle of the picture. Is calculate from the maximum and minimum image positions
int lowPos = 0100;	// galvanometer input that generates the minimum input voltage

int maxPicPos = 3400;	// galvanometer input that generates the hightest position in the picture
int minPicPos = 0500;	// galvanometer input that generates the lowest position in the picture

long int ROI = 2900;	// region of interest. The region between maxPicPos and minPicPos
long int lineTime = 100; // line time of the camera. The time the camera needs from one line to the next in rolling shutter mode
long int expLines = 100; // exposure lines of the camera. The number of lines in the camera that are exposed simultaneously
long int picHeight = 2048;	// number of pixels in the resulting image
long int calibThreshold = 1500;	// maximum time in µs that the sought calibration may deviate from the optimal time.

// Calculated Variables
int interPos;		// position that is located slightly above the maxPicPos and is used with tInitial to start the run the galvanometer before the actual picture starts
long int factor;	// deprecated: A factor that is used rectify camera bugs
long int tAll;		// overall time from start of the image to image readout
long int tTrig;		// time the galvanometer waits from start of the camera to starting the run. Insures that the laser is located in the middle of the exposed block
long int tFirstTrigger;	// similar to tTrig, but considers the jitter and the start of tInitial
long int tJitter;	// estimated value of the camera jitter.

// Measured Variables
long int t1;	// timestamp from the start of a routine
long int t2;	// timestamp from the end of a routine
long int tFinal;	// delay in µs between every iteration in a scan routine. Controls the speed of the galvanometer
byte number;	// byte read from the serial port


/*
	Starts the serial connection with the pc and the spi connection with the DAC and initializeses. Is called first thing when starting the hardware controller
*/
void setup() {
  Serial.begin(baudrate);
  SPI.begin();
  SPI.setClockDivider(SPI_CLOCK_DIV4);
  SPI.setDataMode(SPI_MODE1);
  useInternalRefVoltage();
  send(DACChannel, nullPos); // 0.0V Position for current setup enhanced output
}


/*
	Method that describes the main sequence of the program. Is called after setup is done
*/
void loop() {
  number = 0;
	if (state == 0) {
    // checks for the right program on both sides
		if (Serial.available() > 0) {
		  byte number = getInputNumber();
		  if (number == 0) { // 0 is verification command from computer
			  Serial.println("Theben"); // writes name of the right program onto serial port
			  state = 1;
		  } else if (number == 9) { // not used in program. Sets the position of the galvanometer for analysis purposes
			  setPosition();
		  } else { // computer is in a false state or is running a wrong program
			  Serial.println("Wrong Input");
		  }
		}
	}
	else if (state == 1) {
		if (Serial.available() > 0) {
			number = getInputNumber();
			if (number == 1) {	// Computer sends current state of the machine.
				// Get all vars from serial connection
				mode = getInputVar(1);
				camTrigPin = getInputVar(1);
				camTrigPolarity = getInputVar(1);
				if (camTrigPolarity == 2) {
				  pinMode (camTrigPin, OUTPUT);
				  digitalWrite(camTrigPin, HIGH);
				}
				highPos = getInputVar(4);
				lowPos = getInputVar(4);
				int lineTime_length = getInputNumber();
				lineTime = getInputVar(lineTime_length);
				int expLines_length = getInputNumber();
				expLines = getInputVar(expLines_length);
				int picHeight_length = getInputNumber();
				picHeight = getInputVar(picHeight_length);
				int calibThreshold_length = getInputNumber();
				calibThreshold = getInputVar(calibThreshold_length);
				int maxSteps_length = getInputNumber();
				maxSteps = getInputVar(maxSteps_length);
				interPos = maxPicPos + 10;
				if (mode == 2) { // if mode is running, get additional variables of the parameter file
					maxPicPos = getInputVar(4);
					minPicPos = getInputVar(4);
					int roi_length = getInputNumber();
					ROI = getInputVar(roi_length);
					int tTrig_length = getInputNumber();
					tTrig = getInputVar(tTrig_length);
					int tFinal_length = getInputNumber();
					tFinal = getInputVar(tFinal_length);
					state = 2; // go to running mode state
				} else if (mode == 3) { // calibration mode
					state = 3; // go to calibrabtion mode state
				}
				Serial.println("received");
			} else if (number == 0) { // State was already set but is still not verified in program
				Serial.println("Theben");
			} else if (number == 4) { // 4 is exit command
				endCon();
			} else {  // Unknown command
				state = 0;
			}
		}
	}
	else if (state == 2) { // running mode
		if (Serial.available() > 0) {
			number = getInputNumber();
			if (number == 2) { // 2 is start command
				Serial.println("received");
				delay(1000);
				scan();
			} else if (number == 4) { // 4 is exit command
				endCon();
			} else { // Unknown command
				state = 0;
			}
		}
	}
	else if (state == 3) { // calibration mode
		if (Serial.available() > 0) {
			number = getInputNumber();
			if (number == 2) { // 2 is start command
				Serial.println("received");
        intensityTest();
				maxPicPos = findMaxPicPos();
				Serial.println(maxPicPos);
        delay(1000);
				minPicPos = findMinPicPos();
				Serial.println(minPicPos);
				if (maxPicPos == -1 || minPicPos == -1) {
          // finding maxPicPos/ minPicPos failed.
					state = 0;
				} else {
					if (opticalTest() == 1) {
						if (picRow(maxPicPos, minPicPos) == 1) {
							if (timeCalibration()) {
                // calibration successful
								Serial.println(tFinal);
								Serial.println(tTrig);
                delay(100);
                // Start from beginning now in running mode
								state = 0;
							} else {
								// no calibration found
								Serial.println("-1");
								Serial.println("-1");
							}
						} else { // picRowTest failed
							state = 0;
						}
					} else { // opticalTest failed
						state = 0;
					}
				}
			} else if (number == 4) { // 4 is exit command
				endCon();
			} else { // Unknown command
				state = 0;
			}
		}
	}
}


/*
  Stops serial connection and resets settings.
*/
void endCon() {
	state = 0;
	triggerCam(); // release camera from blocked state
	Serial.end();
	send(DACChannel, nullPos); // reset position
}


/*
  Sends a given voltage to the given chanel of the DAC
*/
void send(int channel, int V) {
  digitalWrite(SS, LOW); // prepare command (Select Slave)
  byte commandb1 = 0x03; // command 0x03 -> set voltage to particular channel (-> see pmoda4 datasheet p. 23 & manual p. 2)
  // encode data bits:
  byte commandb2 = (channel << 4) | ((V & 0x0F00) >> 8);
  byte commandb3 = V & 0x0FF;
  byte commandb4 = 0x00;
  // send command:
  SPI.transfer(commandb1);
  SPI.transfer(commandb2);
  SPI.transfer(commandb3);
  SPI.transfer(commandb4);
  digitalWrite(SS, HIGH); // finish command (Select Slave)
}


/*
  Sends a command to the DAC to use hardware controller 5V internal reference voltage
*/
void useInternalRefVoltage() {
  digitalWrite(SS, LOW); // prepare command (Select Slave)
  byte commandb1 = 0x08; // command 0x08 -> use internal reference voltage (-> see pmoda4 datasheet p. 23)
  byte commandb2 = 0x00;
  byte commandb3 = 0x01; // 0x01 -> 'Reference on'
  // send command:
  SPI.transfer(commandb1);
  SPI.transfer(commandb2);
  SPI.transfer(commandb2);
  SPI.transfer(commandb3);
  digitalWrite(SS, HIGH); // finish command (Select Slave)
}


/*
  Clears DAC voltage to 0V
*/
void clearVoltages() {
  send(0x0F, 0x000);
}


/*
  Sends a TTL 5V pulse to given pin with given polarity to trigger camera
*/
void triggerCam() {
  pinMode (camTrigPin, OUTPUT);
  if (camTrigPolarity == 1) {
	  digitalWrite(camTrigPin, HIGH);
	  digitalWrite(camTrigPin, LOW);
  } else {
	  digitalWrite(camTrigPin, LOW);
	  digitalWrite(camTrigPin, HIGH);
  }
}


/*
  Recieves a single byte from the serial port.
  Converts this byte to an integer (using offset)
*/
byte getInputNumber() {
  while (Serial.available() == 0) {} // waits for input on serial port
  byte input = Serial.read();
  return (input - 48); // converts byte to int
}


/*
  Recieves bytes of given length from the serial port.
  Converts the input to a multi digit integer (using offset)
*/
int getInputVar(int length) {
  byte valueInput[length];
  int value = 0;
  while (Serial.available() == 0) {} // waits for input on serial port
  Serial.readBytes(valueInput, length);
  int size = sizeof(valueInput)/sizeof(valueInput[0]);
  for (int i = 0; i < size; i++) {
    value = value * 10 + valueInput[i] - 48; // converts bytes to int respecting their importance
  }
  return value;
}


/*
  Sends all values from start to end to DAC using send with a delay of delayMus in µs.
  Can be cancelled by writing '4' into the serial port. -> See delay_with_cancel()
*/
void fastTransition(int start, int end, uint32_t* delayMus) {
  for (int i = start; i > end; i--) {
    send(DACChannel, i);
    delay_with_cancel(delayMus);
  }
}


/*
  Sends all values from start to end to DAC using send with a delay of delayMs in ms.
  The direction is either -1 -> descending or +1 -> ascending.
*/
void slowTransition(int start, int end, int direction, int delayMs) {
  if (direction == -1) {
    for (int i = start; i > end; i--) {
      send(DACChannel, i);
      delay(delayMs);
    }
  } else {
    for (int i = start; i < end; i++) {
      send(DACChannel, i);
      delay(delayMs);
    }
  }
}


/*
  Sets the DAC to given Position. Can be used to determin highest and lowest positions
*/
void setPosition() {
	Serial.println("Type in voltage value (0000..4095):");
	int value = getInputVar(4);
	send(DACChannel, value);
}


// Code from Marcel Mueller's ArduinoLightSourceControl
/*
  Delays in microseconds. Can be cancelled by writing '4' onto serial port
*/
uint8_t delay_with_cancel(uint32_t* time) {
  uint8_t ret = 0;
  asm(
    "ld r24, Z+ \n  "  // load the counter
    "ld r25, Z+ \n  "
    "ld r26, Z+ \n  "
    "ld r27, Z  \n  "
    "ldi r16, '4' \n"  // load '4' into r16

    // this is the main delay loop, taking 16 cycles (thus 1us @ 16 Mhz)
    "intr_loop_start%=: \n "     // +0 - busy loop starts here
    "sbiw r24, 1 \n"             // +2 - dec part lo,hi
    "sbci r26, 0 \n"             // +3 - dec byte 2
    "sbci r27, 0 \n"             // +4 - dec byte 3
    "breq intr_loop_done%= \n"   // +5 - if all counter bytes == 0, jump out of loop
    "lds r17, %[uartstate] \n"   // +7 - load uart status into r17
    "sbrc r17, %[rxbit] \n"      // +8 - skip next instruction if no data was received
    "lds r17, %[uartdata] \n"    // +10 - load current UART data into r17
    "nop\n nop\n nop\n "         // +13 - waste 3 cycles
    "cpse r17,r16 \n"            // +14 - skip the jump to loop start if r17 (data) == r16 ('x')
    "rjmp intr_loop_start%= \n"  // +16 - jump into loop start

    // we arrive here if the loop was canceled
    "ldi %[ret], 1 \n"   // load the return value 1
    "rjmp intr_end%=\n"  // jump to end of asm

    // we arrive here if the loop counter reached 0
    "intr_loop_done%=:\n"
    "ldi %[ret], 0 \n"

    // target to end the routine
    "intr_end%=:\n"
    : [ret] "=d"(ret)
    : "z"(time), [uartstate] "m"(UCSR0A), [rxbit] "M"(RXC0), [uartdata] "m"(UDR0)
    : "r24", "r25", "r26", "r27", "r16", "r17");

  return ret;
}


/*
  Routine for taking a picture in lightsheet mode with given parameters
*/
void scan() {
	pinMode(galvoMeasurePin, OUTPUT); // galvoMeasurePin indicates when the relevant (in picture) positions are passed through
	tJitter = 2 * lineTime; // camera jitter is between 1 and 2.5 times the line_time. 2 times is enough for a rough estimate
	tFirstTrigger = tTrig - tJitter - tInitial;
	slowTransition(nullPos, highPos, 1, 1);
	slowTransition(highPos, interPos, -1, 1);				// bring galvo in starting position
	delay(100);
	triggerCam();
	t1 = micros();											// measure time
	delay_with_cancel(&tFirstTrigger);						// wait until galvanometer position is in the middle of the shutter
	fastTransition(interPos, maxPicPos, &tInitialDelay);	// starts the galvanometer tInitial µs before the actual picture to minimize inertial effects
	digitalWrite(galvoMeasurePin, HIGH);					// output is set high to indicate starting of the actual curve
	fastTransition(maxPicPos, minPicPos, &tFinal);			// actual curve
	digitalWrite(galvoMeasurePin, LOW);						// output is set low to indicate ending of the actual curve
	delay_with_cancel(&tTrig);
	t2 = micros();											// measure time
	fastTransition(minPicPos, lowPos, &tFinal);				// prevents galvanometer stop abruptly
	slowTransition(lowPos, nullPos, 1, 1);					// reset to null position
	Serial.println(t2 - t1);								// write time difference onto serial port
}


/*
  Routine for time calibration. Calculates the amount of time the camera needs,
  estimates a number for the speed of the galvanometer (tFinal) and optimizes the time
  through running the galvanometer mulitple times. Finally evaluates if the calibration
  is sufficient for the purpose.
*/
bool timeCalibration() {
  number = getInputNumber();
  if (number == 6) { // 6 is trigger command
    Serial.println("received");
  } else {
    return -1;
  }

	tJitter = 2 * lineTime;
	tTrig = round(0.5 * expLines * lineTime);
	tFirstTrigger = tTrig + tJitter - tInitial;
	if (tFirstTrigger < 0) {
		Serial.println("200"); //Errorcode 200 -> Illegal camera setup
    return false;
	}

	long int tAll = (picHeight + expLines) * lineTime + (2 * tTrig) + tJitter;	// overall time needed
	long int tSend = tSingleSend * ROI;	// time needed if tFinal was 0. Overall time (tAll) cannot be smaller than tSend
	if (tAll < tSend) {
		Serial.println("200");	//Errorcode 200 -> Illegal camera setup
		return false;
	}

  Serial.println("1");	// no error code -> program continues

	long int tLin = tAll - (2 * tTrig);	// time the galvanometer has to move inbetween the maxPicPos and minPicPos
	long int tDelay = tLin - tSend;		// time difference between the minimum possible galvanometer speed (tFinal = 0) and the optimal time
	tFinal = static_cast<int>(round(tDelay / static_cast<float>(ROI)));	// tDelay for every value between maxPicPos and minPicPos (ROI) is the estimated tFinal

	long int tMeasure;	// measured time
	long int tDiff;		// time difference between the optimal time and the measured time
	long int tDiffOld = 0;	// time difference of last tFinal
	long int increment;	// indicates if the speed is too fast (-1) or too slow (1)
	bool condition = true;
	int step = 0;	// number of runs
	while (true) {
		// scanning rountine without triggering cam:
		slowTransition(nullPos, highPos, 1, 1);
		slowTransition(highPos, interPos, -1, 1);
		delay(1000);
		t1 = micros();
		delay_with_cancel(&tFirstTrigger);
		fastTransition(interPos, maxPicPos, &tInitialDelay);
		fastTransition(maxPicPos, minPicPos, &tFinal);
		delay_with_cancel(&tTrig);
		t2 = micros();
		fastTransition(minPicPos, lowPos, &tFinal);
		slowTransition(lowPos, nullPos, 1, 1);

		tMeasure = t2 - t1;
		tDiff = tAll - tMeasure;
		if (step == 0) {
		  if (tDiff < 0 && abs(tDiff) < calibThreshold) {
			break;			// estimated tFinal is optimal tFinal
		  }
		  if (tDiff >= 0) {
			increment = 1;	// galvanometer speed too slow
		  } else if (tDiff < 0) {
			increment = -1;	// galvanometer speed too fast
		  }
		}
		// find the smallest negative time difference to the optimal time difference:
		if (increment < 0 && tDiff > 0) {
		  tFinal++;
		  tDiff = tDiffOld;
      Serial.println("finished");
		  break;
		}
		if (increment > 0 && tDiff <= 0) {
      Serial.println("finished");
		  break;
		}
		tFinal = tFinal + increment;	// adjust tFinal
		step++;
		tDiffOld = tDiff;
		if (step >= maxSteps) {
		  break;	// no optimal calibration found in number of maxSteps
      Serial.println("finished");
		}
    Serial.println("received");
	}
	Serial.println(tFinal);		// write final tFinal onto serial port
  Serial.println(abs(tDiff));
	if (abs(tDiff) > calibThreshold) {
		Serial.println("-200"); //Errorcode -200 -> No proper calibration found
		return false;
	} else {
		Serial.println("1"); // -> Proper calibration found
		return true;
	}
}

/*
  Finds position that has its maximum in the 0. pixel.
  Starts at the highest position and decreases with 10 galvanometer steps (~0,0061 V)
*/
int findMaxPicPos() {
	slowTransition(nullPos, highPos, 1, 1);	// start at highest position
	int pos = highPos;
	while(true) {
		number = getInputNumber();
		if (number == 6) { // 6 is trigger command
			Serial.println("received");
			pos = pos - 10;
			send(DACChannel, pos);
			delay (1000);
			triggerCam();
		} else if (number == 7) { // 7 is finished command
			Serial.println("received");
			slowTransition(pos, nullPos, -1, 1);
			return pos;
		} else if (number == 9) { // 9 is reject command
      Serial.println("received");
      pos = highPos;          // reset position, try again
    } else if (number == 4) { // 4 is exit command
			return -1;
		} else { // Unknown command
			return -1;
		}
	}
}


/*
  Finds position that has its maximum in the 2047. pixel.
  Starts at the lowest position and increases with 10 galvanometer steps (~0,0061 V)
*/
int findMinPicPos() {
	slowTransition(nullPos, lowPos, -1, 1);
	int pos = lowPos;
	while(true) {
		number = getInputNumber();
		if (number == 6) { // 6 is trigger command
      Serial.println("received");
			pos = pos + 10;
			send(DACChannel, pos);
			delay (1000);
			triggerCam();
		} else if (number == 7) { // 7 is finished command
      Serial.println("received");
			slowTransition(pos, nullPos, 1, 1);
			return pos;
    } else if (number == 9) { // 9 is reject command
      Serial.println("received");
      pos = highPos;          // reset position, try again
		} else if (number == 4) { // 4 is exit command
			return -1;
		} else { // Unknown command
			return -1;
		}
	}
}


/*
  Takes a picture in null position. Pc will analyze
  the intensity of the laser.
*/
int intensityTest() {
	number = getInputNumber();
	if (number == 6) { // 6 is trigger command
    Serial.println("received");
		send(DACChannel, nullPos);
    delay(1000);
		triggerCam();
	} else if (number == 4) { // 4 is exit command
		return -1;
	} else { // Unknown command
		return -1;
	}
}


/*
  Takes a picture in a position received through the serial port.
  This picture will be analyzed by the pc and will be confirmed or rejected.
*/
int opticalTest() {
  midPos = getInputVar(4);
  Serial.println("received");
	number = getInputNumber();
	if (number == 6) { // 6 is trigger command
    Serial.println("received");
		send(DACChannel, midPos);
    delay(1000);
		triggerCam();
    delay(1000);
		number = getInputNumber();
    if (number == 8) { // 8 is confirmation command
      Serial.println("received");
	    send(DACChannel, nullPos);	// reset position
      return 1;
    } else {  // rejected
      Serial.println("received");
	    send(DACChannel, nullPos);	// reset position
      return -1;
    }
	} else if (number == 4) { // 4 is exit command
		return -1;
	} else { // Unknown command
		return -1;
	}
}


/*
  Takes multiple pictures starting at the 0. pixel to the 2047. pixel in
  galvanometer steps of 100 (~0,0611 V). The pc compares galvanometer positions
  to picture position too see if the galvanometer runs correct according to the camera.
  This will only detect non dynamical issues.
*/
int picRow(int maxPicPos, int minPicPos) {
	slowTransition(nullPos, maxPicPos, 1, 1);
	int pos = maxPicPos;
	while(true) {
		number = getInputNumber();
		if (number == 6) { // 6 is trigger command
      Serial.println("received");
			pos = pos - 100;
			if (pos < minPicPos) {
				pos = minPicPos;
			}
			send(DACChannel, pos);
			delay (1000);
			triggerCam();
		} else if (number == 7) { // 7 is finished command
      Serial.println("received");
			slowTransition(pos, nullPos, 1, 1);	// reset position
      return 1;
		} else if (number == 4) { // 4 is exit command
			return -1;
		} else { // Unknown command
			return -1;
		}
	}
}
