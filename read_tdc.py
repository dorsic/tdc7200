import tdc7200
import datetime
import time

tdc = tdc7200.TDC7200() # Create TDC object with SPI interface.
#tdc.initGPIO() # Set pin directions and default values for non-SPI signals.
tdc.initGPIO(enable=13,trig1=15,int1=11,start=29,stop=None,verbose=True)

tdc.set_SPI_clock_speed(20000000)
tdc.on()
tdc.configure(clk_freq=16000000, 
	meas_mode=1,num_stop=1,clock_cntr_stop=0, timeout=0.0001)
tss = datetime.datetime.now()
while True:
    status = tdc.measure(simulate=False)
    if status < 6:
        # (times, normLSB, time_counts, clock_counts, calibrations, interrupt_mask)
        data = tdc.read_data()
#        print("{} {}".format(datetime.datetime.utcnow().timestamp(), data))
        if data[0][0]:
            print("{0:.3f} {1:.2f} {2}".format(datetime.datetime.utcnow().timestamp(), data[0][0]*1000000000, data))
        else:
            print("{0:.3f} {1} {2}".format(datetime.datetime.utcnow().timestamp(), "N/A", data))
        #time.sleep(0.5)
    else:
        print("Something went wrong (status: {})".format(status))
    #tdc.clear_status()
tse = datetime.datetime.now()
print("Elapsed {} for measurement, ...-600ns between measurements.".format(tse-tss))
tdc.off()
