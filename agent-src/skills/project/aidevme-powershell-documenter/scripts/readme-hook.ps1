#Requires -Version 7
# cspell:ignore aidevme

<#
.SYNOPSIS
    Claude Code PostToolUse hook: after a script in scripts\<group>\ is written or edited, asks Claude to update
    that folder's README.md with the aidevme-powershell-documenter skill.

.DESCRIPTION
    Registered in .claude/settings.json for the Write and Edit tools. Reads the hook input (JSON) from stdin and
    looks at tool_input.file_path. When it is a .ps1 file directly in a scripts\<group>\ folder (not in tests\),
    it prints a PostToolUse result whose additionalContext tells Claude to run the skill for that folder. For any
    other file it prints nothing. It never edits a file and always exits 0, so a hook problem never blocks a tool.

.EXAMPLE
    '{"tool_input":{"file_path":"C:\\repo\\scripts\\wordpress-scripts\\get-draft-posts.ps1"}}' |
        pwsh -NoProfile -File .claude/skills/aidevme-powershell-documenter/scripts/readme-hook.ps1
#>

try {
    $hookInput = [Console]::In.ReadToEnd() | ConvertFrom-Json
    $file = "$($hookInput.tool_input.file_path)" -replace '\\', '/'
    if ($file -match '(?i)(^|/)scripts/([^/]+)/([^/]+\.ps1)$') {
        $group = $Matches[2]; $script = $Matches[3]
        $context = "You changed scripts/$group/$script. Before you finish, update scripts/$group/README.md with " +
                   "the aidevme-powershell-documenter skill (workflow: update $script), unless Zsolt asked you not to " +
                   "or this edit is part of a larger change you'll document once at the end."
        [ordered]@{
            hookSpecificOutput = [ordered]@{ hookEventName = 'PostToolUse'; additionalContext = $context }
        } | ConvertTo-Json -Compress
    }
}
catch { }
exit 0
