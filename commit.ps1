[CmdletBinding()]
param (
    [Parameter(Position=0, ValueFromRemainingArguments=$true)]
    [string[]]$Message,
    [switch]$NoPush,
    [switch]$Push
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$pyArgs = @()
if ($Message) {
    $pyArgs += $Message
}
if ($NoPush) {
    $pyArgs += "--no-push"
}
if ($Push) {
    $pyArgs += "--push"
}

python "$PSScriptRoot\commit.py" @pyArgs
