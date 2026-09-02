import json,os,re,urllib.parse,urllib.request
from datetime import datetime
KEY=os.environ['OPENDART_API_KEY'];today=datetime.now().strftime('%Y%m%d');rows=[];page=1
while True:
 q=urllib.parse.urlencode({'crtfc_key':KEY,'bgn_de':today,'end_de':today,'page_count':100,'page_no':page,'sort':'date','sort_mth':'desc'})
 with urllib.request.urlopen('https://opendart.fss.or.kr/api/list.json?'+q,timeout=30) as r:data=json.load(r)
 if data.get('status')=='013':break
 if data.get('status')!='000':raise RuntimeError(data.get('message','DART error'))
 rows+=data.get('list',[])
 if page>=int(data.get('total_page',1)):break
 page+=1
rules=[(r'단일판매|공급계약','대규모 수주',32),(r'잠정.*실적|영업실적|손익구조','실적 개선',28),(r'자기주식.*소각|자사주.*소각','주주환원',32),(r'자기주식.*취득|배당','주주환원',22),(r'품목허가|임상시험.*결과|FDA.*승인','허가·임상',30),(r'특허권.*취득','특허',18),(r'신규시설투자|시설투자','설비투자',17)];risks=[(r'정정|기재정정',-12),(r'해지|철회|취소',-35),(r'유상증자|전환사채|신주인수권',-28)]
out=[]
for x in rows:
 if not x.get('stock_code','').strip() or x.get('corp_cls') not in ('Y','K'):continue
 score=35;cat='';matched=False
 for p,label,n in rules:
  if re.search(p,x['report_nm']):score+=n;cat=label;matched=True
 for p,n in risks:
  if re.search(p,x['report_nm']):score+=n
 if matched:out.append({'id':x['rcept_no'],'company':x['corp_name'],'ticker':x['stock_code'].strip(),'market':'KOSPI' if x['corp_cls']=='Y' else 'KOSDAQ','title':x['report_nm'],'category':cat,'score':max(0,min(99,score)),'date':x['rcept_dt'],'url':'https://dart.fss.or.kr/dsaf001/main.do?rcpNo='+x['rcept_no']})
out.sort(key=lambda x:x['score'],reverse=True)
with open('signals.json','w',encoding='utf-8') as f:json.dump({'updated_at':datetime.now().strftime('%m/%d %H:%M'),'signals':out},f,ensure_ascii=False,separators=(',',':'))
