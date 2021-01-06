import tdc7200
import datetime
import time
import sys
import asyncio
from elasticsearch_async import AsyncElasticsearch

elasticusernamepassword = '...'
es = AsyncElasticsearch(['https://' + elasticusernamepassword + '@rarach.northeurope.cloudapp.azure.com/elastic'])

async def sendrequest(datajson):
    es.index(index="tdc", doc_type="_doc", body=datajson)

def elasticlog(data):
    try:
        align = 1.0/(3.0*2000000)
        tof = data[0][0]
        tofa = None if not tof else (tof if tof < align else tof - 2*align)
        tofa = None if not tof else (tof+align if tof < align else tof)
        res = {
            "@timestamp": datetime.datetime.now(), "tof": tof, "tofa": tofa, "normLBS": data[1], 
            "time1": data[2][0], "cal1": data[4][0], "cal2": data[4][1], "name": sys.argv[1] }
        loop = asyncio.get_event_loop()
        loop.run_until_complete(sendrequest(res))
    except:
        pass

def measure():
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
            elasticlog(data)
            time.sleep(0.7)
        else:
            print("Something went wrong (status: {})".format(status))
        #tdc.clear_status()
    tse = datetime.datetime.now()
    print("Elapsed {} for measurement, ...-600ns between measurements.".format(tse-tss))
    tdc.off()

if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) < 2:
        print("You need to provide measurement name for logging to elastic.")
        exit(1)
    measure()



