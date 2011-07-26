# -*- coding: utf-8 -*-

from datetime import datetime
from django.utils.translation import ugettext as _
from modoboa.lib import tables, db, static_url
from modoboa.lib.email_listing import MBconnector, EmailListing
from modoboa.lib.emailutils import *

class Qtable(tables.Table):
    tableid = "emails"
    idkey = "mailid"

    type = tables.Column("type", align="center", width="30px",
                         label="<input type='checkbox' name='toggleselect' id='toggleselect' />")
    rstatus = tables.ImgColumn("rstatus", width='25px')
    from_ = tables.Column("from", label=_("From"), limit=30)
    subject = tables.Column("subject", label=_("Subject"), limit=40)
    time = tables.Column("date", label=_("Date"))
    to = tables.Column("to", label=_("To"), limit=30)

    cols_order = ['type', 'rstatus', 'to', 'from_', 'subject', 'time']

    def parse_date(self, value):
        return datetime.fromtimestamp(value)

class SQLconnector(MBconnector):
    def __init__(self, filter=None):
        self.conn = db.getconnection("amavis_quarantine")
        self.filter = ""
        if filter:
            for a in filter:
                if not a:
                    continue
                if a[0] == "&":
                    self.filter += " AND "
                else:
                    self.filter += " OR "
                self.filter += a[1:]
        query = self._get_query()
        status, cursor = db.execute(self.conn, """
SELECT count(quarantine.mail_id) AS total
%s
""" % query)
        if not status:
            print cursor
            self.count = 0
        else:
            self.count = int(cursor.fetchone()[0])

    def _get_query(self):
        return """
FROM quarantine, maddr, msgrcpt, msgs
WHERE quarantine.mail_id=msgrcpt.mail_id
AND msgrcpt.rid=maddr.id
AND msgrcpt.mail_id=msgs.mail_id
AND quarantine.chunk_ind=1
%s
ORDER BY msgs.time_num DESC
""" % self.filter

    def messages_count(self, **kwargs):
        return self.count

    def fetch(self, start=None, stop=None, **kwargs):
        query = self._get_query()
        status, cursor = db.execute(self.conn, """
SELECT msgs.from_addr, maddr.email, msgs.subject, msgs.content, quarantine.mail_id,
       msgs.time_num, msgs.content, msgrcpt.rs
%s
LIMIT %d,%d
""" % (query, start - 1, kwargs["nbelems"]))
        if not status:
            print cursor
            return []
        emails = []
        rows = cursor.fetchall()
        for row in rows:
            m = {"from" : row[0], "to" : row[1], 
                 "subject" : row[2], "content" : row[3],
                 "mailid" : row[4], "date" : row[5],
                 "type" : row[6]}
            if row[7] == "R":
                m["img_rstatus"] = static_url("pics/release.png");
            emails.append(m)
        return emails

class SQLlisting(EmailListing):
    tpl = "amavis_quarantine/index.html"
    tbltype = Qtable
    deflocation = "listing/"
    defcallback = "updatelisting"
    reset_wm_url = True

    def __init__(self, user, filter, **kwargs):
        if not user.is_superuser:
            Qtable.cols_order.remove('to')
        self.mbc = SQLconnector(filter)
        EmailListing.__init__(self, **kwargs)

class SQLemail(Email):
    def __init__(self, msg, *args, **kwargs):
        Email.__init__(self, msg, *args, **kwargs)
        fields = ["X-Amavis-Alert", "Subject", "From", "To", "Date"]
        for f in fields:
            label = f
            if not msg.has_key(f):
                f = f.upper()
                if not msg.has_key(f):
                    self.headers += [{"name" : label, "value" : ""}]
                    continue
            self.headers += [{"name" : label, "value" : msg[f]}]
            try:
                label = re.sub("-", "_", label)
                setattr(self, label, msg[f])
            except:
                pass
