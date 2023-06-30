"""
author: Yong_z
妈蛋,真折磨人
"""
import time

from github import Github
from github import GithubException
import os

# heyong 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
# XIII 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
# 你的 Github Personal Access Token
access_token = "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"
# 实例化 Github 对象
try:
    g = Github(access_token)
    repo = g.get_user().get_repo('ManifestAutoUpdate')  # 输入 Repo 的名称
except GithubException as e:
    print(f"Github Exception: {e}")
    if e.status == 403:
        # 这里是处理「被禁止访问」的逻辑
        print("api 调用次数限制！休息1小时")
        time.sleep(3600)
else:
    print(f"Connected to Github as {g.get_user().login}")
    # 获取远程仓库的所有分支
    remote_branches = [b.name for b in repo.get_branches()]
    # 获取当前目录的所有文件夹名
    folders = [folder for folder in os.listdir('.') if os.path.isdir(folder) and not folder.startswith('.')]
    path = ''
    # 将每个文件夹对应生成分支并将文件夹内的文件 push 到相应的分支中
    for folder in folders:
        if folder not in remote_branches:  # 判断分支是否存在
            # 生成分支
            repo.create_git_ref('refs/heads/' + folder, repo.get_branch('main').commit.sha)
            # 将文件夹内的所有文件 push 到分支中
            for root, dirs, files in os.walk(folder):
                for filename in files:
                    if not filename.startswith("."):
                        with open(os.path.join(root, filename), 'rb') as file:
                            try:
                                repo.create_file(os.path.join(filename), 'commit message', file.read(),
                                                 branch='refs/heads/' + folder)
                                print(
                                    f"File {filename} in folder {folder} pushed to {folder} branch created successfully!")
                            except GithubException as e:
                                print(f"Something went wrong while pushing file {filename} to {folder} branch: {e}")
                                if e.status == 403:
                                    # 这里是处理「被禁止访问」的逻辑
                                    print("api 调用次数限制！休息1小时")
                                    time.sleep(3600)
                            if filename not in ["config.vdf","LICENSE"]:
                                try:
                                    # 生成tags
                                    tags_name = filename[:filename.index(".")]
                                    tags_ref = f'refs/tags/{tags_name}'
                                    sha = repo.get_branch(folder).commit.sha
                                    repo.create_git_ref(ref=tags_ref, sha=sha)
                                    print(
                                        f"tag {tags_name} created successfully!")
                                except GithubException as e:
                                    print(f"tag {tags_name} created error {e}")
                                    if e.status == 403:
                                        # 这里是处理「被禁止访问」的逻辑
                                        print("api 调用次数限制！休息1小时")
                                        time.sleep(3600)

        if folder in remote_branches:  # 判断分支是否存在
            # 获取当前远程分支的所有文件
            remote_files = [f.path for f in repo.get_contents('', ref=f'refs/heads/{folder}')]
            # 删除当前远程分支中的config.vdf文件
            # if "config.vdf" in remote_files:
            #     try:
            #         # 获取要删除文件的SHA值
            #         sha = repo.get_contents('config.vdf', ref=folder).sha
            #         repo.delete_file('config.vdf', 'Deleting config.vdf', sha, branch=folder)
            #         remote_files.remove("config.vdf")
            #         print(f"Deleted config.vdf from {folder} branch")
            #     except GithubException as e:
            #         print(f"Failed to delete config.vdf from {folder} branch: {e}")
            for root, dirs, local_files in os.walk(folder):
                for filename in local_files:
                    if not filename.startswith("."):
                        if filename in remote_files:
                            # 删除文件
                            try:
                                # 获取要删除文件的SHA值
                                sha = repo.get_contents(filename, ref=folder).sha
                                repo.delete_file(filename, f'Deleting {filename}', sha, branch=folder)
                                remote_files.remove(filename)
                                print(f"Deleted {filename} from {folder} branch")
                            except GithubException as e:
                                print(f"Failed to delete {filename} from {folder} branch: {e}")
                            if filename not in ["config","LICENSE"]:
                                # 删除tags
                                try:
                                    tags_name = filename[:filename.index(".")]
                                    if tags_name != "config":
                                        tag = repo.get_git_ref(f"tags/{tags_name}")
                                        tag.delete()
                                        print(f"Deleted tag: {tags_name}")
                                except GithubException as e:
                                    print(f"Failed to delete tag {tags_name}: {e}")
                print("文件及tags删除完成,程序休眠10S")
                time.sleep(10)
                for filename in local_files:
                    if not filename.startswith("."):
                        if filename not in remote_files:
                            with open(os.path.join(root, filename), 'rb') as file:
                                try:
                                    repo.create_file(os.path.join(filename), 'commit message', file.read(),
                                                     branch=f'refs/heads/{folder}')
                                    print(
                                        f"File {filename} in folder {folder} pushed to {folder} branch created successfully!")
                                except GithubException as e:
                                    print(
                                        f"Something went wrong while pushing file {filename} to {folder} branch: {e}")
                                    if e.status == 403:
                                        # 这里是处理「被禁止访问」的逻辑
                                        print("API调用次数限制！休息1小时")
                                        time.sleep(3600)
                                if filename not in ["config.vdf","LICENSE"]:
                                    # 生成tags
                                    try:
                                        tags_name = filename[:filename.index(".")]
                                        tags_ref = f'refs/tags/{tags_name}'
                                        sha = repo.get_branch(folder).commit.sha
                                        repo.create_git_ref(ref=tags_ref, sha=sha)
                                        print(
                                            f"分支存在创建 tag {tags_name} created successfully!")
                                    except GithubException as e:
                                        print(f"tag {tags_name} created error {e}")
                                        if e.status == 403:
                                            # 这里是处理「被禁止访问」的逻辑
                                            print("API调用次数限制！休息1小时")
                                            time.sleep(3600)
