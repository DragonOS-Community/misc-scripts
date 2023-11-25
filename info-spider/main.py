# -*- coding: UTF-8 -*-
import time

import requests
import json
import xlwt
from os import path
from concurrent.futures import ThreadPoolExecutor

__all__ = ["get_dict", "get_json"]

USER = "DragonOS-Community"  # 目标用户
PATH = ""  # 文件输出路径，为空则默认在脚本文件同一目录下`
TOKEN = "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"  # github访问令牌，用于增加api访问次数
function_list = ["get_cnt", "get_pr", "get_contributors"]  # 信息获取函数

pool = ThreadPoolExecutor(max_workers=16)


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
    contri_dict = get_info(repo_dict["contributors_url"])
    result = {"contributor": []}
    for dic in contri_dict:
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
                for contribute in repo[k]:
                    if contribute_existed.get(contribute["name"]) is None:
                        result["total"][k].append(contribute.copy())
                        contribute_existed[contribute["name"]] = pos
                        pos += 1
                    else:
                        result["total"][k][contribute_existed[contribute["name"]]]["contributions"] += \
                            contribute["contributions"]
    result["total"]["contributor"].sort( key=lambda a: a["contributions"],reverse=True)
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

    thread_list = []
    for dic in root_dict:
        thread_list.append(pool.submit(thread, dic))
        time.sleep(0.05)
    while thread_list:
        for x in thread_list:
            if x.done():
                thread_list.remove(x)
    return info_dict


def get_json():
    """
    :return:带有信息的json文本
    """
    return json.dumps(sum_up(get_dict()), sort_keys=False, indent=4, separators=(',', ':'), ensure_ascii=False)


def wt_json():
    text = get_json()
    if PATH:
        with open(path.join(PATH, "github_info.json"), "w") as f:
            f.write(text)
    else:
        with open("github_info.json", "w",encoding="utf-8") as f:
            f.write(text)


if __name__ == '__main__':
    wt_json()
