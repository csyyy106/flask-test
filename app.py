import json
import jenkins
import requests
import logging
from collections import OrderedDict
from flask import Flask, jsonify, request

# 配置日志
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为 INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # 日志格式
    handlers=[
        logging.FileHandler('app.log'),  # 将日志输出到文件
        logging.StreamHandler()  # 将日志输出到控制台
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def get_home():
    logger.info("访问了根路由 '/'")
    tx = '请访问路由:“ /job_name/name ”,并将 "name" 的值改为真实存在的jenkins job名称，例：/job_name/ec-cs'
    return tx


@app.route('/job_name/<name>', methods=['GET', 'POST'])
def get_job_info(name):
    logger.info(f"访问了路由 '/job_name/{name}'")
    job_name = name
    logger.info(f"请求的 Jenkins Job 名称: {job_name}")

    # 获取所有 Jenkins Job 名称
    job_names = get_all_jobname()
    logger.info(f"所有 Jenkins Job 名称: {job_names}")

    if job_name not in job_names:
        logger.error(f"输入的 Jenkins Job 名称有误: {job_name}")
        return '您输入的*jenkins job名称有误,请再试一次！'
    else:
        # Jenkins 登录信息
        jenkins_url = 'https://jenkins.tb1.sayweee.net'
        jenkins_token = '11dca30fed5e7febd21fb70f73ab25714a'
        logger.info(f"Jenkins URL: {jenkins_url}")

        # 构建 Jenkins API 请求 URL
        api_url = f'{jenkins_url}/job/{job_name}/lastBuild/api/json'
        logger.info(f"Jenkins API 请求 URL: {api_url}")

        try:
            # 发送请求
            response = requests.get(api_url, auth=('siyuan.cui@sayweee.com', jenkins_token))
            response.raise_for_status()  # 检查请求是否成功
            logger.info("Jenkins API 请求成功")
        except requests.exceptions.RequestException as e:
            logger.error(f"Jenkins API 请求失败: {e}")
            return jsonify({"error": "无法连接到 Jenkins 服务器"}), 500

        # 解析响应数据
        data = json.loads(response.text)
        logger.info(f"Jenkins API 响应数据: {data}")

        actions = data.get("actions", [])
        for action in actions:
            if "causes" in action:
                causes = action["causes"]
                for cause in causes:
                    if cause.get("_class") == "hudson.model.Cause$UserIdCause":
                        job_user_id = cause.get("userId")  # 当前 Job 执行人的 email
                        user_name = cause.get("userName")  # 当前 Job 执行人的 name
                        job_number = data['number']  # 当前的 Job 编号
                        job_result = data['result']  # 当前 Job 最近一次执行状态
                        logger.info(f"Job 执行人: {user_name} ({job_user_id})")
                        logger.info(f"Job 编号: {job_number}")
                        logger.info(f"Job 状态: {job_result}")

                        result_dict = OrderedDict([
                            ('user_email', job_user_id),
                            ('job_name', job_name),
                            ('job_number', job_number),
                            ('result', job_result)
                        ])
                        return jsonify(result_dict)

        logger.warning(f"未找到 Job {job_name} 的执行人信息")
        return jsonify({"error": "未找到 Job 的执行人信息"}), 404


def get_all_jobname():
    logger.info("获取所有 Jenkins Job 名称")
    jenkins_url = 'https://jenkins.tb1.sayweee.net'
    jenkins_token = '11dca30fed5e7febd21fb70f73ab25714a'
    username = 'siyuan.cui@sayweee.com'
    logger.info(f"Jenkins URL: {jenkins_url}")

    try:
        # 连接到 Jenkins
        server = jenkins.Jenkins(jenkins_url, username=username, password=jenkins_token)
        all_jobs = server.get_jobs()  # 获取所有 Job
        logger.info("成功获取所有 Jenkins Job 名称")
    except jenkins.JenkinsException as e:
        logger.error(f"连接到 Jenkins 失败: {e}")
        return []

    # 提取 Job 名称
    job_names = [job['name'] for job in all_jobs]
    logger.info(f"所有 Jenkins Job 名称: {job_names}")
    return job_names


if __name__ == '__main__':
    logger.info("启动 Flask 应用")
    app.run(host='0.0.0.0', port=5000)
