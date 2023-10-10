""" Reads the time intervals from TDC7200 chip with Raspberry Pi.
    The pinout is set as for the TDC7200 PDC by Justus Liebig Uni, Giessen. See https://oshwlab.com/hgzaunick/RPi-TDC

"""

import tdc7200
import os
import pandas as pd
from time import sleep
from datetime import datetime, timezone
from GPSTimeConv import GPSTimeConv
from dailylogfile import DailyLogFile, DayNumber

logfile = DailyLogFile(ftype='csII_Trimble', columns=['MJD', 'UTC', 'TI'], daynumbertype='mjd', offset_s=18, immediate_flush=False,
                       template='{0:.8f}\t{1:.6f}\t{2:.3f}\n')

tdc = tdc7200.TDC7200() # Create TDC object with SPI interface.
#tdc.initGPIO() # Set pin directions and default values for non-SPI signals.
#tdc.initGPIO(enable=40,trig1=15,int1=38,start=29,stop=None,verbose=True)
tdc.initGPIO(enable=40,trig1=15,int1=38,start=None,stop=None,verbose=True)

tdc.set_SPI_clock_speed(20000000)
tdc.on()
tdc.configure(clk_freq=10000000, 
	meas_mode=1, falling=False, num_stop=1, clock_cntr_stop=0, calibration2_periods=10, timeout=0.000001)

cnt = 0
tss = datetime.now()
try:
    while True:
        status = tdc.measure(simulate=False)
        if status < 6:
            # data is a tuple (times, normLSB, time_counts, clock_counts, calibrations, interrupt_mask)
            data = tdc.read_data()
            utc = datetime.utcnow().timestamp()
            mjd = DayNumber.mjd(utc, return_int=False)
    #        print("{} {}".format(datetime.datetime.utcnow().timestamp(), data))
            if data and data[0] and data[0][0]:
                print(logfile._template.format(mjd, utc, data[0][0]*1e9), end='')
                logfile.logdata([mjd, utc, data[0][0]*1e9])
                #fout.write("{0:.8f}\t{1:.6f}\t{2:.3f}\n".format(ts, uts, data[0][0]*1e9))
    #            print("{0:.3f} {1:.2f} {2}".format(datetime.utcnow().timestamp(), data[0][0]*1e9, data))
                cnt += 1
                if (cnt == 10000):
                    raise KeyboardInterrupt(f"CNT: {cnt} done")

            else:
                print("{0:.8f}\tN/A".format(mjd))
                logfile.logdata([mjd, None, None])
        else:
            print("Something went wrong (status: {})".format(status))
        #tdc.clear_status()
except KeyboardInterrupt:
    print(f"done in {(datetime.now()-tss).total_seconds()}")
    tdc.off()
    pass        
except Exception as e:
    print(f"{e}")
finally:
    print("DONE")
