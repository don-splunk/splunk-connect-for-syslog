# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

# https://www.ciscolive.com/c/dam/r/ciscolive/us/docs/2017/pdf/TECUCC-3000.pdf

# <189>8103: Oct 14 2015 05:50:19 AM.484 UTC :  %UC_AUDITLOG-5-AdministrativeEvent: %[ UserID =administrator][ ClientAddress =10.110.1.2][ Severity =5][ EventType =GeneralConfigurationUpdate][ ResourceAccessed=CUCMAdmin][ EventStatus =Success][ CompulsoryEvent =No][ AuditCategory =AdministrativeEvent][ ComponentID =Cisco CUCM Administration][ AuditDetails =record in table device, with key field name = SEP0000311107A5 deleted][App ID=Cisco Tomcat][Cluster ID=][Node ID=CUCM11PUB]: Audit Event is generated by this application


def test_cisco_ucm_nohost_auditlog(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist),
                          random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    ucm_time = dt.strftime("%b %d %Y %I:%M:%S %p.%f")[:-3]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}8103: {{ ucm_time }} {{ tzname }} : %UC_AUDITLOG-5-AdministrativeEvent: %[ UserID =administrator][ ClientAddress =192.168.1.1][ Severity =5][ EventType =GeneralConfigurationUpdate][ ResourceAccessed=CUCMAdmin][ EventStatus =Success][ CompulsoryEvent =No][ AuditCategory =AdministrativeEvent][ ComponentID =Cisco CUCM Administration][ AuditDetails =record in table device, with key field name = SEP0000311107A5 deleted][App ID=Cisco Tomcat][Cluster ID=][Node ID={{ host }}]: Audit Event is generated by this application\n")
    message = mt.render(mark="<189>", tzname=tzname, ucm_time=ucm_time, host=host, epoch=epoch)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search _time={{ epoch }} index=main host=\"{{ host }}\" sourcetype=\"cisco:ucm\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


# <189>17: Apr 21 19:01:35.638 UTC : %CCM_RTMT-RTMT-2-RTMT-ERROR-ALERT: RTMT Alert Name:SyslogSeverityMatchFound Detail: At Tue Apr 21 14:01:35 CDT 2009 on node ORD-PUB1, the following SyslogSeverityMatchFound events generated: SeverityMatch - Critical ntpRunningStatus.sh: NTP server 10.12.254.33 is inactive. Verify the network to this server, that it is a NTPv4 server and is operational. SeverityMatch - Alert sshd(pam_unix)[20038]: check pass; user unknown App ID:Cisco AMC Service Cluster ID: Node ID:ord-pub1
def test_cisco_ucm_nohost_rtmt(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist),
                          random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    ucm_time = dt.strftime("%b %d %H:%M:%S.%f")[:-3]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}17: {{ ucm_time }} {{ tzname }} : %UC_AUDITLOG-5-AdministrativeEvent: %[ UserID =administrator][ ClientAddress =10.1.1.1][ Severity =5][ EventType =GeneralConfigurationUpdate][ ResourceAccessed=CUCMAdmin][ EventStatus =Success][ CompulsoryEvent =No][ AuditCategory =AdministrativeEvent][ ComponentID =Cisco CUCM Administration][ AuditDetails =record in table device, with key field name = SEP0000311107A5 deleted][App ID=Cisco Tomcat][Cluster ID=][Node ID={{ host }}]: Audit Event is generated by this application {{ ucm_time }} {{ epoch }}\n")
    message = mt.render(mark="<189>", ucm_time=ucm_time, tzname=tzname, host=host, epoch=epoch)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search _time={{ epoch }} index=main host=\"{{ host }}\" sourcetype=\"cisco:ucm\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <189>23813: cucm-pub: Jul 05 2016 04:03:01 PM.688 UTC : %UC_RTMT-2-RTMT_ALERT: %[AlertName=SyslogSeverityMatchFound][AlertDetail= At Tue Jul 05 12:03:01 EDT 2016 on node 1.2.3.4, the following SyslogSeverityMatchFound events generated: #012SeverityMatch : Critical#012MatchedEvent : Jul 5 12:02:29 cucm-sub1 local7 2 ccm: 6838: cucm-sub1: Jul 05 2016 16:02:29.795 UTC : %UC_CALLMANAGER-2-SignalCongestionEntry: %[Thread=SIP Handler Thread] [AverageDelay=22] [EntryLatency=20] [ExitLatency=8] [SampleSize=10] [TotalSignalCongestionEntry=6752][HighPriorityQueueDepth=0][NormalPriorityQueueDepth=1][LowPriorityQueueDepth=0][AppID=Cisco CallManager][ClusterID=UCMCluster1][NodeID=cucm-sub1]: Unified CM has detected signal congestion in an internal thread and has throttled activities for that thread#012AppID : Cisco Syslog Agent#012Cluster


def test_cisco_ucm_host_auditlog(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist),
                          random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    ucm_time = dt.strftime("%b %d %Y %I:%M:%S %p.%f")[:-3]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}23813: {{ ucm_time }} {{ tzname }} : %UC_AUDITLOG-5-AdministrativeEvent: %[ UserID =administrator][ ClientAddress =192.1.1.1][ Severity =5][ EventType =GeneralConfigurationUpdate][ ResourceAccessed=CUCMAdmin][ EventStatus =Success][ CompulsoryEvent =No][ AuditCategory =AdministrativeEvent][ ComponentID =Cisco CUCM Administration][ AuditDetails =record in table device, with key field name = SEP0000311107A5 deleted][App ID=Cisco Tomcat][Cluster ID=][Node ID={{ host }}]: Audit Event is generated by this application\n")
    message = mt.render(mark="<189>", ucm_time=ucm_time, tzname=tzname, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search _time={{ epoch }} index=main host=\"{{ host }}\" sourcetype=\"cisco:ucm\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#<121>17: Apr 21 19:01:35.638 UTC : %CCM_RTMT-RTMT-2-RTMT-ERROR-ALERT: RTMT Alert Name:SyslogSeverityMatchFound Detail: At Tue Apr 21 14:01:35 CDT 2009 on node ORD-PUB1, the following SyslogSeverityMatchFound events generated: SeverityMatch - Critical ntpRunningStatus.sh: NTP server 10.12.254.33 is inactive. Verify the network to this server, that it is a NTPv4 server and is operational. SeverityMatch - Alert sshd(pam_unix)[20038]: check pass; user unknown App ID:Cisco AMC Service Cluster ID: Node ID:ord-pub1


def test_cisco_ucm_nohost_alert(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist),
                          random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    ucm_time = dt.strftime("%b %d %H:%M:%S.%f")[:-3]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}17: {{ ucm_time }} {{ tzname }} : %CCM_RTMT-RTMT-2-RTMT-ERROR-ALERT: RTMT Alert Name:SyslogSeverityMatchFound Detail: At Tue Apr 21 14:01:35 CDT 2009 on node {{ host }}, the following SyslogSeverityMatchFound events generated: SeverityMatch - Critical ntpRunningStatus.sh: NTP server 10.12.254.33 is inactive. Verify the network to this server, that it is a NTPv4 server and is operational. SeverityMatch - Alert sshd(pam_unix)[20038]: check pass; user unknown App ID:Cisco AMC Service Cluster ID: Node ID:{{host}} {{ ucm_time }} {{ epoch }}\n")
    message = mt.render(mark="<189>", epoch=epoch, ucm_time=ucm_time, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search _time={{ epoch }} index=main host=\"{{ host }}\" sourcetype=\"cisco:ucm\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
