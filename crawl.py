#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib.request, urllib.error, urllib.parse
import lxml.html, json, time, sys

class Crawl(object):
    def __init__(self,
                 # queries
                 position='linux',
                 city='北京',
                 district='',
                 bizArea='',
                 isSchoolJob='',
                 gx='',
                 xl='',
                 jd='',
                 hy='',
                 
                 # params
                 job_url='https://www.lagou.com/jobs',
                 job_ajax='/positionAjax.json',
                 co_ajax='/companyAjax.json',
                 job_list=[]):
        
        self.position=position
        self.job_url=job_url
        self.job_ajax=job_ajax
        self.co_ajax=co_ajax
        self.job_list=job_list        

        self.query={k:v for k,v in {
            'city':city,
            'district':district,
            'bizArea':bizArea,
            'isSchoolJob':isSchoolJob,
            'gx':gx,
            'xl':xl,
            'jd':jd,
            'hy':hy
        }.items() if v!=''}

        self.form={
            'first':'',
            'pn':'',
            'kd':self.position
        }

        self.referer=self.job_url+'/list_'+urllib.parse.quote(self.position)+'?'
        self.referer+=urllib.parse.urlencode(self.query)
        self.referer+='&cl=false&fromSearch=true&labelWords=&suginput='
        
        self.headers={
            'Host':'www.lagou.com',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Accept':'application/json, text/javascript, */*; q=0.01',
            'Accept-Language':'en-US, en; q=0.5',
            'Accept-Encoding':'gzip, deflate, br',
            'Referer':self.referer,
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With':'XMLHttpRequest',
            'X-Anit-Forge-Token':'None',
            'X-Anit-Forge-Code':'0',
            'Cookie':'JSESSIONID=; _ga=; _gat=; user_trace_token=; LGSID=; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=; LGRID=; LGUID=; index_location_city=; TG-TRACK-CODE=; SEARCH_ID=',
            'Connection':'keep-alive'
        }
        
    def downloader(self, pn):
        ''' post request with spoof header to js-rendered page
        return json object '''
        
        self.form['first']='true' if pn==1 else 'false'
        self.form['pn']=str(pn)

        try:
            url=self.job_url+self.job_ajax+'?'+urllib.parse.urlencode(self.query)+'&needAddtionalResult=false'
            req=urllib.request.Request(url, urllib.parse.urlencode(self.form).encode(), self.headers)

            with urllib.request.urlopen(req) as resp:
                html=resp.read().decode('utf-8')
                json_obj=json.loads(html)
                json_str=json.dumps(json_obj, indent=4)
        except urllib.error.HTTPError as e:
            print(e.code, e.reason)
        except urllib.error.URLError as e:
            print(e.reason)
        except Exception as e:
            print(e)
        else:
            return json_obj

    def parser(self, json, pn):
        ''' parse item of json '''

        if json is None: return
        
        if pn==1:
            location=json['content']['positionResult']['locationInfo']['city']
            queries=json['content']['positionResult']['queryAnalysisInfo']['positionName']
            pagesize=json['content']['pageSize']
            total=json['content']['positionResult']['totalCount']

            self.job_list.append({
                'location':location,
                'queries':queries,
                'current':0,
                'total':total,
                'pagesize':pagesize,
                'pages':total//pagesize+1 if total>pagesize and total%pagesize else total//pagesize
            })
            
        pageno=json['content']['pageNo']
        resultsize=json['content']['positionResult']['resultSize']
        result=json['content']['positionResult']['result']
        
        for i in range(resultsize):
            com_id=result[i]['companyId']
            pos_id=result[i]['positionId']
            time=result[i]['createTime']
            short_time=result[i]['formatCreateTime']
            industry=result[i]['industryField']
            salary=result[i]['salary']
            pos_name=result[i]['positionName']
            workyear=result[i]['workYear']
            education=result[i]['education']
            jobnature=result[i]['jobNature']
            stage=result[i]['financeStage']
            com_size=result[i]['companySize']
            com_short_name=result[i]['companyShortName']
            com_full_name=result[i]['companyFullName']
            first_type=result[i]['firstType']
            second_type=result[i]['secondType']
            district=result[i]['district']
            subway=result[i]['subwayline']
            station=result[i]['stationname']
            link=self.job_url + '/' + str(result[i]['positionId']) + '.html'

            self.job_list.append({
                'pos_name':pos_name,
                'salary':salary,
                'workyear':workyear,
                'industry':industry,
                'com_short_name':com_short_name,
                'com_full_name':com_full_name,
                'com_size':com_size,
                'stage':stage,
                'district':district,
                'subway':subway,
                'station':station,
                'link':link,
                'time':time
            })

            self.job_list[0]['current']=1 if self.job_list[0]['current']==0 else self.job_list[0]['current']+1
            print('\r%s, %d/%d' %(self.position, self.job_list[0]['current'], self.job_list[0]['total']), end='')
            if self.job_list[0]['current']==self.job_list[0]['total']: print('')
            
    def tohtml(self):
        ''' html export '''

        html='''<!DOCTYPE html>
<html><head><style>
html{font-size:100%}body{margin:0;padding:0;font-size:13px;overflow-y:scroll}
h1{font-weight:normal}a{text-decoration:none;color: black}p{display:inline-block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin:0}time{margin-left:20px}
#order{text-align:right;width:25px}#pos{margin-left:10px;width:250px}#ind{margin-left:10px;width:130px}#com{margin-left:10px;width:250px}#addr{margin-left:10px;width:400px}
</style><meta charset="UTF-8"><title>result</title></head><body>
</body></html>'''
    
        searchtime=time.strftime('%H:%M:%S %d %m %Y', time.localtime(time.time()))
        filename='jobs#'+searchtime+'.html'

        with open(filename, 'w') as f:
            f.write(html)
        with open(filename, 'r') as f:
            origin=f.read()
            pos=origin.find('</body>')

        if pos != -1:
            latest=''
            latest+='<h1>'+str(len(self.job_list)-1)+' jobs from lagou.com'+'<time>'+searchtime+'</time>'+'</h1>\n'       

        for i in range(len(self.job_list)):
            if i==0: continue
            
            latest+='<div>\n'
            latest+='<p id=\'order\'>'+str(i)+'</p>\n'
            latest+='<p id=\'pos\'><a href=\'' + self.job_list[i]['link'] + '\'>' + self.job_list[i]['pos_name'] + '/' + self.job_list[i]['salary'] + '</a></p>\n'
            latest+='<p id = \'ind\'></p>\n' if self.job_list[i]['industry']==None else '<p id=\'ind\'>'+self.job_list[i]['industry']+'</p>\n'
            latest+='<p id=\'com\'>'+self.job_list[i]['com_full_name']+'</p>\n'
                
            district='' if self.job_list[i]['district']==None else self.job_list[i]['district']
            subway='' if self.job_list[i]['subway']==None else self.job_list[i]['subway']
            station='' if self.job_list[i]['station']==None else self.job_list[i]['station']
                
            latest+='<p id=\'addr\'>'+district+subway+station+'</p>\n'
            latest+='</div>\n'

        with open(filename, 'w') as f:
            f.write(origin[:pos]+latest+origin[pos:])
            
if __name__=='__main__':
    kwargs={i[:i.find('=')]:i[i.find('=')+1:] for i in sys.argv[1:]}
    c=Crawl(**kwargs)
    json_obj=c.downloader(1)
    if json_obj is not None:
        c.parser(json_obj, 1)

        for i in range(2, c.job_list[0]['pages']+1):
            json_obj=c.downloader(i)
            c.parser(json_obj, i)

        c.tohtml()

    '''
    with open('log', 'w') as f:
    [print(item, file=f) for item in c.job_list[1:]]
    '''
