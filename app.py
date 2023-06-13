import json
import  jenkins
import  requests
from collections import OrderedDict
from flask import Flask, jsonify, request


app = Flask(__name__)


@app.route('/',methods=['GET','POST'])
def get_home():
    tx = '请访问路由:“ /job_name/name ”,并将 "name" 的值改为真实存在的jenkins job名称，例：/job_name/ec-cs'
    return  tx

@app.route('/job_name/<name>',methods=['GET','POST'])
def get_job_info(name):
    # 获取请求参数
    # job_name = request.form.get('job_name')           ##post请求
    # job_name = request.args.get('job_name')             ##Get请求
    job_name = name                                     #动态url  name等于job_name
    job_names = get_all_jobname()                       ##所有的 Jenkins job
    if job_name not in job_names:
        return ('您输入的*jenkins job名称有误,请再试一次！')
    else:
    # Jenkins 登录信息
        jenkins_url = 'https://jenkins.tb1.sayweee.net'
        jenkins_token = '11dca30fed5e7febd21fb70f73ab25714a'
        # 构建 Jenkins API 请求 URL
        api_url = f'{jenkins_url}/job/{job_name}/lastBuild/api/json'
        response = requests.get(api_url, auth=('siyuan.cui@sayweee.com', jenkins_token)).text
        data = json.loads(response)
        actions = data.get("actions", [])
        for action in actions:
            if "causes" in action:
                causes = action["causes"]
                for cause in causes:
                    if cause.get("_class") == "hudson.model.Cause$UserIdCause":
                        job_user_id = cause.get("userId")       ##当前job执行人的 email
                        user_name = cause.get("userName")       ##当前job执行人的 name
                        # print(f"userid:{job_user_id},username:{user_name}")
                        job_number = data['number']  ##获取当前的job编号
                        job_result = data['result']  ##获取当前job最近一次执行状态

                        result_dict = OrderedDict([
                            ('user_email', job_user_id),
                            ('job_name', job_name),
                            ('job_number', job_number),
                            ('result', job_result)
                        ])
                        return  jsonify(result_dict)

def get_all_jobname():
    jenkins_url = 'https://jenkins.tb1.sayweee.net'
    jenkins_token = '11dca30fed5e7febd21fb70f73ab25714a'
    username='siyuan.cui@sayweee.com'
    data = jenkins.Jenkins(jenkins_url,username=username,password=jenkins_token)
    all_jobs=data.get_jobs()  ##获取jenkins上所有的job name
    list_1 = [job['name'] for job in all_jobs]
    print(list_1)
    return  list_1





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
