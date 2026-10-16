import sys
import subprocess
import os

def run_cmd(cmd, check=True, capture_output=False):
    """Run a shell command with proper encoding."""
    try:
        res = subprocess.run(
            cmd,
            check=check,
            shell=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=capture_output
        )
        return res
    except subprocess.CalledProcessError as e:
        if check:
            print(f"[错误] 执行命令失败: {cmd}")
            if e.stderr:
                print(e.stderr)
        raise e

def main():
    print("=" * 60)
    print("  钢铁雄心4模组《盐道街之梦》 - 一键 Git Commit & Push 脚本")
    print("=" * 60)

    # 1. 检查是否在 Git 仓库内
    res = run_cmd("git rev-parse --is-inside-work-tree", check=False, capture_output=True)
    if res.returncode != 0:
        print("[错误] 当前目录不是 Git 仓库！")
        sys.exit(1)

    # 2. 检查是否有未提交修改
    status_res = run_cmd("git status --short", check=True, capture_output=True)
    status_output = status_res.stdout.strip()
    if not status_output:
        print("\n[提示] 工作区很干净，没有检测到任何新增或修改的文件。")
        return

    print("\n[当前检测到的改动列表]:")
    print("-" * 50)
    for line in status_output.splitlines():
        print(f"  {line}")
    print("-" * 50)

    # 3. 获取修改内容简介 (命令行参数 或 交互式输入)
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    flags = [arg for arg in sys.argv[1:] if arg.startswith("--")]

    auto_push = "--push" in flags
    no_push = "--no-push" in flags

    if args:
        summary = " ".join(args).strip()
    else:
        try:
            summary = input("\n👉 请输入本次修改的内容简介 (直接回车取消): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n已取消提交。")
            sys.exit(0)

    if not summary:
        print("[提示] 未输入修改简介，已取消提交。")
        sys.exit(0)

    # 4. 执行 git add
    print(f"\n[1/3] 正在暂存文件 (git add -A)...")
    run_cmd("git add -A")

    # 5. 执行 git commit
    print(f"[2/3] 正在创建提交 (git commit)...")
    # 使用参数列表防止引号注入或特殊字符破坏
    subprocess.run(["git", "commit", "-m", summary], check=True, encoding="utf-8", errors="replace")
    print(f"✓ 成功提交: \"{summary}\"")

    # 6. 处理远程推送 (git push)
    remote_res = run_cmd("git remote", check=False, capture_output=True)
    remotes = remote_res.stdout.strip()
    if not remotes:
        print("\n[提示] 未配置远程仓库，跳过推送。")
        return

    should_push = False
    if auto_push:
        should_push = True
    elif no_push:
        should_push = False
    else:
        try:
            push_confirm = input("\n👉 是否推送到远程仓库 GitHub (git push)? [Y/n]: ").strip().lower()
            should_push = (push_confirm == "" or push_confirm in ("y", "yes"))
        except (KeyboardInterrupt, EOFError):
            print("\n跳过推送。")
            should_push = False

    if should_push:
        print("\n[3/3] 正在推送到远程仓库...")
        push_res = run_cmd("git push", check=False)
        if push_res.returncode == 0:
            print("\n✨ 全部完成！修改已成功提交并推送到 GitHub。")
        else:
            print("\n[警告] 推送遇到问题，请检查网络或执行 git push 查看详细日志。")
    else:
        print("\n✨ 本地提交已完成，暂未推送到远程仓库。后续可随时运行 git push 推送。")

if __name__ == "__main__":
    main()
