# -*- coding: utf-8 -*-
#改编自huyi@CSDN
"""
Created on Sat Oct 23 13:54:39 2021
@author: huyi
"""

import os,sys,requests,queue,urllib3
import urllib.parse
http = urllib3.PoolManager(num_pools=50)
def check_httpcode(c:int):
    if(c//100!=2):
        raise requests.HTTPError(c)
class Downloader:
    err=queue.Queue()
    _now=0;_all=0
    @property
    def all(self):
        return self._now
    @property
    def now(self):
        return self._now
    def download(self,_url:str):
        upr=urllib.parse.urlparse(_url)
        print(upr)
        if(upr.scheme=="http" or upr.scheme=="https"):
            upr_scheme=upr.scheme
        elif(not upr.scheme):
            upr_scheme="http"
        else:
            raise ValueError("unsupport proto")
        if(upr.netloc):
            upr_netloc=upr.netloc
        else:
            upr_netloc=upr.path
        url=upr_scheme+"://"+upr_netloc
        
        try:
            self._download(url,os.path.basename(url)+".dadl")
            os.rename(os.path.basename(url)+".dadl",os.path.basename(url))
        except Exception as e:
            print(e.__class__.__name__,e)
            self.err.put(str(e))
        
    def _download(self,url, _fp):
        if(not _fp):
            _fp=os.path.basename(url)
        # 重试计数
        count = 0
        # 第一次请求是为了得到文件总大小
        r1 = requests.get(url, stream=True, verify=True)
        check_httpcode(r1.status_code)
        #print(r1.headers)
        #print(r1.status_code)
        try:
            self._all = int(r1.headers['Content-Length'])
        except:
            if(r1.status_code//100==2):
                self._all=0
            else:
                raise
        r1.close()
        # 判断本地文件是否存在，存在则读取文件数据大小
        if os.path.exists(_fp):
            self._now = os.path.getsize(_fp)  # 本地已经下载的文件大小
        else:
            self._now = 0
        while count < 10:
            if count != 0:
                self._now = os.path.getsize(_fp)
            # 文件大小一致，跳出循环
            if self._now >= self._all:
                break
            count += 1
            # 重新请求网址，加入新的请求头的
            # 核心部分，这个是请求下载时，从本地文件已经下载过的后面下载
            headers = {"Range": f"bytes={self._now}-{self._all}"}
            try:
                open(_fp,"ab").close()
            except:
                open(_fp,"w").close()
            with open(_fp, "ab") as f:
                r = requests.get(url, stream=True, verify=True, headers=headers)
                check_httpcode(r1.status_code)
                if count != 1:
                    f.seek(self._now)
                for chunk in r.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        self._now += len(chunk)
                        f.write(chunk)
                        f.flush()
                        '''done = int(50 * self._now / self._all)
                        self._now=self._now
                        self._all=self._all
                        sys.stdout.write("\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * self._now / self._all)+str(r.status_code))
                        sys.stdout.flush()'''
        return _fp
file="mirrors.aliyun.com/index.html"
#file="localhost/share/test.zip"
#file="hTtp://github.org"
try:
    d=Downloader()
    d.download(file)
except Exception as e:
    print(e.__class__.__name__,e)