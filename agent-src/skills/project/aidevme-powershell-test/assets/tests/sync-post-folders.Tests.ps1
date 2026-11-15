# Pester 6 tests for scripts\wordpress-scripts\sync-post-folders.ps1, the one script that writes to aidevme.com.
# Every npx call is faked; the write request only ever reaches the fake. The script writes its Bruno reports to
# temp\post-folder-reports in the repo (gitignored), so the tests use post IDs from 900001 up and remove their reports.

BeforeAll {
    . $PSScriptRoot/BrunoFake.ps1
    Block-LiveNpx

    $script:Sut       = Join-Path $PSScriptRoot '..\sync-post-folders.ps1'
    $script:ReportDir = Join-Path (git -C $PSScriptRoot rev-parse --show-toplevel) 'temp\post-folder-reports'

    # A report whose data is one post with its folders, as "Get post folders" and "Set post folders" return it.
    function New-PostReport([int] $Id, [int[]] $Folders, [string] $Modified) {
        $r = ConvertFrom-Json (New-BrunoReport)
        $r[0].results[0].response.data = @{ id = $Id; modified = $Modified; wf_post_folders = $Folders }
        ConvertTo-Json -Depth 20 -InputObject @($r)
    }
}
AfterAll {
    Remove-BrunoFake
    Get-ChildItem $ReportDir -Filter '9000*.json' -ErrorAction SilentlyContinue | Remove-Item
}

Describe 'sync-post-folders.ps1' {
    BeforeEach {
        $posts   = Join-Path $TestDrive 'posts.json'
        $folders = Join-Path $TestDrive 'folders.json'
        ConvertTo-Json -InputObject @(@{ id = 900001; slug = 'demo-post' }, @{ id = 900002; slug = 'other-post' }) | Set-Content $posts
        ConvertTo-Json -InputObject @(
            @{ id = 1; slug = '1-demo-post'; taxonomy = 'wf_post_folders' },
            @{ id = 2; slug = 'demo-post';   taxonomy = 'wf_post_folders' },
            @{ id = 3; slug = 'other-post';  taxonomy = 'wf_page_folders' }) | Set-Content $folders

        # The admin .env doesn't exist in CI: pretend it does, and pass every other Test-Path to the real cmdlet.
        # (A module-qualified Microsoft.PowerShell.Management\Test-Path recurses into the mock; a CommandInfo doesn't.)
        $realTestPath = Get-Command Test-Path -CommandType Cmdlet
        Mock Test-Path { $true } -ParameterFilter { "$Path" -like '*aidevme-wordpress-admin*.env' }
        Mock Test-Path { & $realTestPath @PesterBoundParameters }
        Mock Read-Host { 'yes' }

        $global:CurrentFolders = @(5)
        Use-FakeBruno {
            param($Call)
            $id = [int]$Call.EnvVars.postId
            switch -Wildcard ($Call.Request) {
                '*006-get-post-folders.yml' { New-PostReport $id $global:CurrentFolders 'before' }
                '*001-set-post-folders.yml' { New-PostReport $id ($Call.EnvVars.postFolderIds | ConvertFrom-Json) 'after' }
            }
        }
    }
    AfterEach { Block-LiveNpx }

    It 'adds the numbered folder and keeps the current folders' {
        & $Sut -PostsFile $posts -FoldersFile $folders -Slugs demo-post *>$null
        $set = @($global:BrunoFakeCalls | Where-Object Request -like '*001-set-post-folders.yml')
        $set.Count | Should -Be 1
        $set[0].EnvVars.postFolderIds | Should -Be '[5,1]'
        $set[0].Location | Should -BeLike '*aidevme-wordpress-admin'
    }

    It 'reads with the read-only collection' {
        & $Sut -PostsFile $posts -FoldersFile $folders -Slugs demo-post *>$null
        $read = @($global:BrunoFakeCalls | Where-Object Request -like '*006-get-post-folders.yml')
        $read[0].Location | Should -Not -BeLike '*aidevme-wordpress-admin'
    }

    It 'writes nothing unless the answer is yes' {
        Mock Read-Host { 'y' }
        & $Sut -PostsFile $posts -FoldersFile $folders -Slugs demo-post *>$null
        @($global:BrunoFakeCalls | Where-Object Request -like '*001-set*').Count | Should -Be 0
    }

    It 'does not ask with -Force' {
        & $Sut -PostsFile $posts -FoldersFile $folders -Slugs demo-post -Force *>$null
        Should -Invoke Read-Host -Times 0 -Exactly
        @($global:BrunoFakeCalls | Where-Object Request -like '*001-set*').Count | Should -Be 1
    }

    It 'skips a post that is already in its folder' {
        $global:CurrentFolders = @(1)
        & $Sut -PostsFile $posts -FoldersFile $folders -Slugs demo-post *>$null
        @($global:BrunoFakeCalls | Where-Object Request -like '*001-set*').Count | Should -Be 0
        Should -Invoke Read-Host -Times 0 -Exactly
    }

    It 'ignores folders of other taxonomies' {
        & $Sut -PostsFile $posts -FoldersFile $folders -Slugs other-post *>$null
        $global:BrunoFakeCalls.Count | Should -Be 0
    }

    It 'stops at the first failed write' {
        Use-FakeBruno {
            param($Call)
            if ($Call.Request -like '*006*') { New-PostReport ([int]$Call.EnvVars.postId) @(5) 'before' }
            else { New-BrunoReport -Status 401 }
        }
        { & $Sut -PostsFile $posts -FoldersFile $folders -Slugs demo-post *>$null } | Should -Throw '*HTTP 401*'
    }

    It 'rejects a slug that is not in the posts file' {
        { & $Sut -PostsFile $posts -FoldersFile $folders -Slugs no-such-post *>$null } | Should -Throw '*no-such-post*'
    }
}
