#!/usr/bin/env python3

import re
import requests
import json
import time
import copy
import threading
from github import Github

class MonitoringPullRequest:
    class PullReqInfo:
        STATE_STR = "state"
        MERGEABLE_STR = "mergeable"
        
        def __init__(self, no, slack_ts):
            self.__no = no
            self.__pr_state = ""
            self.__pr_mergeable = ""
            self.__pr_merged = ""
            self.__pr_closed_at = ""
            self.__issue_comments = []
            self.__slack_ts = slack_ts
            self.__slack_res = []
            self.__not_posted_comments = []
            
        def check_not_posted_comment(self):
            created_ts = [self.__get_created_ts(slack_res) for slack_res in self.__slack_res]
            for issue_comment in self.__issue_comments:
                if issue_comment[0] not in created_ts:
                    self.__not_posted_comments.append(issue_comment)

        def check_pr_status_change(self, status_type):
            ret_val = False
            find_pr_status_comment = False
            for (ts, text) in self.__slack_res:
                m = re.match(r'^(\(Chang\s+Status\)\n)(%s:)(.+)$' % status_type, text)
                if m:
                    find_pr_status_comment = True
                    if m.group(3) != str(self.get_pr_status(status_type)):
                        ret_val = True
                    break
            if find_pr_status_comment == False:
                ret_val = True
            return ret_val

        def append_slack_res(self, slack_res):
            self.__slack_res.append(slack_res)

        def append_issue_comment(self, issue_comment):
            self.__issue_comments.append(issue_comment)
            
        def set_pr_state(self, pr_state):
            self.__pr_state = pr_state

        def set_pr_mergeable(self, pr_mergeable):
            self.__pr_mergeable = pr_mergeable
            
        def set_pr_merged(self, pr_merged):
            self.__pr_merged = pr_merged

        def set_pr_closed_at(self, pr_closed_at):
            self.__pr_closed_at = pr_closed_at

        def get_no(self):
            return self.__no

        def get_slack_ts(self):
            return self.__slack_ts

        def get_pr_status(self, status_type):
            return_pr_status = ""
            if status_type == self.STATE_STR:
                if self.__pr_merged != True:
                    return_pr_status = self.__pr_state
                else:
                    return_pr_status = "merged"
            elif status_type == self.MERGEABLE_STR:
                return_pr_status = self.__pr_mergeable
            return return_pr_status

        def get_issue_comments(self):
            return self.__issue_comments

        def get_not_posted_comments(self):
            return self.__not_posted_comments
        
        def __unificate_line_sep(self, src):
            return "\n".join(src.splitlines())
        
        def __get_created_ts(self, src):
            converted_src = self.__unificate_line_sep(src[1])
            src_elm = converted_src.split("\n")
            created_ts = ""
            last_line = ""
            if len(src_elm) != 0:
                last_line = src_elm[-1]
                m = re.match(r'^(\(Created\s+at:)\s*(.+)\)$', last_line)
                if m:
                    created_ts = m.group(2)
            return created_ts
        
    def __init__(self, github_tkn, slack_tkn, repo_url, slack_channel):
        self.GITHUB_TOKEN = github_tkn
        self.SLACK_TOKEN = slack_tkn
        self.HIST_API_URL = "https://slack.com/api/channels.history"
        self.POST_API_URL = "https://slack.com/api/chat.postMessage"
        self.SLACK_CHANNEL = slack_channel
        self.__git_hub = Github(self.GITHUB_TOKEN)
        self.__repo = self.__git_hub.get_repo(repo_url)
        self.__slack_hist = None
        self.__pull_req_infos = []
    
    def main_loop(self, interval, wait=True):
        base_time = time.time()
        next_time = 0
        while True:
            print(time.time())
            thread = threading.Thread(target=self.__monitor_pr)
            thread.start()
            if wait:
                thread.join()
            next_time = ((base_time - time.time()) % interval) or interval
            time.sleep(next_time)
    
    def __get_slack_hist(self):
        payload = {
            "token": self.SLACK_TOKEN,
            "channel": self.SLACK_CHANNEL
        }
        req = requests.post(url=self.HIST_API_URL, data=payload)
        return json.loads(req.text)
    
    def __monitor_pr(self):
        # get slack history
        self.__slack_hist = self.__get_slack_hist()
        # get pr comment from slack
        # resistor target pr
        self.__get_slack_pr_comment()
        # get responces to target pr comment from slack
        self.__get_slack_thread_comment()
        # get pr info (state, mergeable, issue comments) to target pr from Github
        self.__get_pr_info()
        # check not posted comments to Slack
        for pull_req_info in self.__pull_req_infos:
            pull_req_info.check_not_posted_comment() 
        # post issue comments(not posted) to Slack
        self.__post_issue_comment_to_slack()
        # post pr status(state, mergeable) info(when changed) to Slack
        self.__post_pr_status_info_to_slack(self.PullReqInfo.STATE_STR)
        self.__post_pr_status_info_to_slack(self.PullReqInfo.MERGEABLE_STR)
        # post process
        self.__clear_infos()
    
    def __get_slack_pr_comment(self):
        for message in self.__slack_hist["messages"]:
            text = message["text"]
            ts = message["ts"]
            m = re.match(r'^(PR#)([0-9]+)$', text)
            if m:
                pull_req_info = self.PullReqInfo(m.group(2), ts)
                self.__pull_req_infos.append(pull_req_info)
    
    def __get_slack_thread_comment(self):
        for message in self.__slack_hist["messages"]:
            if "thread_ts" in message:
                text = message["text"]
                res_ts = message["ts"]
                thread_ts = message["thread_ts"]
                # exclude top comment
                m = re.match(r'^(PR#)([0-9]+)$', text)
                if not m:
                    for pull_req_info in self.__pull_req_infos:
                        ts = pull_req_info.get_slack_ts()
                        if thread_ts == ts:
                             pull_req_info.append_slack_res((res_ts, text))
    
    def __get_pr_info(self):                              
        for pull_req_info in self.__pull_req_infos:
            no = pull_req_info.get_no()
            pull_req = self.__repo.get_pull(int(no))
            pull_req_info.set_pr_merged(pull_req.merged)
            pull_req_info.set_pr_closed_at(pull_req.closed_at)
            pull_req_info.set_pr_state(pull_req.state)
            pull_req_info.set_pr_mergeable(pull_req.mergeable)
            for issue_comment in pull_req.get_issue_comments():
                pull_req_info.append_issue_comment((issue_comment.created_at.strftime("%Y%m%d%H%M%S"), issue_comment.body))

    def __post_issue_comment_to_slack(self):        
        for pull_req_info in self.__pull_req_infos:
            slack_ts = pull_req_info.get_slack_ts()
            not_posted_comments = pull_req_info.get_not_posted_comments()
            print()
            for not_posted_comment in not_posted_comments:
                text = "(New Comment)\n%s\n(Created at:%s)" % (not_posted_comment[1], not_posted_comment[0])
                payload = {
                    "token": self.SLACK_TOKEN,
                    "channel": self.SLACK_CHANNEL,
                    "thread_ts": slack_ts,
                    "text": text
                }
                req = requests.post(url=self.POST_API_URL, data=payload)
                
    def __post_pr_status_info_to_slack(self, status_type):   
        for pull_req_info in self.__pull_req_infos:
            slack_ts = pull_req_info.get_slack_ts()
            ret_val = pull_req_info.check_pr_status_change(status_type)
            if ret_val == True:
                pr_status = pull_req_info.get_pr_status(status_type)
                if str(pr_status) != "None":
                    text = "(Chang Status)\n%s:" % status_type
                    text += str(pr_status)
                    payload = {
                        "token": self.SLACK_TOKEN,
                        "channel": self.SLACK_CHANNEL,
                        "thread_ts": slack_ts,
                        "text": text
                    }
                    req = requests.post(url=self.POST_API_URL, data=payload)
                
    def __clear_infos(self):
        self.__pull_req_infos = []
