from datetime import datetime,timezone,timedelta
from email.utils import parsedate_to_datetime

def deadline(meta,gate,now=None):
    now=now or datetime.now(timezone.utc)
    local=7200
    if meta.get('http_status')==429:
        local=min(86400,max(7200,2*gate.get('last_retry_delay_seconds',7200)))
    result=now+timedelta(seconds=local)
    value=meta.get('retry_after')
    if value:
        try:server=now+timedelta(seconds=max(0,int(value)))
        except ValueError:server=parsedate_to_datetime(value)
        result=max(result,server)
    return result.isoformat(),local
