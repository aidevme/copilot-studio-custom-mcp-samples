# OpenCollection YAML in Bruno

<!-- cspell:ignore aidevme opencollection usebruno -->

The file formats this skill writes, checked on 2026-10-27 against the Bruno docs (`usebruno/bruno-docs`) and the
Bruno CLI's own test fixtures (`usebruno/bruno`, `packages/bruno-cli/tests/runner/fixtures/opencollection/`). YAML
collections need **Bruno 3.0.0 or later** ("Starting with Bruno 3.0.0, you can save your API request data using
YAML"). The assets collection was parsed and run with Bruno CLI 4.3.0. When Bruno changes a format, check the docs
again rather than trusting this page.

## Layout

```text
aidevme-wordpress/
├── opencollection.yml        # collection root: version, name, collection-level headers
├── .env.example              # names of the process.env variables; .env itself is gitignored
├── environments/
│   └── Production.yml
├── site/
│   ├── folder.yml
│   └── 001-get-api-index.yml
└── posts/
    ├── folder.yml
    └── 001-list-recent-posts.yml
```

A `.bru` collection uses `bruno.json` + `collection.bru` instead; don't mix the two formats in one collection.

## Collection root (`opencollection.yml`)

```yaml
opencollection: "1.0.0"
info:
  name: aidevme-wordpress

extensions:
  bruno:
    defaultEnvironment: Production
    ignore:
      - node_modules
      - .git

request:
  headers:               # sent with every request in the collection
    - name: User-Agent
      value: "Mozilla/5.0 (...) Chrome/126.0 Safari/537.36"
      enabled: true
```

## Folder (`<folder>/folder.yml`)

```yaml
info:
  name: Posts
  type: folder
  seq: 2
```

## Environment (`environments/<Name>.yml`)

```yaml
name: Production
variables:
  - name: baseUrl
    value: https://aidevme.com
    description: Shown in the Bruno app
  - name: wpAppPassword
    value: '{{process.env.AIDEVME_WP_APP_PASSWORD}}'
```

- `--env Production` on the CLI selects it by name.
- `secret: true` marks a value Bruno keeps encrypted and does not write to disk; a `{{process.env.*}}` reference
  is not itself a secret, so it stays a plain variable.
- `process.env`: the **CLI** reads the shell's environment first, then the collection's `.env` file (which
  overrides it); the **app** reads the collection's `.env` file.

## Request (`<folder>/NNN-name.yml`)

```yaml
info:
  name: List recent posts      # sentence case, action first
  type: http
  seq: 1                       # order inside the folder; unique per folder
  tags:
    - smoke                    # bru run --tags smoke / --exclude-tags auth

http:
  method: GET                  # uppercase; this collection allows GET and HEAD only
  url: "{{baseUrl}}/wp-json/wp/v2/posts?per_page=10&_fields=id,slug"
  params:                      # mirror every query parameter of the URL
    - name: per_page
      value: "10"              # quote numbers
      type: query              # query | path
    - name: _fields
      value: id,slug
      type: query
  auth: inherit                # or: type: basic + username/password as {{variables}}

runtime:
  assertions:
    - expression: res.status
      operator: eq             # eq, neq, isString, isNumber, ...
      value: "200"
  scripts:
    - type: after-response     # before-request | after-response | tests
      code: |-
        bru.setVar("postSlug", res.getBody()[0].slug);
    - type: tests
      code: |-
        test("returns an array", function () {
          expect(res.getBody()).to.be.an("array");
        });

settings:
  encodeUrl: true
  timeout: 30000
  followRedirects: true
  maxRedirects: 5

docs: |-
  What it returns, the variables it needs, auth, and the expected result.
```

## Script API used here

| Call | Use |
| --- | --- |
| `res.getStatus()`, `res.getBody()`, `res.getHeader(name)` | Read the response (header names lower-case) |
| `bru.setVar(key, value)` / `bru.getVar(key)` | Runtime variable for later requests in the same run |
| `bru.getEnvVar(key)` | Read an environment variable |
| `test(name, fn)` + `expect(...)` | Chai assertions |

Variable precedence: runtime, request, folder, collection, environment.

## CLI

```bash
npm install -g @usebruno/cli          # or run it with npx @usebruno/cli
cd .bruno/aidevme-wordpress
bru run --env Production --tags smoke                       # quick check
bru run --env Production --exclude-tags auth                # every public read
bru run posts --env Production                              # one folder (-r for subfolders)
bru run --env Production --reporter-html ../../temp/bruno-report.html   # temp/ is gitignored
```

The CLI runs in Safe Mode by default (v3+); this collection needs nothing else.

## Sources

- Bruno docs: [OpenCollection YAML overview](https://docs.usebruno.com/opencollection-yaml/overview),
  [samples](https://docs.usebruno.com/opencollection-yaml/samples),
  [environment variables](https://docs.usebruno.com/variables/environment-variables),
  [DotEnv file](https://docs.usebruno.com/secrets-management/dotenv-file),
  [CLI run](https://docs.usebruno.com/bru-cli/run/overview)
- Bruno CLI source: `packages/bruno-cli/src/commands/run.js` (shell environment merged with the collection's `.env`)
- [bruno-collections/bruno-agent-skills](https://github.com/bruno-collections/bruno-agent-skills): the generic
  collection, test and CI skills this one follows
