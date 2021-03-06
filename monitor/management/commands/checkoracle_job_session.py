#coding=utf-8
from django.core.management.base import BaseCommand
from monitor.models import oraclelist
from monitor.command.getoracleinfo import *
from monitor.command.sendmail_phone import *
from monitor.command.sendmail_wechat import *
class Command(BaseCommand):
    def handle(self, *args, **options):
        mailcontent=[]
        ip=oraclelist.objects.all().order_by('tnsname')
        for i in ip:
            #print (i.ipaddress)
            if i.monitor_type==1:
                ipaddress=i.ipaddress
                username=i.username
                password=i.password
                port=i.port
                tnsname=i.tnsname
                try:
                    db = cx_Oracle.connect(username+'/'+password+'@'+ipaddress+':'+port+'/'+tnsname ,mode=cx_Oracle.SYSDBA)
                except Exception as  e:
                    content= (i.tnsname+' is Unreachable,The reason is '+str(e)).strip()
                    mailcontent.append(content)
                    #print (mailcontent)
                else:
                    cursor = db.cursor()
                    job=checkjob(cursor)
                    session=checkactivesession(cursor)
                    if tnsname=='hdb':
                        asm=checkasm(cursor)
                        if asm=='error':   
                            asmresult=  'The Size of ASM diskgroup  On  '+i.tnsname +' almost full '
                            mailcontent.append(asmresult)
                    cursor.close()
                    db.close()
                    if job=='error':   
                        jobresult=  'The job have errors on  '+i.tnsname
                        mailcontent.append(jobresult)
                    if session=='error':   
                        sessionresult=  'The Session On  '+i.tnsname +' have long running sessions '
                        mailcontent.append(sessionresult)
        if len(mailcontent) != 0:
            #print ('dda')
            mailcontent='\n'.join(mailcontent)
            send_mail_phone(to_list,'Oracle Job&Session  Status Monitor',mailcontent)
            token=GetToken()
            Send_Message(token,2,'Oracle Job&Session Status Monitor',mailcontent)
