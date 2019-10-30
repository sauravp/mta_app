import datetime 

class MTALine:
    def __init__(self, line_name):
        self.line_name = line_name
        self.created_at = datetime.datetime.now()
        self.current_status = "not delayed"
        self.last_downtime_start = None
        self.total_downtime = 0.0

    def update_status(self, new_status):
        new_status = self._cleanup_status(new_status)
        if  new_status != self.current_status:
            if new_status == "delayed":
                self.last_downtime_start = datetime.datetime.now()
                print("Line {} is experienceing delays".format(self.line_name))
            else:
                self.total_downtime = self.total_downtime + \
                    (datetime.datetime.now() -  self.last_downtime_start).total_seconds()
                print("Line {} is now recovered".format(self.line_name))
            self.current_status = new_status
    
    def get_uptime():
        time_since_inception = (datetime.datetime.now() - self.created_at).total_seconds()
        return 1 - self.total_downtime/time_since_inception

    def _cleanup_status(self, status):
        if status.lower() == "delays":
            return "delayed"
        else: 
            return "not delayed"