# -*- coding: UTF-8 -*-
import time
import requests
import json
from retry import retry
import xlwt
from os import path
from sys import stdout
from concurrent.futures import ThreadPoolExecutor

__all__ = ["get_dict", "get_json"]

function_list = ["get_cnt", "get_pr", "get_contributors"]  # 信息获取函数
PATH = ""  # 文件输出路径以及配置文件存储路径，为空则默认在脚本文件同一目录下`

# TODO 手动配置线程数与线程时间
with open(path.join(PATH, "config.json"), "r", encoding="utf-8") as f:
    # 配置文件选项说明
    dic = json.loads(f.read())
    USER = dic["user"]  # 目标用户
    TOKEN = dic["token"]  # github访问令牌，用于增加api访问次数
    PARALLEL = dic["parallel_threads"]  # 最并行线程数
    BLACKLIST = dic["black_list"]  # contributor获取的仓库黑名单
    WHITELIST = dic["white_list"]  # 仓库黑名单中的contributor白名单

pool = ThreadPoolExecutor(max_workers=PARALLEL)


@retry(Exception, 5, 2, 8)
def get_info(url):
    """
    :param url:请求的api链接
    :return: py字典
    """
    headers = {"Authorization": "Bearer " + TOKEN}
    response = requests.get(url=url, headers=headers).text
    return json.loads(response)


def get_repo(repo_dict):
    """
    :param repo_dict:仓库字典
    :return: py字典
    """
    result = {"name": repo_dict.get("name"), "description": repo_dict.get("description")}
    for fuc in function_list:
        result.update(eval("%s(repo_dict)" % (fuc)))
    return result


def get_cnt(repo_dict):
    result = {
        "starred": repo_dict.get("stargazers_count"),
        "watching": repo_dict.get("watchers_count"),
        "fork": repo_dict.get("forks_count"),
        "issue": repo_dict.get("open_issues_count"),
    }
    return result


def get_pr(repo_dict):
    pr_dict = get_info(r"https://api.github.com/repos/" + repo_dict["full_name"] + "/pulls")
    return {"pull_requests": len(pr_dict)}


def get_contributors(repo_dict):
    result = {"contributor": []}
    contri_dict = get_info(repo_dict["contributors_url"])
    for dic in contri_dict:
        # 黑白名单实现
        if repo_dict["name"] in BLACKLIST or repo_dict.get("parent"):
            if dic["login"] not in WHITELIST:
                continue
        tmp = {
            "name": dic["login"],
            "id": dic["id"],
            "contributions": dic["contributions"]
        }
        result["contributor"].append(tmp)
    return result


def sum_up(dic):
    contribute_existed = {}
    result = {"total": {
        "starred": 0,
        "watching": 0,
        "fork": 0,
        "issue": 0,
        "pull_requests": 0,
        "contributor": []
    }}
    pos = 0
    for repo in dic["repositories"]:
        for k in result["total"].keys():
            if k != "contributor":
                result["total"][k] += repo[k]
            else:
                # contributor累加
                for contribute in repo[k]:
                    if contribute_existed.get(contribute["name"]) is None:
                        result["total"][k].append(contribute.copy())
                        contribute_existed[contribute["name"]] = pos
                        pos += 1
                    else:
                        result["total"][k][contribute_existed[contribute["name"]]]["contributions"] += \
                            contribute["contributions"]
    result["total"]["contributor"].sort(key=lambda a: a["contributions"], reverse=True)
    dic.update(result)
    return dic


def get_dict():
    """
    :return:带有信息的py字典
    """
    # 获取用户信息
    info_dict = {"repositories": []}
    root_dict = get_info(r"https://api.github.com/users/" + USER + r"/repos")

    # 解析信息
    def thread(dic):
        result = get_repo(dic)
        info_dict["repositories"].append(result)
        return 1

    thread_list = []
    wrong_list = []
    for dic in root_dict:
        thread_list.append(pool.submit(thread, dic))
        time.sleep(0.05)
    while thread_list:
        for x in thread_list:
            if x.done() and x.result():
                thread_list.remove(x)
            elif x.done() and not x.result():
                wrong_list.append(x.exception())
                thread_list.remove(x)
            stdout.write('\r %d threads left. . .' % (len(thread_list)))

    # 输入线程完成情况
    stdout.write('\r Done!During the process,%d exceptions have been raised. . . ' % (len(wrong_list)))
    stdout.flush()

    if len(wrong_list):
        for i in wrong_list:
            stdout.write(str(i) + "\n")
            stdout.flush()

    return info_dict


def get_json():
    """
    :return:带有信息的json文本
    """
    return json.dumps(sum_up(get_dict()), sort_keys=False, indent=4, separators=(',', ':'), ensure_ascii=False)


def wt_json():
    text = get_json()
    if PATH:
        with open(path.join(PATH, "github_info.json"), "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
    else:
        with open("github_info.json", "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()


if __name__ == '__main__':
    wt_json()
    # 　TODO　编写xl接口
