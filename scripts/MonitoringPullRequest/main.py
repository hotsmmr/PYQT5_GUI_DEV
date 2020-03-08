#!/usr/bin/env python3

import MonitoringPullRequest from MonitoringPullRequest

obj = MonitoringPullRequest("GITHUB_TOKEN",
                            "SLACK_TOKEN",
                            "{REPOSITORY}",
                            "SLACK_CHANNEL")
                            
obj.main_loop(1)
