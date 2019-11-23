import re, json, requests
from pyencrypt import rsa_encrypt
from bs4 import BeautifulSoup


class Spider:

    loginjs_url = 'https://css.zhiyuanyun.com/common/login.js'
    loginpg_url = 'https://www.bv2008.cn/app/user/login.php'
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }

    def __init__(self):
        self.cookies = requests.cookies.RequestsCookieJar()
        self.sess = requests.Session()
        self.api = {}
        self.refresh()

    def refresh(self):
        res = self.sess.get(Spider.loginpg_url)
        self.sess.cookies.update(res.cookies)
        soup = BeautifulSoup(res.text, 'lxml')
        self.seid = soup.find('input', {'id': 'seid'})['value']

    def get_crsf_token(self, url):
        resp = self.sess.get(url)
        soup = BeautifulSoup(resp.text, 'lxml')
        tag = soup.find('meta', {'name': 'csrf-token'})
        return tag['content']
    
    def update_header(self, url):
        token = self.get_crsf_token('https://www.bv2008.cn/app/opp/opp.my.php')
        Spider.headers.update({'x-csrf-token': token})

    def _get_pub_key(self):
        res = self.sess.get(Spider.loginjs_url)
        pubkey = ''.join(re.findall(r"pubkey\s*\+?\='(.*)'", res.text)[1:-1])
        return pubkey

    def _get_upass(self, password):
        pubkey = self._get_pub_key()
        upass = rsa_encrypt(password, pubkey)
        return upass

    def login_bv(self, username, password):
        res = self.sess.post(
            Spider.loginpg_url + '?m=login',
            data={
                'seid': self.seid,
                'uname': username,
                'upass': self._get_upass(password),
                'referer': 'https://www.bv2008.cn/'
            },
            headers=Spider.headers)
        return json.loads(re.match(r'.*(\{.*\}).*', res.text).groups()[0])

    def register(self, name):
        def wrapper(func):
            def inner_wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            self.api[name] = inner_wrapper

        return wrapper

def register(spider):

    # 获取项目和岗位
    @spider.register('get_projects')
    def get_projects():
        resp = spider.sess.get('https://www.bv2008.cn/app/opp/opp.my.php')
        soup = BeautifulSoup(resp.text, 'lxml')
        acts = []
        for activity in soup.find_all(
                'a', {
                    'href':
                    re.compile(
                        r'(view\.opp\.php\?id\=[0-9]+)|(item=hour&job_id\=[0-9]+)')
                }):
            match_act = re.match(r'.*view\.opp\.php\?id\=([0-9]+).*',
                                str(activity))
            match_job = re.match(r'.*job_id\=([0-9]+).*', str(activity))
            if match_act:
                acts.append({
                    'id': match_act.groups()[0],
                    'name': activity.string,
                    'jobs': []
                })
            elif match_job:
                i = 10
                p = activity.parent
                while i > 0:
                    p = p.previous_sibling
                    i -= 1
                acts[-1]['jobs'].append({
                    'id': match_job.groups()[0],
                    'name': p.string
                })
        return acts

    @spider.register('generate_code')
    def generate_code(opp_id, job_id, count, time, memo):
        '''
        opp_id: str -> 活动id
        job_id: str -> 岗位id
        count: int -> 时长码个数
        time: float -> 时长
        memo: str -> 备注
        '''
        page_url = 'https://www.bv2008.cn/app/opp/opp.my.php?item=hour&job_id=' + job_id + '&opp_id=' + opp_id + '&manage_type=0'
        spider.update_header(page_url)
        resp = spider.sess.post(
            page_url + '&m=save_hour_code',
            data={
                'job_id': job_id,
                'hc_total': count,
                'hc_hour': time,
                'memo': memo,
                'uid': ''
            },
            headers=Spider.headers)
        return json.loads(re.match(r'.*(\{.*\}).*', resp.text).groups()[0])

    @spider.register('get_code_list')
    def get_code_list(opp_id, job_id):
        page_url = 'https://www.bv2008.cn/app/opp/opp.my.php?item=hour&job_id=' + job_id + '&opp_id=' + opp_id + '&type=checko&manage_type=0'
        resp = spider.sess.get(page_url)
        soup = BeautifulSoup(resp.text, 'lxml')
        codes = []
        i = 0
        loop = 6
        code = {}
        user = {}
        for tag in soup.find('table', {'class': 'table1'}).find_all('td'):
            if i % loop == 0:
                code = {}
                use = {}
            string = str(tag.string).replace(' ', '').replace('\r', '').replace('\n', '').replace('\t', '')
            if i == 0:
                code['code'] = string
            elif i == 1:
                code['time'] = string
            elif i == 2:
                code['date'] = string
            elif i == 3:
                a = tag.find('a')
                if a is not None:
                    name = a.string
                    uid = re.match(r'.*uid=([0-9]+).*', a['href']).groups()[0]
                    use['user'] = {"uid": uid, "name": name}
                else:
                    use['user'] = {}
            elif i == 4:
                use['date'] = string
            i += 1
            if i % loop == 0:
                code['use'] = use
                codes.append(code)
            i %= loop
        return codes


    @spider.register('use_code')
    def use_code(code):
        spider.update_header('https://www.bv2008.cn/app/opp/opp.my.php')
        resp = spider.sess.post(
            'https://www.bv2008.cn/app/opp/opp.my.php?m=save_hour_code',
            data={
                'hour_code': code
            },
            headers=Spider.headers
        )
        return json.loads(re.match(r'.*(\{.*\}).*', resp.text).groups()[0])
