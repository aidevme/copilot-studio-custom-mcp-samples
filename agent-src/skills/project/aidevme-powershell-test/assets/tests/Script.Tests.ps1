# Template: Pester 6 tests for one of the get-*.ps1 scripts. Copy it to the tests folder next to the script
# (scripts\wordpress-scripts\tests\<script>.Tests.ps1)
# and change the lines marked CHANGE. As written it tests get-published-posts.ps1.
# Rules: every npx call is faked (BrunoFake.ps1), output goes to $TestDrive (never the default .content path),
# fixtures use demo data only.

BeforeAll {
    . $PSScriptRoot/BrunoFake.ps1
    Block-LiveNpx                                   # any npx call a test didn't fake now fails

    $script:Sut     = Join-Path $PSScriptRoot '..\get-published-posts.ps1'     # CHANGE: the script under test
    $script:Request = 'posts/004-list-all-published-posts.yml'                 # CHANGE: the request it runs

    # CHANGE: one item as the WordPress REST API returns it, demo data only.
    function New-Fixture([int] $Id) {
        @{ id = $Id; date = '2026-01-0{0}T09:00:00' -f $Id; modified = '2026-02-01T09:00:00'; slug = "demo-post-$Id"
           link = "https://example.com/demo-post-$Id/"; title = @{ rendered = "Demo &amp; post $Id" }
           categories = @(1); tags = @(2, 3) }
    }
}
AfterAll { Remove-BrunoFake }

Describe 'get-published-posts.ps1' {                # CHANGE: the script name
    BeforeEach {
        $out = Join-Path $TestDrive 'out.json'
        $global:Report = New-BrunoReport -Data @((New-Fixture 1), (New-Fixture 2))
        Use-FakeBruno { param($Call) $global:Report }
    }
    AfterEach { Block-LiveNpx }

    It 'runs the expected request once' {
        & $Sut -OutFile $out *>$null
        $global:BrunoFakeCalls.Count | Should -Be 1
        $global:BrunoFakeCalls[0].Request | Should -Be $Request
    }

    It 'writes the mapped fields' {                 # CHANGE: the fields the script keeps
        & $Sut -OutFile $out *>$null
        $items = @(Get-Content $out -Raw | ConvertFrom-Json)
        $items.Count | Should -Be 2
        $items[0].title | Should -Be 'Demo & post 1'
        $items[0].PSObject.Properties.Name | Should -Be @('id', 'date', 'modified', 'slug', 'link', 'title', 'categories', 'tags')
    }

    It 'stops when the items span more than one page' {        # CHANGE: drop for scripts that page (media, tags, folders)
        $global:Report = New-BrunoReport -Data @(New-Fixture 1) -Total 150 -TotalPages 2
        { & $Sut -OutFile $out *>$null } | Should -Throw '*on 2 pages*'
    }

    It 'stops when the count does not match X-WP-Total' {
        $global:Report = New-BrunoReport -Data @(New-Fixture 1) -Total 3
        { & $Sut -OutFile $out *>$null } | Should -Throw '*X-WP-Total says 3*'
    }

    It 'reports an HTTP error with its status' {
        $global:Report = New-BrunoReport -Status 406
        { & $Sut -OutFile $out *>$null } | Should -Throw 'HTTP 406*'
    }

    It 'reports a request error' {
        $global:Report = New-BrunoReport -ErrorMessage 'getaddrinfo ENOTFOUND'
        { & $Sut -OutFile $out *>$null } | Should -Throw '*ENOTFOUND*'
    }

    It 'stops when Bruno writes no report' {
        Use-FakeBruno { param($Call) }
        { & $Sut -OutFile $out *>$null } | Should -Throw '*wrote no report*'
    }

    It 'refuses a report with masked values' {
        $global:Report = (New-BrunoReport -Data @(New-Fixture 1)) -replace 'example\.com', '********'
        { & $Sut -OutFile $out *>$null } | Should -Throw '*masked values*'
    }

    It 'restores the AIDEVME_WP_* variables and hides them from Bruno' {
        $env:AIDEVME_WP_USER = 'demo-user'          # a placeholder, never a real value
        try {
            Use-FakeBruno { param($Call) $global:SeenUser = $env:AIDEVME_WP_USER; $global:Report }
            & $Sut -OutFile $out *>$null
            $global:SeenUser | Should -BeNullOrEmpty
            $env:AIDEVME_WP_USER | Should -Be 'demo-user'
        }
        finally { Remove-Item env:AIDEVME_WP_USER -ErrorAction SilentlyContinue; Remove-Variable SeenUser -Scope Global -ErrorAction SilentlyContinue }
    }

    It 'runs Bruno in a scratch copy without .env and removes it afterwards' {
        & $Sut -OutFile $out *>$null
        $work = $global:BrunoFakeCalls[0].Location
        $work | Should -BeLike "$([IO.Path]::GetTempPath().TrimEnd('\'))*aidevme-bruno-*"
        Test-Path $work | Should -BeFalse
    }
}
