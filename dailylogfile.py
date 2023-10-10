import os
from datetime import datetime, timezone

class DayNumber():

    MJD_START = datetime(2021, 1, 3, 0, 0, 0, 0, tzinfo=timezone.utc)
    gnss_leapsec = 0  # 18 for GPS AS OF 2023

    def __init__(self, gnss_leapsec=0):
        self.gnss_leapsec = gnss_leapsec    

    @staticmethod
    def now(daynumbertype=None, offset_s=0, return_int=True):
        if not daynumbertype:
            return datetime.now(tz=timezone.utc)
        if daynumbertype == 'mjd':
            return DayNumber.mjd(offset_s=offset_s, return_int=return_int)
        elif daynumbertype == 'rnx':
            return DayNumber.rnx(offset_s=offset_s, return_int=return_int)
        elif daynumbertype == 'iso':
            return DayNumber.iso(offset_s=0)
    
    @classmethod
    def mjd(self, utctimestamp=None, offset_s=0, return_int=False):
        # 59217.0 = 2021-01-03 00:00:00 = START
        td = datetime.fromtimestamp(utctimestamp, tz=timezone.utc) if utctimestamp else DayNumber.now()
        td = td - self.MJD_START
        mjd = 59217.0 + td.days + (offset_s + td.seconds+td.microseconds*1.0e-6)/86400.0
        return int(mjd) if return_int else mjd
        
    @staticmethod
    def rnx(utctimestamp=None, offset_s=0, dayofyear_only=False, return_int=False):
        td = datetime.fromtimestamp(utctimestamp, tz=timezone.utc) if utctimestamp else DayNumber.now()
        rnx = td.utctimetuple().tm_yday
        rnx = td.year*1000 + rnx if not dayofyear_only else rnx
        rnx = rnx + td.hour/24 + td.minute/1440 + (offset_s + td.second)/86400 + td.microsecond/86400000000 if not return_int else rnx
        return rnx
    
    @staticmethod
    def iso(utctimestamp=None, offset_s=0):
        td = datetime.fromtimestamp(utctimestamp, tz=timezone.utc) if utctimestamp else DayNumber.now()
        return td.year*10000 + td.month * 100 + td.day
    
class DailyLogFile():
    _f = None
    _daynumber = 0
    _fname = None
    _template = None

    def __init__(self, columns, ftype='general', dir='./', delim='\t', comment_prefix='#', daynumbertype='mjd', offset_s=0, template=None, immediate_flush=False) -> None:
        """ daynumbertype format can be mjd or rnx of iso
            columns is a list of column names used as header
        """

        if (daynumbertype not in ('mjd', 'rnx', 'iso')):
            raise Exception("Daynumbertype must be one of 'mjd', 'rnx' or 'iso'")
        self.ftype = ftype
        self.dir = dir
        self.columns = columns
        self.delim = delim
        self.comment_prefix = comment_prefix
        self.immediate_flush = immediate_flush
        self.offset_s = offset_s        
        self._template = (self.delim.join(['{' + str(i) + '}' for i in range(len(self.columns))]) + '\n') if not template else template
        self.daynumbetype = daynumbertype

    def writeheader(self) -> None:
        if not self._f:
            return
        hdr = self.delim.join(self.columns)
        self._f.write(hdr+'\n')

    @property
    def filename(self) -> str:
        return self._fname

    @property
    def daynumber(self) -> int:
        return self._daynumber

    @daynumber.setter
    def daynumber(self, value: int) -> None:
        if self._daynumber == value:
            return

        if self._f:
            self._f.close()
        self._fname = os.path.join(self.dir, f"{self.ftype}-{value}.txt")
        self._daynumber = value
        if not os.path.exists(self._fname):
            self._f = open(self._fname, 'a')
            self.writeheader()
        else:
            self._f = open(self._fname, 'a')

    def logdata(self, data: list, daynumber=None, use_now=True, immmediate_flush=False) -> None:
        if daynumber:
            self.daynumber = int(daynumber)
        elif use_now:            
            self.daynumber = DayNumber.now(self.daynumbetype, self.offset_s, True)
        if not self._f:
            return
        pddata = pd.Series(data).fillna(pd.NA)
        self._f.write((self._template).format(*pddata))
        if (self.immediate_flush or immmediate_flush):
            self._f.flush()

    def logcomment(self, message, immediate_flush=False) -> None:
        if not self._f:
            return
        self._f.write(f"{self.comment_prefix} {message}\n")
        if (self.immediate_flush or immediate_flush):
            self._f.flush()

    def close(self) -> None:
        if self._f:
            self._f.close()
            self._fname = None

#logfile = DailyLogFile(ftype='csII_Trimble', columns=['TS', 'UTS', 'TI'], daynumbertype='mjd', offset_s=18, immediate_flush=False,
#                       template='{0:.8f}\t{1:.6f}\t{2:.3f}\n')
