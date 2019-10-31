import datetime 

class MTALine:
    def __init__(self, line_name):
        self.line_name = line_name
        self.created_at = datetime.datetime.now()
        self.current_status = "not delayed"
        self.last_downtime_update = None
        self.total_downtime = 0.0
        self.percent_uptime = 1.0

    def update_status(self, new_status):
        change = False
        new_status = self._cleanup_status(new_status)
        now = datetime.datetime.now()
        if  new_status != self.current_status:
            change = True
            if new_status == "delayed":
                self.last_downtime_update = now
                print("Line {} is experienceing delays".format(self.line_name))
            else:
                self.total_downtime = self.total_downtime + \
                    (now -  self.last_downtime_start).total_seconds()
                print("Line {} is now recovered".format(self.line_name))
            self.current_status = new_status
        else:
            if new_status == "delayed": # current status is also delayed
                    self.total_downtime = self.total_downtime + \
                        (now -  self.last_downtime_update).total_seconds()
                    self.last_downtime_update = now
        time_since_inception = (now - self.created_at).total_seconds()
        self.percent_uptime = "{:.2f}".format(1 - self.total_downtime/time_since_inception)
        return change
        

    def _cleanup_status(self, status):
        if status.lower() in ["delays", "train delayed"]:
            return "delayed"
        else: 
            return "not delayed"